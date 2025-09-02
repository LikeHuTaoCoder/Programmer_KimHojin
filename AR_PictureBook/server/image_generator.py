from openai import OpenAI
import os
import tempfile
import base64

client = OpenAI(api_key = os.environ["OPENAI_API_KEY"])

def dall_e_generater(user_speech:str):
    print("dall_e_generater()")
    print(user_speech)
    prefix = "동화책 스타일로 그려진 귀여운 일러스트, seed=696098030"

    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"{user_speech}, {prefix}",
        size="1024x1024",
        quality="low",
        n=1,
    )
    return response.data[0].b64_json 

def chatgpt_wisper_stt(wav_b64:str):
    try:
        # base64 디코딩
        audio_bytes = base64.b64decode(wav_b64)

        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        # OpenAI Whisper API 호출
        
        with open(temp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="json"
        )
        # 임시 파일 삭제
        os.remove(temp_path)
        return transcript.text

    except Exception as e:
        print(f"Error: {e}")
        return "Failed to process audio."