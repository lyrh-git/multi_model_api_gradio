
import base64
import hashlib
import imghdr
import io
import json
import os
import re
import unittest

import PIL.Image
import cv2
import numpy as np
from PIL import Image
import requests

from config import NGINX as NGINX_URL
from TimeHandler import TimeHandler

time_handler = TimeHandler()

class ImageHandler:

    NGINX = NGINX_URL
    def image_path_to_base64(self, image_path):
        with open(image_path, "rb") as file:
            # 读取文件内容
            file_data = file.read()
            # 使用base64编码
            base64_encoded = base64.b64encode(file_data)
            # 将bytes对象转换为字符串
            base64_string = base64_encoded.decode("utf-8")
            return base64_string
            # "ngrok http 8889 --request-header-add ngrok-skip-browser-warning:true"

    def image_data_to_base64(self, input_data):
        # print(f"Handing image_data_to_base64... \n"
        #       f"input_data type: {type(input_data)}\n"
        #       f"input_data: {input_data}")
        if isinstance(input_data, str):
            print(f"input data str: {input_data}")
            if input_data.startswith("http"):
                print(f"downloading image from {input_data} ...")
                response = requests.get(input_data)
                response.raise_for_status()  # 检查响应状态码是否为200
                input_image_base64 = response.content
                # print("response content type: ", type(input_image_base64))
            else:
                print(input_data)
                assert os.path.exists(input_data), f"{input_data} does not exist"
                input_image_base64 = self.image_path_to_base64(input_data)
        elif isinstance(input_data, PIL.Image.Image):
            img_buffer = io.BytesIO()
            try:
                input_data.save(img_buffer, format="JPEG")
            except Exception as e:
                print(f"Error: {e}")
                input_data.save(img_buffer, format="png")
            byte_data = img_buffer.getvalue()
            input_image_base64 = base64.b64encode(byte_data).decode('utf-8')  # 解码成bytes
        else:
            input_image_base64 = base64.b64encode(input_data.tobytes()).decode('utf-8')
        # print("final_image_type: ", type(input_image_base64))
        return input_image_base64

    def image_data_to_bytes(self, input_data, output_type="bytes"):
        image_base64 = self.image_data_to_base64(input_data)
        if not isinstance(image_base64, bytes):
            image_rb = base64.b64decode(image_base64)
        else:
            image_rb = image_base64
        img_rb_io = io.BytesIO(image_rb)  # _io.BytesIO
        img_rb = img_rb_io.read()  # bytes
        img_rb_buffered = io.BufferedReader(img_rb_io)  # _io.BufferedReader
        if output_type == "bytes":
            return img_rb
        elif output_type == "bytes_io":
            return img_rb_io
        elif output_type == "buffer":
            return img_rb_buffered
        return img_rb_buffered

    def base64_to_image(self, image_data, image_path=None):
        # print(f"image_data type: {type(image_data)}")
        if not isinstance(image_data, bytes):
            image_rb = base64.b64decode(image_data)
        else:
            image_rb = image_data
        img_rb_io = io.BytesIO(image_rb)
        image_object = Image.open(img_rb_io)
        if image_path:
            # print(image_path, "saving")
            image_object.save(image_path)
        return image_object

    def get_result_image(self, result, images_count=1):
        cnt = images_count
        images_base64 = list()
        if result.get("binary_data_base64"):
            cnt = min(images_count, len(result['binary_data_base64']))
            images_base64 = result['binary_data_base64'][:cnt]
        elif result.get("image_urls"):
            cnt = min(images_count, len(result['image_urls']))
            image_urls = result['image_urls'][:cnt]
            images_base64 = list()
            for image_url in image_urls:
                response = requests.get(image_url)
                response.raise_for_status()  # 检查响应状态码是否为200
                images_base64.append(response.content)
        return [self.base64_to_image(image_base64) for image_base64 in images_base64]

    def get_result_video_base64(self, result, videos_count=1):
        cnt = videos_count
        videos_base64 = list()
        if result.get("binary_data_base64"):
            cnt = min(videos_count, len(result['binary_data_base64']))
            videos_base64 = result['binary_data_base64'][:cnt]
        elif result.get("video_url"):
            cnt = min(videos_count, len(result['video_url']))
            video_urls = result['video_url'][:cnt]
            videos_base64 = list()
            for video_url in video_urls:
                response = requests.get(video_url)
                response.raise_for_status()  # 检查响应状态码是否为200
                videos_base64.append(response.content)
        return videos_base64



    # 计算图片的 MD5 值
    def calculate_md5(self, image_object):
        hash_md5 = hashlib.md5()
        if isinstance(image_object, str):
            image_object = image_object.encode("utf-8")
            hash_md5.update(image_object)
        elif isinstance(image_object, bytes):
            hash_md5.update(image_object)
        elif isinstance(image_object, PIL.Image.Image):
            for chunk in iter(lambda: image_object.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_image_type_by_base64(self, image_base64):
        img_data = base64.b64decode(image_base64)
        img_type = imghdr.what(None, h=img_data)
        return img_type

    def base64_to_url(self, image_base64):
        image_type = self.get_image_type_by_base64(image_base64)
        url = f'data:image/{image_type};base64,{image_base64}'
        return url

    def base64_to_remote_url(self, image_base64):

        server = self.NGINX
        body = {
            "image_base64": image_base64
        }
        headers = {
            "ngrok-skip-browser-warning": "111"
        }
        response = requests.post(f"{server}/save_show_image", json=body, headers=headers)
        remote_url = f"{server}/{response.text}"
        return remote_url

    def image_path_to_remote_url(self, filename):
        server = self.NGINX
        body = {
            "image_filename": filename
        }
        response = requests.post(f"{server}/save_show_image", json=body)
        remote_url = f"{server}/{response.text}"
        return remote_url

    def get_image_contrary(self, image):
        image_array = np.array(image)
        input_width, input_height = image_array.shape[1], image_array.shape[0]
        print(f"Image shape: {image_array.shape}")
        print(f"Image size - width: {input_width}, height: {input_height}")
        mask_binary = np.zeros((input_height, input_width), dtype=np.uint8)

        if len(image_array.shape) == 3:
            if image_array.shape[-1] == 4:  # RGBA格式
                mask_binary[image_array[:, :, 3] < 255] = 255  # 只考虑alpha通道
                mask_binary[image_array[:, :, 3] >= 255] = 0  # 只考虑alpha通道
            else:  # RGB格式
                mask_binary[np.any(image_array[:, :, :3] < 255, axis=-1)] = 255
                mask_binary[np.any(image_array[:, :, :3] >= 255, axis=-1)] = 0
        else:  # 单通道
            mask_binary[image_array[:, :] < 255] = 255  # 0黑，255白
            mask_binary[image_array[:, :] >= 255] = 0
        return Image.fromarray(mask_binary.astype('uint8'))


    def image_overlay(self, images):

        image_objs = [self.base64_to_image(self.image_data_to_base64(x)) for x in images]
        # # 打开主图像（背景图像）
        # img1 = Image.open('background_image.png')
        #
        # # 打开叠加图像（包含透明区域）
        # img2 = Image.open('overlay_image.png')

        # 在主图像上叠加叠加图像
        image_objs[0].paste(image_objs[1], (0, 0), mask=image_objs[1])

        # 显示结果
        # image_objs[0].show()
        return image_objs[0]

        # image_cvs = [cv2.cvtColor(np.asarray(x), cv2.COLOR_RGB2BGR) for x in image_objs]
        #
        # image_cvs_reserved = image_cvs[::-1]
        # img_add = cv2.add(image_cvs_reserved[0], image_cvs_reserved[1])
        # # img_add = image_cvs_reserved[0]
        # # for x in image_cvs_reserved[1:]:
        # #     img_add = cv2.add(img_add, x)
        #
        # # 显示结果
        # cv2.imshow('Image Add', img_add)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    def image_data_to_remote_url(self, image_data):
        image_base64 = self.image_data_to_base64(image_data)
        image_type = self.get_image_type_by_base64(image_base64)

        image_bytes = self.image_data_to_bytes(image_data, output_type="bytes")

        now_time = time_handler.time_string_now()

        if isinstance(image_data, str) and os.path.exists(image_data):
            file_name = re.search("[/\\\]*([^/\\\]+\.[^/\\\]+)$", image_data).group(1)
        else:
            file_name = f'{now_time}.{image_type}'

        print(f"Uploading image {file_name} ...")
        url = "https://mlmhs.yingsaidata.com/xhszc/common/uploadImage"

        payload = {}
        files = [
            ('file', (file_name, image_bytes, f'image/{image_type}'))  # 成功！
            # xxx失败xxx ('file', (file_name, image_bytes_buffer, f'image/{image_type}'))  # 失败（文件为空）：requests files: [('file', ('松下吹风机.png', <_io.BufferedReader>, 'image/png'))]
            # √√√成功√√√ ('file', (file_name, open(image_data, "rb"), f'image/{image_type}'))  # 成功： <_io.BufferedReader name='/Users/admin/program/projects/multi_model_api_gradio/data/flask/upload/松下吹风机.png'>
        ]
        # print(f"requests files: {files}")
        headers = {}

        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        result = response.json()
        print(result)
        image_url = result.get("data", dict()).get("url", None)
        if not image_url:
            print(f"Upload image failed, message: {result}")
        else:
            print(f"Upload image {file_name} successfully, url: {image_url}")
        return image_url



class TEST(unittest.TestCase):
    image_handler = ImageHandler()
    def test_get_image_contrary(self):
        image = Image.open("/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/美食-鲜花蛋糕1 背景白.png")
        self.image_handler.get_image_contrary(image)

    def test_base64_to_remote_url(self):
        path = "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/植物-南天竹1.png"
        image_base64 = self.image_handler.image_path_to_base64(path)
        remote_url = self.image_handler.base64_to_remote_url(image_base64)
        print(remote_url)

    def test_image_path_to_remote_url(self):
        filename = "test_picture.png"
        remote_url = self.image_handler.image_path_to_remote_url(filename)
        print(remote_url)

    def test_image_overlay(self):
        paths = [
                 "/Users/admin/Files/评测/文生图/图片/source/商品图加字/松下吹风机/图生文生图2 抠图 涂抹.png",
            "/Users/admin/Files/评测/文生图/图片/source/商品图加字/松下吹风机/松下吹风机 抠图.png"
        ]
        self.image_handler.image_overlay(paths)

    def test_image_data_to_remote_url(self):
        image_path = "/Users/admin/program/projects/multi_model_api_gradio/data/flask/upload/松下吹风机.png"
        result = self.image_handler.image_data_to_remote_url(image_path)
        print(result)
