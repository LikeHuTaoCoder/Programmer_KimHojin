import getpass, os

from langchain_openai import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough,RunnableSequence
from langchain.chains import LLMChain
#from langchain.globals import set_llm_cache, set_debug
 
import base64

def caption_init():
    print("caption_init()")

    # OpenAI API key 설정
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(
                model="gpt-4o",
                temperature=0.5 # llm의 창의력(?) 정도, 높을 수록 대답이 자유분방해짐
                #streaming=True # 한 글자씩 출력하게 함 -> 반응성 향상
            )
    memory = ConversationSummaryBufferMemory(
            llm = model,
            max_token_limit=20,
            return_messages=True,
            input_key="user_input",
        )
    inital_prompt = (
    """
        1. You are an agent specialized in tagging image of character's information and behavior.
        2. You will be provided with a base64-encoded image, and you have to extract keywords about character in image.
        3. If there are multiple characters in the image, you should extract information of biggest character only.
        4. Keywords should be concise and in lower case. 
        5. Keywords can be chosen in this list:
            {{ "character" : ["man", "woman", "boy", "girl", "cat", "dog", "bear", "elephant", "sheep", "zebra", "giraffe"], "status" : ["idle", "jump", "walk", "eat", "run"], "direction" : ["left", "right"], "color" : ["red", "yellow", "blue", ...] }}
        6. Except color, you must choose one keyword for each item.
        7. "direction" is the direction of character's face. If character is facing to left, then "direction" : "left".
        8. "color" should be chosen from the most dominant color in the image. And return values in hex color code.
        9. When "character" is a human, "color" have multiple values, top and bottom. 
        10. Pick the most dominant color in the image for each item.
        11. For example, if character is wearing red top and green bottom, then "color" : ["#ba1c16", "#27c250"]
        12. This is examples of valid return values:
        {{ 
            "character" : "man",
            "status" : "walk",
            "direction" : "right",
            "color" : ["#ba1c16", "#27c250"]
        }},
        {{
            "character" : "cow",
            "status" : "run",
            "direction" : "left",
            "color" : ["#ba1c16"]
        }}
        13. When there is an error, such as an image not detected, just return like this:
        {{
            "character" : "null"
        }}
        14. Now, let's start the task! Please extract keywords from the image.
    """
                    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", [
                inital_prompt
                ]),
            ("human", [
                {
                    "type" : "text",
                    "text" : "{user_input}"
                },
                {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,{image_b64}"},
                    }
            ]),
        ],
    )

    chain = LLMChain(
        llm=model,
        prompt=prompt,
        verbose=False,
    )
    return chain
def story_init():
    print("story_init()")
    
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    model = ChatOpenAI(
                model="gpt-4o",
                temperature=0.7 # llm의 창의력(?) 정도, 높을 수록 대답이 자유분방해짐
                #streaming=True # 한 글자씩 출력하게 함 -> 반응성 향상
            )
    memory = ConversationSummaryBufferMemory(
            llm = model,
            max_token_limit=20,
            memory_key="chat_history",
            return_messages=True,
            input_key="user_input",
        )
    inital_prompt = (
                    """
                        You are a professional storyteller for young children.
                        You only reply in Korean.
                        Use simple korean words that are easy for children to understand.
                        You will be provided with a base64-encoded image, and you have to write a short story within 3 ~ 4 sentences.
                        Write the story in a way that explains what's going on in the current image and creates curiosity.
                        If there is a history between AI and human, than continue the story from previous one.
                        Stories should flow naturally from the previous one.
                        When user says "last image", then end up the story.
                        Return story like this: 
			            "the story goes here..."
                        If there is an error such as image not found, just return "이미지 인식 실패!".
                    """
                )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", [
                inital_prompt
                ]),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", [
                {
                    "type" : "text",
                    "text" : "{user_input}"
                },
                {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,{image_b64}"},
                    }
            ]),
        ],
    )

    chain = LLMChain(
        llm=model,
        memory=memory,
        prompt=prompt,
        verbose=False,
    )
    return chain

def invoke_chain(question,chain):
    result=chain.predict(user_input="", image_b64=question)
    #result=chain.predict(user_input="this is a last image", image_b64=question)
    return result

# GPT에게 이미지 전달하는 함수
def generate_caption(image_array,chain):
    try:
        # 이미지 URL 생성 (이미지 경로를 서버 URL과 결합)
        #image_url = "http://192.168.0.11:8081/" + image_path

        # 이미지 데이터를 GPT에게 전달
        result=invoke_chain(image_array,chain)

        return result
    except Exception as e:
        return f"Error occurred while generating caption: {e}"
    
def generate_story(image_array,chain):
    try:
        # 이미지 URL 생성 (이미지 경로를 서버 URL과 결합)
        #image_url = "http://192.168.0.11:8081/" + image_path

        # 이미지 데이터를 GPT에게 전달
        result=invoke_chain(image_array,chain)

        return result
    except Exception as e:
        return f"Error occurred while generating caption: {e}"
    
