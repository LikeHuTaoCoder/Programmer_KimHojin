#gpt를 이용해 문장을 생성하는 코드
import openai
import os
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def make_sentence(subject,verb) -> str:
    from openai import OpenAI
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that converts words into sentences. Make sure to respond in Korean. The output should be creative and engaging.",
            },
            {
                "role": "user",
                "content": f"{subject}, {verb}",
            },
        ],
        max_tokens=50,
        temperature=0.7,
    )
    print(response.choices[0].message.content.strip())
    sentence = response.choices[0].message.content.strip()
    return sentence
    