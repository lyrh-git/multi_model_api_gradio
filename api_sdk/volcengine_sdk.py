# coding:utf-8
from __future__ import print_function

import concurrent.futures
import copy
import datetime
import json
import os
import re

import time
import unittest
import random

import requests
from PIL import Image

import os
from volcenginesdkarkruntime import Ark

import cv2

from common.ImageHandler import ImageHandler
from common.logger import setup_logging
from common.TimeHandler import TimeHandler

logger = setup_logging("volcengine__logger")
image_handler = ImageHandler()
time_handler = TimeHandler()

def get_path_prefix_tail(path):
    t = re.search("(.+)(\.[^.]+)", path, flags=re.S)
    if t:
        return t.group(1), t.group(2)
    else:
        return path, ""

def save_and_log(prompt, input_path, result, output_path=None, other_exist_info=None, other_out_keys=None, save_images_count=1):
    log_message = dict()

    if save_images_count > 1:
        if result.get("binary_data_base64"):
            cnt = min(len(result.get("binary_data_base64")), save_images_count)
        elif result.get("image_urls"):
            cnt = min(len(result.get("image_urls")), save_images_count)
    else:
        cnt = save_images_count
    print(f"SAVE PICTURE COUNT: {cnt}")

    output_paths = list()
    if output_path:
        if cnt == 1:
            output_paths = [output_path]
        else:
            for i in range(cnt):
                prefix, tail = get_path_prefix_tail(output_path)
                _output_path = f"{prefix} {i + 1}{tail}"
                output_paths.append(_output_path)

    if isinstance(result, dict) and result.get("binary_data_base64"):
        # print(f"save from binary_data_base64, output_path {output_path}")
        output_images_base64 = result.get("binary_data_base64")
        log_message = {
            "input_data": str(input_path)[:100],
            "prompt": prompt,
            "output_path": output_paths
        }

        for i, output_image_base64 in enumerate(output_images_base64[:cnt]):
            image_handler.base64_to_image(output_image_base64, output_paths[i])


    elif isinstance(result, dict) and result.get("image_urls"):
        # print(f"save from image_urls, output_path {output_path}")
        log_message = {
            "input_data": str(input_path)[:100],
            "prompt": prompt,
            "output_path": output_paths,
            "image_url": []
        }
        for i, image_url in enumerate(result.get("image_urls")[:cnt]):
            log_message["image_url"].append(image_url)
            image_base64 = image_handler.image_data_to_base64(image_url)
            image_handler.base64_to_image(image_base64, output_paths[i])

    elif (isinstance(result, dict) and result.get("video_url")) or "content" in str(type(result)).lower():
        video_url = result.get("video_url") if isinstance(result, dict) else result.video_url

        response = requests.get(video_url, stream=True)
        response.raise_for_status()  # 检查响应状态码是否为200
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=10240):
                f.write(chunk)

    if other_exist_info:
        log_message.update(other_exist_info)
    if other_out_keys:
        for k in other_out_keys:
            if k not in log_message and k in result:
                log_message[k] = result.get(k, "")
    print(f"Log message: {log_message}")

    logger.info(json.dumps(log_message, ensure_ascii=False))  # 使用 JSON 格式记录日志消息
    # print(result)


def cut_print(response):
    new_resp = copy.deepcopy(response)
    if isinstance(new_resp, dict) and "binary_data_base64" in new_resp.get("data", ""):
        new_resp["data"]["binary_data_base64"] = [str(x)[:100] + "..." for x in new_resp["data"]["binary_data_base64"]]
    return new_resp
    # return response


def cut_print_form(form):
    keys = ["binary_data_base64", "product_image_input", "ref_image_input"]
    new_form = copy.deepcopy(form)
    for k in keys:
        if k in new_form:
            if not isinstance(new_form[k], list):
                new_form[k] = [new_form[k]]
            new_form[k] = [str(x)[:100] + "..." for x in new_form[k]]
    return new_form


def generate_random_seed():
    return random.randint(0, 2 ** 32 - 1)


class VolcengineAPI:
    def __init__(self):
        # 以华北 2 (北京) 为例，<ARK_BASE_URL> 处应改为 https://ark.cn-beijing.volces.com/api/v3
        # self.client = Ark(
        #     ak="AKxxxg",
        #     sk="TTxxxRQ==",
        #     timeout=1000,
        #     max_retries=2
        # )  # 不支持 ak sk
        # self.client = Ark(api_key="98d65202-3179-478a-83f6-a17a4ed1ec68")
        self.client = Ark(api_key="e512c929-afab-46d2-8011-6d4b04ee71db")
        self.output_videos_path = "/Users/admin/program/projects/multi_model_api_gradio/data/output_videos/"


    def video_generation(self, model, prompt="", image_data1=None, image_data2=None, output_path=None, params=None):
        '''图生视频
        https://www.volcengine.com/docs/82379/1520757
        https://www.volcengine.com/docs/82379/1521309
        '''
        print(f"\n===\nYou are using [image_to_video]...")

        # 更新
        # 文生视频 | doubao-seedance-1-0-pro-250528
        # 图生视频-首帧 | doubao-seedance-1-0-pro-250528

        # 文生视频 | doubao-seedance-1-0-lite-t2v-250428
        # 文生视频 | doubao-seaweed
        # 图生视频-首帧 | doubao-seedance-1-0-lite-i2v-250428
        # 图生视频-首尾帧 | wan2-1-14b-flf2v-250417
        # 图生视频-首尾帧 | wan2-1-14b-flf2v-250417

        # 即梦3.0 （seedance 1.0）
        # 即梦S2.0 (seaweed alpha)
        # 即梦S2.0 pro (seaweed alpha)
        # 即梦P2.0 pro （pixeldance）

        # 即梦3.0 （seedance 1.0）doubao-seedance-1.0-lite
        # 即梦S2.0 (seaweed alpha)即梦S2.0 pro (seaweed alpha)都是doubao-seaweed


        task = model.split("|")[0].strip()
        if task == "文生视频":
            image_data1 = None
            image_data2 = None

        elif task == "图生视频-首帧":
            image_data2 = None
            if not params:
                params = dict()
            if "ratio" not in params or params.get("ratio") == "keep_ratio":
                params["ratio"] = "adaptive"

        model = model.split("|")[-1].strip()


        if not output_path:
            dir_path = f"{self.output_videos_path}/{model}"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            output_path = f"{dir_path}/{time_handler.time_string_now()}.mp4"

        image_url1, image_url2 = "", ""
        if image_data1:
            image_url1 = image_handler.image_data_to_remote_url(image_data1)
        if image_data2:
            image_url2 = image_handler.image_data_to_remote_url(image_data2)

        params_map = {
            "resolution": "rs",  # 视频分辨率，枚举值： 480p  720p（默认）
            "ratio": "rt",  # wan2.1-14b-i2v 默认值 keep_ratio
                            # doubao-seaweed 图生视频，默认值：根据所上传图片的比例，自动选择最合适的宽高比。   image to video only supports '--ratio adaptive
                            # doubao-seedance-1-0-lite-i2v，默认值：根据所上传图片的比例，自动选择最合适的宽高比
                            # 16:9  4:3  1:1  3:4  9:16  21:9  9:21  keep_ratio：所生成视频的宽高比与所上传图片的宽高比保持一致。
            "duration": "dur",  # 生成视频时长，单位：秒。枚举值： 5（默认）  10
            "framepersecond": "fps",  # 帧率，即一秒时间内视频画面数量。枚举值：16 24
                                      # wan2.1-14b 默认值 16   doubao-seaweed 默认值 2
            "watermark": "wm",  # 生成视频是否包含水印。枚举值： false：不含水印。（默认） true：含有水印。
            "seed": "seed",  # 种子整数，用于控制生成内容的随机性。取值范围：[-1, 2^32-1]之间的整数。
                             # 当不指定seed值或令seed取值为-1时，会使用随机数替代。
                             # 改变seed值，是相同的请求获得不同结果的一种方法。对相同的请求使用相同的seed值会产生类似的结果，但不保证完全一致。

            "camerafixed": "cf"  # 是否固定摄像头。枚举值： true：固定摄像头。平台会在用户提示词中追加固定摄像头，实际效果不保证。 false：不固定摄像头。（默认)
        }
        req_params = dict()
        if params:
            for k, v in params.items():
                if k in params_map:
                    req_params[params_map.get(k)] = v
                else:
                    print(f"[ERROR]: {k} parameter not in image_to_video, will escape.")

        req_params_text = " --".join([f"{k} {str(v).lower()}" for k, v in req_params.items()])

        content = []
        content.append(
            {
                "type": "text",
                "text": prompt + req_params_text
            })
        if image_url1:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url1
                    },
                    "role": "first_frame"
                })
        if image_url2:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url2
                    },
                    "role": "last_frame"
                })


        form = {
            "model": model,
            "content": content
        }
        print(f"Request1: {cut_print_form(form)}")

        response = self.client.content_generation.tasks.create(
            # doubao-seedance-1-0-lite-t2v-250428
            model=model,
            content=content
        )
        # res = requests.post(URL, data=json.dumps(form))
        # response = res.json()
        print(response)
        print(f"Response1: {cut_print(response)}")
        result = response

        # task_id = result.get("id")
        task_id = result.id
        print(f"TASK_ID: {task_id}")  # "cgt-2025****"

        video_url = ""
        start_time = time.time()
        try_cnt = 1
        while not video_url:
            print(f"trying {try_cnt} ...")
            if time.time() - start_time < 1000 and try_cnt <= 20:
                form2 = {
                    "req_key": "jimeng_vgfm_i2v_l20",
                    "task_id": task_id
                }
                print(f"Request2: {cut_print_form(form2)}")
                response2 = self.client.content_generation.tasks.get(task_id=task_id)
                # res2 = requests.post(URL, data=json.dumps(form2))
                # response2 = res2.json()
                print(response2)
                print(f"Response2: {cut_print(response2)}")

                result2 = response2.content
                if result2:
                    video_url = result2.video_url
                    break
                elif response2.error:
                    print(f"[ERROR]: {response2.error}")
                    break
                else:
                    time.sleep(10)
                    try_cnt += 1
            else:
                break

        # resp_data, video_url
        whole_result = {
            "output_video": video_url,
            "video_url": video_url,
            "output_path": output_path
        }

        save_and_log(prompt, "", result2, output_path, other_exist_info={"form": cut_print_form(form2)})

        print(f"Used [image_to_video] over.")
        return whole_result

class TEST(unittest.TestCase):

    volcengine_api = VolcengineAPI()

    def test_video_generation(self):
        model = "文生视频 | doubao-seedance-1-0-lite-t2v-250428"
        prompt = "一个女子手持TF口红展示。"
        result = self.volcengine_api.video_generation(model, prompt=prompt, image_data1=None, image_data2=None, output_path=None, params=None)