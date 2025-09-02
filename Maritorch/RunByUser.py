import socket
import traceback
import DisplayNetwork
from Config import get_data
import os
import keyboard
import datetime

PORT = 2222
# ButtonNames 순서에 맞춰 키 매핑
KEY_MAP = {
    'x': 0,    # A
    'z': 1,    # B
    's': 2,    # X
    'a': 3,    # Y
    'up': 4,   # Up
    'down': 5, # Down
    'left': 6, # Left
    'right': 7 # Right
}
OUTPUT_SIZE = 8
SAVE_PATH = "recordings"
os.makedirs(SAVE_PATH, exist_ok=True)
now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
file = open(os.path.join(SAVE_PATH, f"ManualSession_{now}.txt"), "w")

data_info = get_data(training=False)
file.write(' '.join(data_info.header) + "\n")
file.write("Session 1\n")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((socket.gethostname(), PORT))
server.listen(1)
server.settimeout(1.0)

print(f"Hostname: {socket.gethostname()}, Port: {PORT}")
print(f"Waiting for connection on port {PORT}...")

try:
    while True:
        try:
            clientsocket, address = server.accept()
            print(f"Connected from {address}")
        except socket.timeout:
            continue

        display = DisplayNetwork.Display(data_info.input_width, data_info.input_height)

        try:
            clientsocket.send((str(len(data_info.header)) + "\n").encode())
            for param in data_info.header:
                clientsocket.send((str(param) + "\n").encode())

            while True:
                screen = ""
                while not screen.endswith("\n"):
                    chunk = clientsocket.recv(2048).decode('ascii')
                    if not chunk:
                        raise Exception("Connection closed by client.")
                    screen += chunk

                screen = screen.strip()
                if screen == "close":
                    print("Client requested close.")
                    break

                words = screen.split()
                if len(words) != data_info.input_size:
                    print(f"⚠️ Input size mismatch: expected {data_info.input_size}, got {len(words)}")
                    continue

                # 화면 15x15 (225개)
                screen_size = data_info.input_width * data_info.input_height
                screen_data = words[:screen_size]
                for i in range(0, screen_size, data_info.input_width):
                    file.write(' '.join(screen_data[i:i + data_info.input_width]) + "\n")

                # extra input 20개 + 3개로 분할 저장
                extra_data = words[screen_size:]
                file.write(' '.join(extra_data[:20]) + "\n")
                file.write(' '.join(extra_data[20:]) + "\n")

                # 버튼 입력 감지
                buttons = ['0'] * OUTPUT_SIZE
                for key, idx in KEY_MAP.items():
                    if keyboard.is_pressed(key):
                        buttons[idx] = '1'

                file.write(' '.join(buttons) + "\n")

                # pygame 시각화
                display.update([float(x) for x in words], None, [float(x) for x in buttons])

                # 버튼 전송
                clientsocket.send((' '.join(buttons) + "\n").encode())

        except Exception as e:
            print("❌ Exception occurred:")
            traceback.print_exc()
            try:
                clientsocket.send(b"close")
            except:
                pass
            clientsocket.close()
        finally:
            display.close()
            print(f"Waiting for connection on port {PORT}...")

except KeyboardInterrupt:
    print("Server shutting down.")
finally:
    file.close()
    server.close()
    print("Terminal state restored.")
