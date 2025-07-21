import json
import os
import unittest

import requests

from common.ImageHandler import ImageHandler
from common.logger import setup_logging
from common.TimeHandler import TimeHandler

image_handler = ImageHandler()
time_handler = TimeHandler()

logger = setup_logging("other_sdk__logger")
class OtherAPI:
    def picture_to_text__minicpm(self, image, prompt=None):
        print(f"\n===\nYou are using [picture_to_text__minicpm]...")
        model = "MiniCPM-V-2_6"
        url = "http://describe.yingsaidata.com/describe_image"
        body = {
            "image": image_handler.image_data_to_base64(image)
        }
        if prompt:
            body["prompt"] = prompt

        whole_result = {
            "text": ""
        }
        response = requests.post(url, json=body, timeout=60)
        if response.status_code == 200:
            result = response.json()
            whole_result["text"] = result.get("description", f"Error: can't fetch 'description' from response.")

        log_message = {
            "prompt": prompt,
            "image": str(image)[:100]
        }
        log_message.update(whole_result)
        logger.info(json.dumps(log_message, ensure_ascii=False))
        print(f"Log message: {log_message}")
        print(f"Used [picture_to_text__minicpm] over.")

        return whole_result


class Test(unittest.TestCase):
    other_api = OtherAPI()
    def test_picture_to_text__minicpm(self):
        input_path = "data/source_images/圣诞.png"
        # input_path = "data/source_images/男人图片.jpg"
        text = self.other_api.picture_to_text__minicpm(input_path)
        print(text)