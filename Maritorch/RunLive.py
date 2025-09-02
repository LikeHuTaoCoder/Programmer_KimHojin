import torch
import socket
import random
import traceback
import DisplayNetwork
from Config import get_model, get_data, get_checkpoint_dir
import os

PORT = 2222
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

data_info = get_data(training=False)

model = get_model(data_info).to(device)
model.load_state_dict(torch.load(os.path.join(get_checkpoint_dir(), "mario_best.pt"), map_location=device))
model.eval()

hidden = None
prev_buttons = [-1.0] * data_info.output_size if data_info.recur_buttons else [] # 재귀 버튼 사용 시 -1로 초기화
print("Previous buttons initialized:", prev_buttons)
# 서버 소켓 생성 및 바인딩
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# IPv4, SOCK_STREAM=순차적인 데이터 전달
server.bind((socket.gethostname(), PORT)) #장치 이름과 포트번호
server.listen(1) #연결은 하나만
server.settimeout(1.0)

print(f"Hostname: {socket.gethostname()}, Port: {PORT}")

print(f"Waiting for connection on port {PORT}...")
try:
    while True:
        # 클라이언트 연결 대기
        try:
            clientsocket, address = server.accept()
            print(f"Connected from {address}")
        except socket.timeout:
            continue

        display = DisplayNetwork.Display(data_info.input_width, data_info.input_height) #pygame 화면 생성

        try:
            # 클라이언트로부터 데이터 수신
            clientsocket.send((str(len(data_info.header)) + "\n").encode()) #헤더의 길이 전송
            for param in data_info.header:
                clientsocket.send((str(param) + "\n").encode()) 

            # 클라이언트와의 통신 루프
            while True:
                screen = ""
                
                while not screen.endswith("\n"):
                    chunk = clientsocket.recv(2048).decode('ascii') # 클라이언트로부터 데이터 수신 2048바이트씩
                    if not chunk: # 클라이언트가 연결을 종료한 경우 chunk는 빈 문자열
                        raise Exception("Connection closed by client.") #의도적으로 오류 발생 except로 넘어감
                    screen += chunk

                screen = screen.strip() # 양쪽 공백 제거
                words = screen.split(" ") # 공백으로 나누기

                expected_size = data_info.input_size # 입력 크기 

                if data_info.recur_buttons: # 재귀 버튼 사용 시
                    expected_size -= data_info.output_size # 버튼 크기만큼 줄임 버튼을 두 번 더했기 때문
                
                if len(words) != expected_size: # 입력 크기와 수신된 데이터 크기가 다르면
                    print("Invalid input size. Closing client.")
                    clientsocket.close() # 클라이언트 연결 종료
                    break

                single_input = [float(v) for v in words] + prev_buttons 
                x = torch.tensor(single_input, dtype=torch.float32).view(1, 1, -1).to(device) # 텐서로 변환

                prediction, hidden = model.predict(x, hidden) # 예측결과 및 hidden state 업데이트
                probs = prediction[0][0].cpu().tolist() # 예측 결과를 CPU로 이동 후 리스트로 변환
                
                # probs는 모델의 예측 결과로, 각 버튼에 대한 확률을 나타냄(0.0 ~ 1.0)
                # 버튼값을 0 또는 1로 변환
                buttons = []
                for p in probs:
                    if random.random() < p: # 확률에 따라 버튼값 결정 0.9면 90% 확률로 1
                        buttons.append("1")
                    else:
                        buttons.append("0")
                
                # 재귀 버튼 사용 시 이전 버튼값 업데이트
                if data_info.recur_buttons:
                    prev_buttons = [float(b) for b in buttons]

                # 클라이언트에게 예측 결과 전송
                clientsocket.send((" ".join(buttons) + "\n").encode())

                # 표시용 hidden state 생성
                # hidden state는 모델의 내부 상태로, 모델이 이전 입력을 기억하는 데 사용됨
                fake_tf_state = [
                    type("FakeState", (), {
                        "h": layer_h[0].detach().cpu().flatten().tolist(),
                        "c": layer_c[0].detach().cpu().flatten().tolist()
                    })
                    for (layer_h, layer_c) in hidden  # hidden은 리스트 of 튜플
                ]

                #기존에 pygame에서는 tensorflow모델의 hidden state를 사용했지만
                #여기서는 torch모델의 hidden state를 사용하기 위해서 fake_tf_state를 만들어서 사용
                display.update(x.view(-1).cpu().tolist(), fake_tf_state, probs)
                #display.update(x.view(-1).cpu().tolist(), hidden, probs)

        except Exception as e:
            print("❌ Exception occurred:")
            traceback.print_exc() # 오류 발생 시 스택 트레이스 출력
            clientsocket.send(b"close")
            clientsocket.close()
        finally:
            display.close() # pygame 종료
            print(f"Waiting for connection on port {PORT}...")# 클라이언트 연결 종료 후 새 연결 대기
except KeyboardInterrupt:
    print("Server shutting down.")
finally:
    server.close()