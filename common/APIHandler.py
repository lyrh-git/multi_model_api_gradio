# coding=utf-8

from volcenginesdkarkruntime import Ark

from llm.llm_api import LLMChat, Config

from CommonHandler import JSONHandler
from FileHandler import FileHandler


class ApiHandler:
    json_handler = JSONHandler()
    file_handler = FileHandler()

    def __init__(self):
        self.fangzhouClient = Ark(api_key="e512c929-afab-46d2-8011-6d4b04ee71db")
        self.chat = LLMChat(Config.SETTINGS)
        self.chat.initialize()


