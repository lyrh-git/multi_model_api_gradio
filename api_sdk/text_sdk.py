# coding:utf-8
from __future__ import print_function

import json
import unittest
import requests

from common.ImageHandler import ImageHandler
from common.logger import setup_logging
from common.TimeHandler import TimeHandler

logger = setup_logging("text_sdk__logger")
image_handler = ImageHandler()
time_handler = TimeHandler()

class TextAPI:

    def handle_query_texts(self, texts):
        query_list = list()
        if isinstance(texts, str):
            query_list = [{"role": "user", "content": texts}]
        elif isinstance(texts, list):
            if all(isinstance(text, str) for text in texts):
                query_list = [{"role": "user" if i % 2 == 0 else "assistant", "content": text} for i, text in
                              enumerate(texts)]
            elif all(isinstance(text, dict) and "role" in text for text in texts):
                query_list = texts
        return query_list

    def text_chat_one_turn(self, prompt, model, params=None):
        model_list = ['qianfan | chatglm2-6b-32k',
                      'hunyuan | hunyuan-pro',
                      'hunyuan | hunyuan-turbo',
                      'fangzhou | Doubao-1.5-pro-32k',  # 有更新
                      'fangzhou | Doubao-pro-32k-240828',
                      'fangzhou | Doubao-pro-32k',
                      'fangzhou | Doubao-pro-32k-func',
                      'fangzhou | Doubao-pro-128k',
                      'fangzhou | Doubao-lite-4k',
                      'fangzhou | fangzhou_chat_agent',
                      'fangzhou | Deepseek-V3',
                      'fangzhou | Deepseek-r1-250120',
                      'qwen2 | qwen2-72b',
                      'donson | glm4:9b-chat-fp16',
                      'donson | qwen:72b-chat-v1.5-fp16',
                      'self | xhs_zhongcao_sft']

        url = "http://192.168.20.93:18000/llm/chatapi/v1/modelChat"

        form = {
            'messages': self.handle_query_texts(prompt),
            'stream': False,
            'model': model,
            'temperature': 0.5,
            'presence_penalty': 0,
            'frequency_penalty': 0,
            'top_p': 1
        }

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in text_chat_one_turn, will escape.")

        print(f"Request: {form}")
        logger.info(f"Request: {form}")
        # response = self.visual_service.cv_sync2async_submit_task(form)
        response = requests.post(url, data=json.dumps(form))
        result = response.json()
        print(f"Response: {result}")
        logger.info(f"Response: {result}")

        if not isinstance(result, dict):
            try:
                result = json.loads(result)
            except Exception as e:
                print(f"[ERROR]: {e}")
                result = dict()

        whole_result = {
            "answer": result.get("answer", "").strip(),
        }

        logger.info(f"whole_result: {whole_result}")
        print(f"Used [text_chat_one_turn] over.")
        return whole_result

class Test(unittest.TestCase):

    text_sdk = TextAPI()
    def test_text_chat_one_turn(self):
        prompt = "你是什么模型？"
        model = "fangzhou | Deepseek-r1-250120"
        result = self.text_sdk.text_chat_one_turn(prompt, model)
        print(result)