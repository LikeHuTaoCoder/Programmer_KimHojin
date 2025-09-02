from typing import List
import json
import os
import threading
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from image_captioning import generate_caption,generate_story
import crud
import re
import models

from threading import Thread
 
class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
 
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return
    
def remove_json_block(text):
    # ```json 또는 ```로 감싸진 블록 제거
    cleaned_text = re.sub(r"```json\s*|\s*```", "", text, flags=re.MULTILINE)
    return cleaned_text.strip() 

def generate_story_and_caption(base64_image:str,book:models.Book,page:models.Page,characters:List[models.CharacterInfo],story_chain,caption_chain):
    
    # 모든 스레드의 결과값을 받아오기 
    threads = []
       
    result=dict()
    result["characterInfo"]=list()
    
    thread=ThreadWithReturnValue(target=generate_story, args=(base64_image,story_chain,))
    threads.append(thread)
    thread.start()

    for chara in characters:
        base64_chara_image = crud.get_character_image(book_path=book.book_path,
                                            page=page.page_order,
                                            char=chara.character_index)

        thread=ThreadWithReturnValue(target=generate_caption, args=(base64_chara_image,caption_chain,))
        threads.append(thread)
        thread.start()
   
    for index,thread in enumerate(threads):
        thread_result = thread.join()  # join()이 실행 결과를 반환함
        thread_result = remove_json_block(thread_result)
        if index == 0:
            result["story"]=thread_result
        else:
            print(thread_result)
            result["characterInfo"].append(json.loads(thread_result))
    if len(result["characterInfo"]) == 0:
        result["characterInfo"]="null"
    return result
    