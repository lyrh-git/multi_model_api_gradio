import json
import unittest

# 通过 pip install volcengine-python-sdk[ark] 安装方舟SDK
from volcenginesdkarkruntime import Ark

from common.ChatHandler  import ChatHandler
from other_sdk import ImageHandler
from common.logger import setup_logging
from llm_api import LLMChat, Config

image_handler = ImageHandler()
chat_handler = ChatHandler()
logger = setup_logging("fangzhou_sdk__logger")
class FangzhouAPI:
    def __init__(self):
        self.client = Ark(api_key='e512c929-afab-46d2-8011-6d4b04ee71db')

        self.fangzhouClient = Ark(api_key="e512c929-afab-46d2-8011-6d4b04ee71db")
        self.chat = LLMChat(Config.SETTINGS)
        self.chat.initialize()

    def picture_to_text__fangzhou(self, image, prompt=None, model="Doubao-vision-pro-32k-241028", params=None):
        print(f"\n===\nYou are using [picture_to_text__fangzhou]...")

        model_map = {
            "Doubao-vision-lite-32k": {  # 推理时延短
                "ep_id": "ep-20250106191742-z4w99",
                "prompt": "请详细解读图片中的信息，包括不限于图片风格、图片主题、图片主体、图片背景、图片氛围、图片文字等，如果图片是关于某个产品，那你要重点描述产品的品牌、名称、类别、形状、颜色、大小、材质、纹理、打开状态、外部结构、内部结构等信息。不需要分点描述，用自然流畅的语言描述即可。"
            },
            "Doubao-vision-pro-32k-241028": {  # 推理时延长，准确率高一些
                "ep_id": "ep-20241231161330-b2p2c",
                "prompt": "详细解读这张图片"
            }
        }

        if model not in model_map:
            model = "Doubao-vision-pro-32k-241028"

        ep_id = model_map.get(model).get("ep_id")
        prompt = model_map.get(model).get("prompt") if not prompt else prompt

        # Doubao-vision-pro-32k-241028: ep-20241231161330-b2p2c  推理时延长，准确率高一些
        # Doubao-vision-lite-32k:  ep-20250106191742-z4w99   推理时延短

        base64_image = image_handler.image_data_to_base64(image)
        image_type = image_handler.get_image_type_by_base64(base64_image)
        print(f"this image type is {image_type}")

        prompt = "请详细解读图片中的信息，包括不限于图片风格、图片主题、图片主体、图片背景、图片氛围、图片文字等，如果图片是关于某个产品，那你要重点描述产品的品牌、名称、类别、形状、颜色、大小、材质、纹理、打开状态、外部结构、内部结构等信息。不需要分点描述，用自然流畅的语言描述即可。" if not prompt else prompt
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            # 需要注意：传入Base64编码前需要增加前缀 data:image/{图片格式};base64,{Base64编码}：
                            # PNG图片："url":  f"data:image/png;base64,{base64_image}"
                            # JEPG图片："url":  f"data:image/jpeg;base64,{base64_image}"
                            # WEBP图片："url":  f"data:image/webp;base64,{base64_image}"
                            "url": f"data:image/{image_type};base64,{base64_image}"
                        },
                    },
                ]
            }]


        whole_result = {
            "text": ""
        }
        try:
            response = self.client.chat.completions.create(
                model=ep_id,
                messages=messages
            )
            whole_result["text"] = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Error]: {e}")

        log_message = {
            "prompt": prompt,
            "image": str(image)[:100],
            "model": model
        }
        log_message.update(whole_result)
        print(log_message)
        logger.info(json.dumps(log_message, ensure_ascii=False))
        print(f"Log message: {log_message}")
        print(f"Used [picture_to_text__fangzhou] over.")

        return whole_result



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

    def query_chat(self, texts, platform="fangzhou", model_name="default", paras=None):
        messages = self.handle_query_texts(texts)
        result = ""
        for each in self.chat.run(platform=platform,
                                  model_name=model_name,  # 使用默认模型
                                  messages=messages,
                                  params=paras):
            result += each
        return result

class Test(unittest.TestCase):
    fangzhou_api = FangzhouAPI()
    def test_picture_to_text__fangzhou(self):
        input_path = "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/美食-鲜花蛋糕1.png"
        # input_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/书灯/图片素材/商品详情-图片1.png"
        # base64: iVBORw0KGgoAAAANSUhEUgAABDgAAAWgCAYAAAC7UvMVAAAEDmlDQ1BrQ0dDb2xvclNwYWNlR2VuZXJpY1JHQgAAOI2NVV1oHFUU...
        # input_path = "data/source_images/男人图片.jpg"
        text = self.fangzhou_api.picture_to_text__fangzhou(input_path)
        print(text)

    def test_query_chat(self):
        print(self.fangzhou_api.query_chat("你好"))