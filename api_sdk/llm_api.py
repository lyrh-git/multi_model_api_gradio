#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/9/29
@Author  : Vincent
@File    : llm_api
@Function:
离线脚本，支持直接调用厂商大模型接口和本地开源模型
1.厂商接口从其余模块导入
2.本地开源使用vllm和ollama推理框架，调用方式使用openai的sdk文档
"""

from volcenginesdkarkruntime import Ark
from loguru import logger
import qianfan
import os
from openai import OpenAI
from api_sdk.CONFIG import QIANFAN_AK, QIANFAN_SK

class BaseChat(object):
    def __init__(self, config):
        self.config = config
        self.client = None
        self.model_names = config.get('model_names', {})

    def get_model_names(self):
        """获取支持的所有模型名称"""
        return self.model_names

    def add_model_name(self, model_name, model_value=None):
        """动态加入模型名称"""
        if model_name in self.model_names:
            logger.info("{} in {}, add failed, or change other name.", model_name, self.model_names)
            return

        model_value = model_name if model_value is None else model_value
        self.model_names[model_name] = model_value

    def get_client(self):
        pass

    def chat_completions(self, *args, **kwargs):
        pass


class BaiduChat(BaseChat):
    name = "qianfan"
    os.environ["QIANFAN_AK"] = QIANFAN_AK
    os.environ["QIANFAN_SK"] = QIANFAN_SK

    def chat_completions(self,
                         model_name,
                         messages,
                         stream=True,
                         top_k=None,
                         top_p=None,
                         extra_body=None,
                         ):
        if model_name not in self.model_names:
            logger.info("{} not in {}, default model {}", model_name,
                        self.model_names, self.model_names['default'])
        # 获取模型名称
        model = self.model_names.get(model_name) or self.model_names['default']

        chat_comp = qianfan.ChatCompletion()

        # 指定特定模型
        resp = chat_comp.do(
            model=model,
            messages=messages,
            stream=stream,
            top_k=top_k,
            top_p=top_p,
            extra_body=extra_body)

        for m in resp:
            yield m.body['result']


class OpenAIChat(BaseChat):
    """openai的调用方式"""

    def get_client(self):
        if self.client is None:
            self.client = OpenAI(
                api_key=self.config.get('api_key'),
                base_url=self.config.get('base_url')
            )

    def chat_completions(self,
                         model_name,
                         messages,
                         max_tokens=1000,
                         temperature=0,
                         history: list = None,
                         stream=True,
                         top_p=0.8,
                         extra_body=None,
                         ):
        self.get_client()
        if model_name not in self.model_names:
            logger.info("{} not in {}, default model {}", model_name,
                        self.model_names, self.model_names['default'])

        model = self.model_names.get(model_name) or self.model_names['default']
        stream = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            stream=stream,
            temperature=temperature,
            top_p=top_p,
            extra_body=extra_body
        )

        for chunk in stream:
            # print(chunk)
            # yield chunk
            if chunk.choices[0].delta.content is None:
                continue
            # print(chunk.choices[0])
            yield chunk.choices[0].delta.content
        # return stream


class FangZhou(OpenAIChat):
    def get_client(self):
        if self.client is None:
            self.client = Ark(
                api_key=self.config.get('api_key'),
                base_url=self.config.get('base_url')
            )


class Config(object):
    # 没用备注的支持联网的，默认不支持联网查询
    SETTINGS = {
        "qianfan": {
            "ak": "PtfH2ppBZmZ6A3Q6bvBGuh2W",
            "sk": "w5ZbM1cZUL1Ka8qBWTUyMhZ6pO4sF2nF",
            "model_names": {
                "default": "ChatGLM2-6B-32K",
                "chatglm2-6b-32k": "ChatGLM2-6B-32K",
            }
        },
        "hunyuan": {
            "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
            "api_key": "sk-NQTG9lphz6zKiYDETD9AdhBZSpKMPdm3nyfoFpcpdaSfSSk6",
            "model_names": {
                "default": "hunyuan-pro",
                'hunyuan-pro': "hunyuan-pro",
                'hunyuan-turbo': "hunyuan-turbo"
            },
        },
        "fangzhou": {
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",  # bot-20240708015513-rc7n6  doubao-pro-32k-240615
            "api_key": "e512c929-afab-46d2-8011-6d4b04ee71db",
            "model_names": {
                "default": "ep-20240602045312-t89w9",  # 默认Doubao-pro-32k
                # "DeepSeek-R1": "",  # 推理输入 0.0020元/千tokens, 推理输出 0.0080元/千tokens
                "Doubao-1.5-pro-32k": "ep-20250123155917-f5wbc",  # 250115, 推理输入 0.0008元/千tokens, 推理输出0.0020元/千tokens
                # "Doubao-1.5-lite-32k": "",  # 推理输入0.0003元/千tokens, 推理输出0.0006元/千tokens
                "Doubao-pro-32k-240828": "ep-20241014114011-2sqwc",  # 推理输入0.0008元/千tokens, 推理输出0.0020元/千tokens
                # "default": "bot-20240708015513-rc7n6",
                "Doubao-pro-32k": "ep-20240602045312-t89w9",
                "Doubao-pro-32k-func": "ep-20240627074759-gkwm5",  # 豆包-联网-pro-32k
                "Doubao-pro-128k": "ep-20240522101426-zhmmb",
                "Doubao-lite-4k": "ep-20240524040011-mfvf9",

                # deepseek-v3: 推理输入 0.0020元/千tokens, 推理输出 0.0080元/千tokens
                # deepseek-r1: 推理输入 0.0040元/千tokens, 推理输出 0.0160元/千tokens
            }
        },
        "qwen2": {
            "base_url": "https://model.yingsaidata.com/v1",  # 部署在华为云
            "api_key": "sss",
            "model_names": {
                "qwen2-72b": "/home/ma-user/work/qwen2-72b-infer/Qwen2-72B-Instruct-sft",
                "default": "/home/ma-user/work/qwen2-72b-infer/Qwen2-72B-Instruct-sft"
            }
        },
        "donson": {
            "base_url": "http://172.16.7.132:23153/v1",  # A800
            "api_key": "sss",
            "model_names": {
                "default": "glm4:9b-chat-fp16",
                "glm4:9b-chat-fp16": "glm4:9b-chat-fp16",
                "qwen:72b-chat-v1.5-fp16": "qwen:72b-chat-v1.5-fp16",
                "xhs_zhongcao_sft": ""
            }
        },
        "self": {
            "base_url": "http://118.195.157.208:23249/v1/",  # H100  # openaichat会自动拼上 chat/completions后缀
            "api_key": "sss",
            "model_names": {
                "default": "glm4:9b-chat-fp16",
                "xhs_zhongcao_sft": "/models/Qwen-110B-Instruct"
            }
        }
    }

    def to_json(self):
        pass

    def from_json(self):
        pass


class LLMChat(object):
    def __init__(self, settings):
        self.settings = settings
        self.clients = {}

    def initialize(self):
        """初始化所有模型客户端， 默认使用openai的sdk"""
        for k, v in self.settings.items():
            if k == "qianfan":
                self.clients[k] = BaiduChat(v)
            elif k == "fangzhou":
                self.clients[k] = FangZhou(v)
            else:
                self.clients[k] = OpenAIChat(v)  # 其余使用openai的sdk初始化
            logger.info("initialized model {}", k)

    def run(self, platform, messages, model_name=None, params=None):
        """
        大模型对话接口，stream=True 只支持流式请求
        platform: 平台名称
        model_name 平台支持的模型名称 配置错误会获取模型模型名称
        messages: chat completions 的对话
        params 其他参数
        """
        if platform not in self.settings:
            raise ValueError(f"{platform} error. value {self.settings.keys()}")

        body = params if isinstance(params, dict) else {}
        body['stream'] = True
        body['messages'] = messages
        body['model_name'] = model_name

        client = self.get_client(platform)
        stream = client.chat_completions(**body)
        return stream

    def get_client(self, platform):
        """获取平台客户端"""
        return self.clients[platform]


if __name__ == '__main__':
    # model = BaiduChat(config={
    #     "ak": "PtfH2ppBZmZ6A3Q6bvBGuh2W",
    #     "sk": "w5ZbM1cZUL1Ka8qBWTUyMhZ6pO4sF2nF",
    #     "model_names": ["ChatGLM2-6B-32K", ]})

    # model = OpenAIChat(Config.SETTINGS['qwen2'])
    # for each in model.chat_completions(
    #         model_name="/home/ma-user/work/qwen2-72b-infer/Qwen2-72B-Instruct-sft",
    #         messages=[{"role": "user", "content": "你是什么模型，能做什么"}],
    #         top_p=0.8):
    #     print(each, end="")

    # model = OpenAIChat(LLMChat.CONFIG['hunyuan'])
    # for each in model.chat_completions(model_name="hunyuan-pro",
    #                                    messages=[{"role": "user", "content": "你是什么模型，能做什么"}],
    #                                    top_p=0.8, stream=True):
    #     print(each, end="")

    # model = FangZhou(LLMChat.CONFIG['fangzhou'])
    # for each in model.chat_completions(model_name="ep-20240602045312-t89w9",
    #                                    messages=[{"role": "user", "content": "你是什么模型，能做什么"}],
    #                                    top_p=0.8, stream=True):
    #     print(each, end="")

    # model = OpenAIChat(LLMChat.CONFIG['donson'])
    # for each in model.chat_completions(model_name="qwen:72b-chat-v1.5-fp16",
    #                                    messages=[{"role": "user", "content": "你是什么模型，能做什么"}],
    #                                    top_p=0.8, stream=True):
    #     print(each, end="")

    chat = LLMChat(Config.SETTINGS)
    chat.initialize()

    # for each in chat.run(platform="fangzhou",
    #                      model_name="Doubao-pro-32k",  # 使用默认模型
    #                      messages=[{"role": "user", "content": "联网查询一下今天天气怎么样"}]):
    #     print(each, end="")

    for each in chat.run(platform="self",
                         model_name="xhs_zhongcao_sft",  # 使用默认模型
                         messages=[{"role": "user", "content": "给我写一个小红书种草文案"}]):
        print(each, end="")
