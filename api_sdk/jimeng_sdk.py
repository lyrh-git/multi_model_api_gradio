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
import urllib

import numpy as np
import requests
from PIL import Image

from volcengine.visual.VisualService import VisualService

import cv2

from common.ImageHandler import ImageHandler
from common.logger import setup_logging
from common.TimeHandler import TimeHandler

from CONFIG import AK, SK

logger = setup_logging("jimeng__logger")
image_handler = ImageHandler()
time_handler = TimeHandler()


def get_path_prefix_tail(path):
    t = re.search("(.+)(\.[^.]+)", path, flags=re.S)
    if t:
        return t.group(1), t.group(2)
    else:
        return path, ""


def save_and_log(prompt, input_path, result, output_path=None, other_exist_info=None, other_out_keys=None,
                 save_images_count=1):
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

    if result.get("binary_data_base64"):
        # print(f"save from binary_data_base64, output_path {output_path}")
        output_images_base64 = result.get("binary_data_base64")
        log_message = {
            "input_data": str(input_path)[:100],
            "prompt": prompt,
            "output_path": output_paths
        }

        for i, output_image_base64 in enumerate(output_images_base64[:cnt]):
            image_handler.base64_to_image(output_image_base64, output_paths[i])


    elif result.get("image_urls"):
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

    elif result.get("video_url"):
        video_url = result.get("video_url")
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
                log_message[k] = result.get(k)
    print(f"Log message: {log_message}")

    logger.info(json.dumps(log_message, ensure_ascii=False))  # 使用 JSON 格式记录日志消息
    # print(result)


def cut_print(response):
    new_resp = copy.deepcopy(response)
    if "binary_data_base64" in new_resp.get("data"):
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


class JiMengAPI:
    def __init__(self):
        self.visual_service = VisualService()
        # call below method if you don't set ak and sk in $HOME/.volc/config
        self.visual_service.set_ak(AK)
        self.visual_service.set_sk(SK)

        self.output_images_path = "/Users/admin/program/projects/multi_model_api_gradio/data/output_images/"
        self.output_videos_path = "/Users/admin/program/projects/multi_model_api_gradio/data/output_videos/"

    def text_to_image(self, prompt, negative_prompt="", model="文生图2.0L", output_path=None, params=None):
        '''文生图
        3.0：https://www.volcengine.com/docs/85128/1526761'''
        print(f"\n===\nYou are using [text_to_image]...")
        model_map = {
            "文生图2.0L": {
                "req_key": "high_aes_general_v20_L",
                "model_version": "general_v2.0_L",
                "req_schedule_conf": "general_v20_9B_pe",
                "scale__default": 3.5
            },
            "文生图2.1": {
                "req_key": "high_aes_general_v21_L",
                "model_version": "general_v2.1_L",
                "req_schedule_conf": "general_v20_9B_pe",
                "scale__default": 3.5
                # 默认值：general_v20_9B_pe, 标准版：general_v20_9B_rephraser, 美感版：general_v20_9B_pe
            },
            "文生图3.0": {
                "req_key": "high_aes_general_v30l_zt2i",
                "scale__default": 2.5
            }
        }
        if model in model_map:
            model_info = model_map.get(model)
        else:
            model = "文生图2.0L"
            model_info = model_map.get("文生图2.0L")

        if not output_path:
            output_path = f"{self.output_images_path}/text_to_image/"

        params = dict() if not params else params

        seed, use_pre_llm, use_sr = -1, False, True
        width, height = 576, 1024
        if params:
            if params.get("seed", -1) > -1:
                seed = params.get("seed")
            use_pre_llm = params.get("use_pre_llm", False)
            width = params.get("width", 576)
            height = params.get("height", 1024)
            use_sr = params.get("use_sr", False)

        form = model_info.copy()
        form.update({
            # "req_key": model_info["req_key"],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            # "model_version": model_info["model_version"],
            # "req_schedule_conf": model_info["req_schedule_conf"],
            "seed": seed,
            "scale": params.get("scale", model_info.get("scale__default", 3.5)),  # 3.5 [1, 10]
            "ddim_steps": params.get("ddim_steps", 16 if model == "文生图2.0L" else 25),
            # 2.1 -> 25 [1, 200] 推荐[1, 50]; 2.0 -> 16 [1-50]
            "width": width,  # 512 [256, 768]
            "height": height,  # 512 [256, 768]
            "use_pre_llm": use_pre_llm,
            "use_sr": use_sr,
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "logo_text_content": ""
            }
        })

        num_images_per_prompt = params.get("num_images", 2)
        res = []

        whole_result = {
            "output_images": list(),
            "llm_result": ""
        }

        print(f"Request: {cut_print_form(form)}")
        print(f"request times: {num_images_per_prompt}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for _ in range(num_images_per_prompt):
                # 提交任务到线程池
                futures.append(executor.submit(self.visual_service.cv_process, form))

            idx = 0
            for future in concurrent.futures.as_completed(futures):
                print(f"Fetching the {idx}th picture...")
                resp = future.result()
                print(f"Response: {cut_print(resp)}")
                image_url = resp['data']['image_urls'][0]
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()  # 检查响应状态码是否为200
                    image_base64 = response.content

                    result = resp.get("data")
                    if not result.get("binary_data_base64"):
                        result["binary_data_base64"] = [image_base64]

                    # image_rb = io.BytesIO(image_base64)
                    # md5 = image_handler.calculate_md5(image_rb)
                    if output_path:
                        tail = prompt[:20].replace("/", "_\\")
                        inner_output_path = os.path.join(output_path,
                                                         f'{time_handler.time_string_now()} - {tail} {idx}.jpg')
                        idx += 1
                    print("output_path: ", inner_output_path)
                    save_and_log(prompt, "", result, inner_output_path, other_exist_info=form,
                                 other_out_keys=["llm_result", "pe_result", "predict_tags_result", "rephraser_result"])
                    res += image_handler.get_result_image(result)
                    if use_pre_llm:
                        whole_result["llm_result"] += f"{idx}：{result.get('llm_result', '')}\n"
                except requests.RequestException as e:
                    print("图片生成失败")
                    return None
        whole_result["output_images"] = res
        print(f"\n===\nUsed [text_to_image] over.\n\n\n")
        return whole_result

    def image_text_seed_edit(self, prompt, input_data, output_path=None, params=None):
        '''图指令编辑 https://www.volcengine.com/docs/6791/1384311'''
        print(f"\n===\nYou are using [image_text_seed_edit]...")
        source_image_base64 = image_handler.image_data_to_base64(input_data)

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/image_text_seed_edit/{time_handler.time_string_now()} - {tail}.jpg"

        whole_result = {
            "output_images": list(),
            "vlm_result": ""
        }

        # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
        form = {
            "req_key": "byteedit_v2.0",
            "binary_data_base64": [source_image_base64],
            # "image_urls": [
            #     input_path
            # ],
            "prompt": prompt,
            "negative_prompt": "",
            "seed": -1,
            "scale": 0.5,  # 0.5 [0, 1]
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "logo_text_content": ""
            }
        }
        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in text_seed_edit, will escape.")

        # print(form)

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        save_and_log(prompt, input_data, result, output_path, other_out_keys=["vlm_result"])

        whole_result["output_images"] = image_handler.get_result_image(result)
        whole_result["vlm_result"] = result.get("vlm_result", "")

        print(f"Used [image_text_seed_edit] over.")
        return whole_result

    def image_text_seed_edit_2(self, prompt, input_data, output_path=None, params=None):
        '''图指令编辑
        https://api.volcengine.com/api-docs/view?serviceCode=cv&version=2024-06-06&action=Img2imgAIDoodleDreamina
        '''
        print(f"\n===\nYou are using [image_text_seed_edit_2]...")
        # source_image_base64 = image_handler.image_data_to_base64(input_data)
        source_image_url = image_handler.image_data_to_remote_url(input_data)

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/image_text_seed_edit_2/{time_handler.time_string_now()} - {tail}.jpg"

        whole_result = {
            "output_images": list()
        }

        # 请求Body(查看接口文档请求参数-请求示例，将请求参数内容复制到此)
        form = {
            "req_key": "img2img_ai_doodle_dreamina",
            # "binary_data_base64": [source_image_base64],
            "image_urls": [
                source_image_url
            ],
            "prompt": prompt,
            "cfg": 3.0,
            # 控制提示词与出图相关性；参数越大，生成的图像与文本提示的相关性越高，但可能会失真。数值越小，相关性则越低，越有可能偏离提示或输入图像，但质量越好。默认值：3.0；取值范围：[0.1, 10.0]
            "strength": 0.9924999999999999,
            # 取值越小输出图与输入图关联参考性越大，取值越大与输入图参考性越小；默认值：0.9924999999999999（推荐）；取值范围：（0.1, 1.0）
            "steps": 4,  # 生成图像的步数；推理步数 ，决定输出图像精细程度，过高会导致处理时长较长；默认值：4；取值范围：[1, 8]
            "seed": -1,  # 随机种子；默认：-1（随机）
            "controlnet_conditioning_scale": 1,
            # "return_url": True,
            # "width": 1024,  # 控制生成图的宽
            # "height": 1024,  # 控制生成图的高 ，建议1024；取值范围：[512, 2048]
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "logo_text_content": ""
            }
        }
        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in text_seed_edit_2, will escape.")

        # print(form)

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        save_and_log(prompt, input_data, result, output_path, other_out_keys=["vlm_result"])

        whole_result["output_images"] = image_handler.get_result_image(result)
        whole_result["vlm_result"] = result.get("vlm_result", "")

        print(f"Used [image_text_seed_edit_2] over.")
        return whole_result

    def inpainting_eraser(self, input_data, mask_data, output_path=None, params=None):
        '''图mask局部涂抹消除'''
        print(f"\n===\nYou are using [inpainting_eraser]...")
        prompt = ""
        input_image_base64 = image_handler.image_data_to_base64(input_data)
        mask_image_base64 = image_handler.image_data_to_base64(mask_data)
        # print(type(input_image_base64))
        # print(type(mask_image_base64))

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/inpainting_eraser/{time_handler.time_string_now()} - {tail}.jpg"

        form = {
            "binary_data_base64": [
                input_image_base64,
                mask_image_base64
            ],
            "req_key": "i2i_inpainting",
            "scale": 7,  # 7 [1, 20]，影响文本描述的程度
            "seed": 0,
            "steps": 30,  # 30 采样步数，生成图像的精细程度，越大效果可能更好，但相应的耗时会剧增
            "dilate_size": 15,  # mask膨胀半径，默认值15
            "strength": 0.8,  # 0.8 取值范围(0.1, 1.0)，越小越接近原图，越大越接近文本控制，如果设成0就和原图一模一样
            "quality": "M",  # 质量参数，默认为M。H，质量最高，速度稍慢；M，质量中等，速度一般 L；质量较低，速度最快
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "logo_text_content": ""
            }
        }
        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in inpainting_eraser, will escape.")
        # print(form.keys())

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")
        # print(result.get("image_urls"))

        whole_result = {
            "output_images": image_handler.get_result_image(result)
        }
        save_and_log(prompt, input_data, result, output_path)

        print(f"Used [inpainting_eraser] over.")
        return whole_result

    def inpainting_edit(self, prompt, input_data, mask_data, output_path=None, params=None):
        '''图mask局部涂抹重绘'''
        print(f"\n===\nYou are using [inpainting_edit]...")
        input_image_base64 = image_handler.image_data_to_base64(input_data)
        mask_image_base64 = image_handler.image_data_to_base64(mask_data)
        # print(type(input_image_base64))
        # print(type(mask_image_base64))

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/inpainting_edit/{time_handler.time_string_now()} - {tail}.jpg"

        form = {
            "binary_data_base64": [
                input_image_base64,
                mask_image_base64
            ],
            "custom_prompt": prompt,
            "req_key": "i2i_inpainting_edit",
            "scale": 5,  # 5 [1, 20]，影响文本描述的程度
            "seed": -1,
            "steps": 25
        }
        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in inpainting_edit, will escape.")
        # print(form.keys())

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")
        # print(result.get("image_urls"))

        whole_result = {
            "output_images": image_handler.get_result_image(result)
        }
        save_and_log(prompt, input_data, result, output_path)

        print(f"Used [inpainting_edit] over.")
        return whole_result

    def outpainting(self, prompt, input_path, output_path=None, use_type="ratio", ratio_info=None, canvas_info=None):
        '''扩图'''
        print(f"\n===\nYou are using [outpainting] with type {use_type}...")
        image_base64 = image_handler.image_data_to_base64(input_path)

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/outpainting/{time_handler.time_string_now()} - {tail}.jpg"

        form = dict()
        # // 使用比例
        if use_type == "ratio":
            form = {
                "req_key": "i2i_outpainting",
                "custom_prompt": prompt,  # 控制在100中文字/英文单词以内，超出部分对生成效果影响较小，此字段会过审核
                "binary_data_base64": [
                    image_base64
                ],
                "scale": 0,  # 7.0 [1, 20] 影响文本描述的程度
                "seed": 0,  #
                "steps": 30,  # 采样步数，生成图像的精细程度，越大效果可能更好，但相应的耗时会剧增
                "strength": 0.8,  # 0.8 [0.1,1.0]，越小越接近原图，越大越接近文本控制，如果设成0就和原图一模一样
                "top": 0.1,  # 0.1 (0,1]，向上扩展比例，暂定最大扩展单边1倍
                "bottom": 0.1,  # (0,1]，向下扩展比例，暂定最大扩展单边1倍
                "left": 0.1,  # 向左扩展比例，暂定最大扩展单边1倍
                "right": 0.1,  # 0.1 (0,1]，向右扩展比例，暂定最大扩展单边1倍
                "max_height": 1920,  # 最大输出高度，在扩图处理后resize到指定尺寸进行兜底
                "max_width": 1920,  # 最大输出宽度，在扩图处理后resize到指定尺寸进行兜底
                "logo_info": {
                    "add_logo": False,
                    "position": 0,
                    "language": 0,
                    "logo_text_content": ""
                }
            }
            if ratio_info:
                for k, v in ratio_info.items():
                    if k in form:
                        form[k] = v
                    else:
                        print(f"[ERROR]: {k} parameter not in outpainting for ratio type, will escape.")
        # // 使用画布
        elif use_type == "canvas":
            assert canvas_info, f"[ERROR]: use canvas but no canvas info in outpainting."
            mask_path = canvas_info.get("canvas_path")
            mask_base64 = image_handler.image_data_to_base64(mask_path)

            form = {
                "req_key": "i2i_outpainting",
                "prompt": prompt,
                "binary_data_base64": [
                    image_base64,
                    mask_base64
                ],
                "scale": 7,
                "seed": -1,
                "steps": 30,
                "strength": 0.8,
                "max_height": 1920,
                "max_width": 1920,
            }
            for k, v in canvas_info.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in outpainting for canvas type, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        other_exist_info = dict()
        if ratio_info:
            other_exist_info = ratio_info
        elif canvas_info:
            other_exist_info = canvas_info

        whole_result = {
            "output_images": image_handler.get_result_image(result)
        }
        save_and_log(prompt, input_path, result, output_path, other_exist_info=other_exist_info)

        print(f"Used [outpainting] over.")
        return whole_result

    def image_to_image(self, prompt, input_data, output_path=None, controlnet_data=None, style_data=None, params=None):
        '''垫图/图mask风格迁移'''
        print(f"\n===\nYou are using [image_to_image]...")
        image_base64 = image_handler.image_data_to_base64(input_data)

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/image_to_image/{time_handler.time_string_now()} - {tail}.jpg"

        form = {
            "req_key": "i2i_xl_sft",  # response里有英文
            "binary_data_base64": [
                image_base64
            ],
            # "image_urls": [
            #     "https://xxx"
            # ],
            "prompt": prompt,
            "seed": -1,
            "ddim_steps": 20,  # 默认20，1~50
            "scale": 7.0,  # 文本影响程度， 1~30
            # "etta_args": {
            #     "binary_data_index": 1
            # },
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 2,
                "language": 0,
                "opacity": 0.3,
                "logo_text_content": ""
            }
        }

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in image_to_image, will escape.")

        idx = 0
        if controlnet_data:  # 实体控制可以有多个图
            if isinstance(controlnet_data, dict):
                controlnet_data = [controlnet_data]
            for inner_control_data in controlnet_data:
                controlnet_base64 = image_handler.image_data_to_base64(inner_control_data.get("controlnet_path"))
                form["binary_data_base64"].append(controlnet_base64)
                controlnet_args = {
                    "type": inner_control_data.get("type", "canny"),
                    # controlnet保持构图的方案，canny轮廓边缘/depth景深/pose人物姿态；type=canny时输出的第二张图是图片轮廓
                    "strength": inner_control_data.get("strength", 0.8),  # [0.0, 1.0] controlnet强度, 为0的时候基本没有物体参考
                    "binary_data_index": idx + 1  # binary_data图片的下标，取值范围：[0, len(binary_data) - 1]
                }
                if not form.get("controlnet_args", None):
                    form["controlnet_args"] = []
                form["controlnet_args"].append(controlnet_args.copy())

                idx += 1

        if style_data:  # 参考风格只能有一个图
            style_base64 = image_handler.image_data_to_base64(style_data.get("style_path"))
            form["binary_data_base64"].append(style_base64)
            style_reference_args = {
                "id_weight": style_data.get("id_weight", 0.2),  # ID保持的作用是人脸保持，人脸数据来源于binary_data[0], [0.0, 1.0]
                "style_weight": style_data.get("style_weight", 1.0),  # [0.0, 1.0] 	风格迁移的强度
                "binary_data_index": idx + 1  # 风格迁移的作用是控制输入图和风格参考图的相似性，风格参考图从binary_data[binary_data_index] 读取
            }
            form["style_reference_args"] = style_reference_args

            idx += 1

        whole_result = {
            "output_images": list(),
            "prompt": ""
        }

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result["output_images"] = image_handler.get_result_image(result)
        whole_result["prompt"] = result.get("prompt")

        save_and_log(prompt, input_data, result, output_path)

        print(f"Used [image_to_image] over.")
        return whole_result

    def image_to_image2(self, prompt, input_data, output_path=None, controlnet_data=None, params=None):
        '''基于字节跳动高美感2.0模型的可控图生图模型，可参考输入图片的轮廓边缘、景深、人物姿态特征进行出图，出图效果更精美。
        https://www.volcengine.com/docs/6791/1424608'''
        print(f"\n===\nYou are using [image_to_image2]...")
        image_base64 = image_handler.image_data_to_base64(input_data)

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/image_to_image2/{time_handler.time_string_now()} - {tail}.jpg"

        form = {
            "req_key": "high_aes_scheduler_svr_controlnet_v2.0",
            "binary_data_base64": [
                image_base64
            ],
            # "image_urls": [
            #     "https://xxx"
            # ],
            "prompt": prompt,
            "model_version": "general_controlnet_v2.0",
            "seed": -1,
            "scale": 3.0,  # 影响文本描述的程度; float 默认值：3.0; 取值范围：[1, 30]
            "ddim_steps": 16,  # 生成图像的步数; 默认值：16; 取值范围：[1, 50]; 过高可能会超时
            "use_rephraser": True,  # 开启中文prompt扩写; 默认值：true
            "use_sr": True,  # true：文生图+AIGC超分; false：文生图; 默认值：true
            "sr_seed": -1,  # 超分模型随机种子，-1为不随机种子；其他为指定随机种子，当use_sr开启时有效; 默认值：-1
            "sr_strength": 0.4,  # 只在超分模型生效; 默认值：0.4; 取值范围：[0.0, 1.0]
            "sr_scale": 3.5,  # 在超分模型上，影响文本描述的程度； 默认值：3.5； 取值范围：[1, 30]
            "sr_steps": 10,  # 超分模型生成图像的步数； 默认值：10； 取值范围：[1, 50]

            # "etta_args": {
            #     "binary_data_index": 1
            # },
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 2,
                "language": 0,
                "opacity": 0.3,
                "logo_text_content": ""
            }
        }

        idx = 0
        if controlnet_data:  # 实体控制可以有多个图
            if isinstance(controlnet_data, dict):
                controlnet_data = [controlnet_data]
            for inner_control_data in controlnet_data:
                controlnet_base64 = image_handler.image_data_to_base64(inner_control_data.get("controlnet_path"))
                form["binary_data_base64"].append(controlnet_base64)
                controlnet_args = {
                    "type": inner_control_data.get("type", "canny"),
                    # controlnet保持构图的方案，canny轮廓边缘/depth景深/pose人物姿态；type=canny时输出的第二张图是图片轮廓
                    "strength": inner_control_data.get("strength", 0.8),  # [0.0, 1.0] controlnet强度, 为0的时候基本没有物体参考
                    "binary_data_index": idx + 1  # binary_data图片的下标，取值范围：[0, len(binary_data) - 1]
                }
                if not form.get("controlnet_args", None):
                    form["controlnet_args"] = []
                form["controlnet_args"].append(controlnet_args.copy())

                idx += 1

        whole_result = {
            "output_images": list(),
            "prompt": ""
        }

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result["output_images"] = image_handler.get_result_image(result)
        whole_result["prompt"] = result.get("prompt")

        save_and_log(prompt, input_data, result, output_path)

        print(f"Used [image_to_image2] over.")
        return whole_result

    def character_preservation(self, prompt, input_data, output_path=None, params=None):
        '''角色特征保持'''
        print(f"\n===\nYou are using [character_preservation]...")
        image_base64 = image_handler.image_data_to_base64(input_data)

        if not output_path:
            tail = prompt[:20].replace("/", "_\\")
            output_path = f"{self.output_images_path}/character_preservation/{time_handler.time_string_now()} - {tail}.jpg"

        form = {
            "req_key": "high_aes_ip_v20",
            "binary_data_base64": [image_base64],
            # "image_urls": ["https://xxx"],
            "prompt": prompt,
            "desc_pushback": True,  # 针对输入图内容进行反推，可使生成图片效果更稳定
            "seed": -1,
            "scale": 3.5,  # 3.5 [1, 10]
            "ddim_steps": 9,  # 9 [1, 200]
            "width": 512,  # 512 [256, 768]
            "height": 512,  # [256, 768]
            "cfg_rescale": 0.7,
            "ref_ip_weight": 0.7,  # 0.7 [0, 1] 参考图主体外观的权重，越大生成结果和参考图中主体的相似度越高
            "ref_id_weight": 0.36,  # [0, 1] 推荐取值范围[0.2, 0.4] 参考图人脸特征的权重，越大生成结果和参考图中人脸的相似度越高
            "use_sr": True,  # 文生图+AIGC超分
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "opacity": 0.3,
                "logo_text_content": "这里是明水印内容"
            }
        }

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in character_preservation, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result = {
            "output_images": image_handler.get_result_image(result),
        }

        save_and_log(prompt, input_data, result, output_path)

        print(f"Used [character_preservation] over.")
        return whole_result

    def clearer(self, input_data, output_path=None, params=None):
        '''清晰化'''
        print(f"\n===\nYou are using [clearer]...")
        image_base64 = image_handler.image_data_to_base64(input_data)

        # print(image_base64)

        print(params)
        result_format = "png" if params.get("result_format", 0) == 0 else "jpeg"

        if not output_path:
            output_path = f"{self.output_images_path}/clearer/{time_handler.time_string_now()}.{result_format}"

        form = {
            "req_key": "lens_nnsr2_pic_common",
            "binary_data_base64": [
                image_base64
            ],
            # "image_urls": ["https://xxx"],
            "model_quality": "MQ",  # 选取哪种模型进行超分，LQ适用于低质量图片，HQ适用于高质量图片。推荐值: "MQ", 取值范围：["HQ", "MQ", "LQ" ]，
            "result_format": 0,  # 0 代表结果图片为png格式，1 代表结果图片为jpeg格式，默认值：0，取值范围：[0, 1]
            "jpg_quality": 95,  # 值越高代表生成jpg图片的质量越高, 默认值：95, 取值范围：[0, 100]
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 2,
                "language": 0,
                "opacity": 0.3,
                "logo_text_content": "这里是明水印内容"
            }
        }

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in clearer, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result = {
            "output_images": image_handler.get_result_image(result),
        }

        save_and_log(None, input_data, result, output_path)

        print(f"Used [clear] over.")
        return whole_result

    def clearer_lqir(self, input_data, output_path=None, params=None):
        '''图像增强
        https://www.volcengine.com/docs/6793/145398
        '''
        print(f"\n===\nYou are using [clearer_lqir]...")
        image_base64 = image_handler.image_data_to_base64(input_data)

        # print(image_base64)

        result_format = "png" if params.get("result_format", 0) == 0 else "jpeg"

        if not output_path:
            output_path = f"{self.output_images_path}/clearer_lqir/{time_handler.time_string_now()}.{result_format}"

        form = {
            "req_key": "lens_lqir",
            "binary_data_base64": [image_base64],
            # "image_urls": ["https://xxx"],
            "resolution_boundary": "4k",  # 图片分辨率 原分辨率低于选项，内部走超分，原分辨率高于选项，内部走模糊；'"144p": [192, 144]; "240p": [320, 240]; "360p": [480, 360]; "480p": [640, 480]; "540p": [960, 540]; "720p": [1280, 720]; "1080p": [1920, 1080]; "2k": [2048, 1152]'
            "enable_hdr": False,  # 是否开启hdr能力
            "enable_wb": False,  # 是否开启白平衡能力
            "result_format": 1,  # 0 代表结果图片为png格式；1 代表结果图片为jpeg格式
            "jpg_quality": 95,  # 值越高，代表生成jpg图片的质量越高
            "hdr_strength": 1.0,  # 值越高，代表HDR效果越明显
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "opacity": 0.3,
                "logo_text_content": ""
            }
        }

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in clearer_lqir, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result = {
            "output_images": image_handler.get_result_image(result),
        }

        save_and_log(None, input_data, result, output_path)

        print(f"Used [clearer_lqir] over.")
        return whole_result


    def picture_seg(self, input_data, output_path=None, params=None, save_mask=False):
        '''抠图
        https://www.volcengine.com/docs/6793/1330693
        '''
        print(f"\n===\nYou are using [picture_seg]...")
        image_base64 = image_handler.image_data_to_base64(input_data)
        # print(image_base64)

        if not output_path:
            output_path = f"{self.output_images_path}/picture_seg/{time_handler.time_string_now()}.png"
        form = {
            # "image_urls": ["https://xxx"],
            "binary_data_base64": [
                image_base64
            ],
            "only_mask": 4,  # 0（默认）: 返回裁剪出主体区域的BGRA透明图片；1: 返回原图大小Mask分割图；2: 返回裁剪出主体区域的BGR前景图 叠加 方形纯色背景
            # 3: 返回原图大小的BGRA透明前景图；4: 返回原图大小的BGRA透明前景图+原图大小mask两个产物；
            # 如使用0, 3, 4等需要返回透明底图的方式，需配合使用rgb=[-1, -1, -1]
            "refine_mask": 0,  # 0：不对边缘增强；1：对边缘增强（matting lite 更快)；2：对边缘增强（matting large)（需精细化分割推荐开启该参数）
            # 默认值：0；注：参数设为2时，且4通道返回结果时，将会对部分背景区域的rgb值设置为0，以减少产物体积
            "req_key": "saliency_seg",
            "logo_info": {
                "add_logo": False,
                "position": 1,
                "language": 0,
                "opacity": 0.3,
                "logo_text_content": ""
            },
            "rgb": [-1, -1, -1]  # 建议值，透明底图
        }

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in picture_seg, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result = {
            "output_images": image_handler.get_result_image(result, images_count=1 if not save_mask else 2),
            "contours_point": result.get("contours_point")
        }

        save_and_log(None, input_data, result, output_path, save_images_count=1 if not save_mask else 2)

        print(f"Used [picture_seg] over.")
        return whole_result

    def product_repaint(self, positive_prompt, input_data, output_path=None, mask_data=None, ref_data=None,
                        composition_data=None, light_data=None, params=None):
        '''AI营销商品图
        https://www.volcengine.com/docs/6791/1400096
        https://bytedance.larkoffice.com/docx/Y8g9dsEgmoKl6Ixz1bpcMNHBnyg

        输入换背景prompt，原图，遮罩图（可选），参考图（可选），光照（文本/预设[8方位]/蒙版光照），构图选择（原图默认，自动构图，手动构图）
        '''
        print(f"\n===\nYou are using [product_repaint]...")
        # image_base64 = image_handler.image_data_to_base64(input_data)
        # image_url = image_handler.base64_to_remote_url(image_base64)
        image_url = image_handler.image_data_to_remote_url(input_data)
        # image_url = "https://static5.yingsaidata.com/bfaa3689-39e3-43d2-9400-5d3df8d72b63.png"

        if not output_path:
            output_path = f"{self.output_images_path}/product_repaint/{time_handler.time_string_now()}.jpg"
        form = {
            "req_key": "img2img_e_commerce_style",
            "product_image_input": image_url,  # 产品图URL，可输入任意图片格式，支持透明底PNG
            "product_alpha_switch": True,  # （不用变）自动识别透明通道，开启后优先使用输入图的透明通道，未识别到透明图层时，自动使用火山侧自动抠主体功能
            "seg_prompt": "",  # 自动扣图-指定物体；默认就会自动抠出主体，一般无需输入。图片内有多个不同的物体时，必要时可通过提示抠出需要的物体

            # 生图参数
            "product_weight": 0.85,  # 产品还原强度。范围：0~1.3 （注意：超过1.3会报错）；默认已开启光影变化，产品还原程度。越低越容易受氛围、环境的光影影响
            "seed": -1,  # 随机种子
            "positive_prompt": positive_prompt,
            "fixed_positive_prompt": params.get("fixed_positive_prompt",
                                                "masterpiece,realistic,photography,product,8K,highres,best quality,bright,ultra detail,high detail,foreground,correct projection,"),
            "negative_prompt": params.get("negative_prompt",
                                          "(human,animal,person,character,girl,boy,old,alien,skeleton,figure,doll,bird:1.1),noise,film grain,dirty,caustics,orange ray,magic,fantasy,fog,outline,simple line,cartoon,anime,comic,"),
            "fixed_negative_prompt": params.get("fixed_negative_prompt",
                                                "(nsfw:1.1),(worst quality,low quality:1.1),jpeg,jpg,normal quality,low resolution,lowres,watermark,wrong lighting,wrong projection,(blurry:1.1),(blurry background:1.2),bokeh,(Depth of field:1.2),dof,melt,(blur:1.2),blur background,illogical,horror, american,logo,text,word,title,headline,"),

            # 其它功能（保底功能）
            "product_safe_switch": False,  # 产品还原度-安全模式；默认：false；开启后，强制还原产品细节。消除产品的任何光影变化。（与环境融合度有所下降）
            "product_edge_weight": 0,  # 产品与环境分离程度；默认：0.0；范围：0~1（注意：数值过高时，高概率让产品悬空）；如果发现产品边缘有畸形，或有异常粘连时。可以调到0.1~0.2
            "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "opacity": 1,
                "logo_text_content": "这里是明水印内容"
            },
        }
        if mask_data:  # 遮罩
            mask_base64 = image_handler.image_data_to_base64(mask_data.get("mask_image_input", ""))
            mask_url = image_handler.base64_to_remote_url(mask_base64)
            form.update({
                "mask_image_switch": True,  # 手动上传mask功能开关，上传mask后需要手动开启，默认为自动抠产品图+识别产品图的透明通道; 默认：false
                "mask_invert_switch": mask_data.get("mask_invert_switch", True),  # 遮罩图片反转，默认开启，反转输入遮罩图; 默认：true
                "mask_image_input": mask_url,  # 遮罩蒙版图片
            })
        else:
            form["mask_image_switch"] = False

        if ref_data:  # 参考图
            ref_base64 = image_handler.image_data_to_base64(ref_data.get("ref_image_input", ""))
            ref_url = image_handler.base64_to_remote_url(ref_base64)
            form.update({
                "ref_switch": True,  # 参考图功能开关
                "ref_image_input": ref_url,  # 参考图
                # "ref_image_input": "https://xxx",
                "ref_weight": ref_data.get("ref_weight", 0.75),  # 参考图强度，0~2（注意：保持在0~1之间最佳）
                "ref_end_at": ref_data.get("ref_end_at", 0.75)
                # 参考图引导结束时间；范围：0~1；参考图引导的结束时间，1=完整引导，0.5=生成到50%时结束引导，让模型自由发挥，获得更好的细节
            })
        else:
            form["ref_switch"] = False

        if composition_data:
            composition_type = composition_data.get("composition_type", "origin")
        else:
            composition_type = "origin"  # 默认按原图
            composition_data = dict()
        if composition_type == "origin":
            form.update({
                "longer_side": composition_data.get("longer_side", 1600)  # 输出分辨率，默认：1600；按产品输入图的长边缩放分辨率，保持原图比例，
                # （推荐输入能被8整除的数，例如：768，1024，1280，1440，1600，2000···）仅影响输出分辨率，不影响生图过程
            })
        elif composition_type == "auto":
            form.update({
                "auto_composition_switch": True,  # 自动构图，默认：false 【默认将产品置中】
                "canvas_width": composition_data.get("canvas_width", 1000),  # 画布宽度（像素）
                "canvas_height": composition_data.get("canvas_height", 1000),  # 画布高度（像素）
                "auto_offset_x": composition_data.get("auto_offset_x", 50),  # x轴偏移（百分比）
                "auto_offset_y": composition_data.get("auto_offset_y", 50),  # y轴偏移（百分比）
                "auto_scale": composition_data.get("auto_scale", 0.7),  # scale大小（百分比）
            })
        elif composition_type == "manual":
            form.update({
                "manual_composition_switch": True,
                "canvas_width": composition_data.get("canvas_width", 1000),  # 画布宽度（像素）,（仅影响输出分辨率，不影响生图过程）
                "canvas_height": composition_data.get("canvas_height", 1000),  # 画布高度（像素）,（仅影响输出分辨率，不影响生图过程）
                "offset_x": composition_data.get("offset_x", 0),  # x轴偏移（像素）
                "offset_y": composition_data.get("offset_y", 0),  # y轴偏移（像素）
                "crop_prodcut_switch": composition_data.get("crop_prodcut_switch", True),
                # 自动裁切至商品大小；默认：true (手动构图开启时，该字段才生效可选）；true：裁剪至商品大小；false：保持输入图片大小
            })

        if light_data:  # 默认没有光源设置
            light_type = light_data.get("composition_type", "preset")
            if light_type == "preset":
                form.update({
                    "preset_light_switch": True,  # 预设光源开关
                    "light_position": light_data.get("light_position", "Top Left Light"),
                    # 预设光源类型， 左光源："Left Light"；右光源："Right Light"；顶光源："Top Light"；底光源："Bottom Light"；
                    # 左上光源："Top Left Light" 【开启预设光后默认】；# 右上光源："Top Right Light"；
                    # 左下光源："Bottom Left Light"；右下光源："Bottom Right Light"
                })
            elif light_type == "upload":
                light_base64 = image_handler.image_data_to_base64(light_data.get("light_image_input", ""))
                light_url = image_handler.base64_to_remote_url(light_base64)
                form.update({
                    "upload_light_switch": True,  # 手动上传光源开关
                    "light_image_input": light_url,  # 手动上传光源图片URL
                })

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in product_repaint, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        print(response)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result = {
            "output_images": image_handler.get_result_image(result),
        }

        save_and_log(positive_prompt, input_data, result, output_path)

        print(f"Used [product_repaint] over.")
        return whole_result

    def image_correction(self, input_data, output_path=None):
        '''图片方位矫正(生成图片会变糊）
        https://www.volcengine.com/docs/6793/145404
        '''
        print(f"\n===\nYou are using [image_correction]...")
        image_base64 = image_handler.image_data_to_base64(input_data)
        # print(image_base64)

        if not output_path:
            output_path = f"{self.output_images_path}/image_correction/{time_handler.time_string_now()}.png"
        form = {
            "req_key": "image_correction",
            # "image_urls": ["https://xxx"],
            "binary_data_base64": [
                image_base64
            ]
        }

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.image_correction(form)
        print(f"Response: {cut_print(response)}")

        result = response.get("data")

        trans_points = [float(x) for x in result.get("trans_points")]
        trans_points_three = np.array([trans_points[:3], trans_points[3:6], trans_points[6:]])

        image = image_handler.base64_to_image(image_base64)
        image_cv = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
        trans_image_cv = cv2.warpPerspective(image_cv, trans_points_three, dsize=image.size)  # 透视变换投影
        trans_image = Image.fromarray(cv2.cvtColor(trans_image_cv, cv2.COLOR_BGR2RGB))
        result["binary_data_base64"] = [image_handler.image_data_to_base64(trans_image)]

        whole_result = {
            "output_images": [image, trans_image],
        }

        save_and_log(None, input_data, result, output_path)

        print(f"Used [image_correction] over.")
        return whole_result

    def dressing(self, model_data, garment_data=None, protect_mask_data=None, output_path=None, params=None):
        '''图片换装
        https://www.volcengine.com/docs/85128/1462743
        输入模特图（模特保护区域图）、服装图（当前仅支持配置一件服装，可以是上衣、裤子、鞋子或帽子其中之一），返回服饰模特上身效果。
        '''
        print(f"\n===\nYou are using [dressing]...")
        model_image_url = image_handler.image_data_to_remote_url(model_data)
        garment_image_url = image_handler.image_data_to_remote_url(garment_data)

        if not output_path:
            output_path = f"{self.output_images_path}/dressing/{time_handler.time_string_now()}.jpg"
        form = {
            "req_key": "dressing_diffusion",
            "model": {
                "id": "1",
                "url": model_image_url
            },
            "garment": {
                "id": "1",
                "data": [
                    {
                        "url": garment_image_url
                    }
                ]
            },
            "do_sr": True,  # 是否对结果进行超分处理 默认值：true
            "seed": -1,  # 随机种子参数，默认为-1，表示系统随机生成seed 默认值：-1
            "keep_head": True,  # 是否保持模特原图的头（包括发型） 默认值：true
            "keep_hand": True,  # 是否保持模特原图的手 默认值：true
            "keep_foot": True,  # 是否保持模特原图的足 默认值：true
            "num_steps": True,  # 模型推理步数，和算法效果、处理时间相关 默认值：50 取值范围： [25, 50]
            "keep_upper": False,  # 是否保持模特原图的上装 默认值：false
            "keep_lower": False,  # 是否保持模特原图的下装 默认值：false

            "tight_mask": "loose",  # 模特图遮挡区域范围 默认值："loose" 支持类型：["tight", "loose", "bbox"]
            # 说明："tight": 上窄下窄 "loose": 上窄下宽（默认） "bbox": 上宽下宽
            "p_bbox_iou_ratio": 0.3,  # 当画面有多个人时，每个人的bbox与主体相交的比例；默认值：0.3；取值范围：[0.1, 0.5]
            "p_bbox_expand_ratio": 1.1,  # bbox在inference时扩大的比例；默认值：1.1；取值范围：[1.0, 1.5]
            "max_process_side_length": 1920,  # 当输入图像时，最大的边长若超过该数值，会先resize到图像到该最大边长；默认值：1920；取值范围：[1080, 4096]

            # "return_url": True,
            "logo_info": {
                "add_logo": False,
                "position": 0,
                "language": 0,
                "logo_text_content": ""
            }
        }
        if protect_mask_data:
            # PNG格式, 保护区域为255 白，非保护区域为0 黑
            # 上传时需要同步修改keep_head/keep_hand/keep_foot参数
            # 若同时上传protect_mask_url和keep_head/keep_hand/keep_foot字段，则取并集

            protect_mask_url = image_handler.image_data_to_remote_url(protect_mask_data)
            form["model"]["protect_mask_url"] = protect_mask_url

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in text_seed_edit_2, will escape.")

        print(f"Request: {cut_print_form(form)}")
        response = self.visual_service.cv_process(form)
        # print(response)
        print(f"Response: {cut_print(response)}")
        result = response.get("data")

        whole_result = {
            "output_images": image_handler.get_result_image(result),
        }

        save_and_log("", model_data, result, output_path, other_exist_info={"form": cut_print_form(form)})

        print(f"Used [dressing] over.")
        return whole_result

    def text_to_video_s20_pro(self, prompt, output_path=None, params=None):
        '''文生视频
        https://www.volcengine.com/docs/85621/1538636
        '''
        print(f"\n===\nYou are using [text_to_video_s20_pro]...")
        URL = "https://visual.volcengineapi.com?Action=CVSync2AsyncSubmitTask&Version=2022-08-31"

        if not output_path:
            output_path = f"{self.output_videos_path}/text_to_video/S20-pro/{time_handler.time_string_now()}.mp4"

        form = {
            "req_key": "jimeng_vgfm_t2v_l20",
            "prompt": prompt,  # 生成视频的的提示词，支持中英文，150字符以内，prompt书写参考上方描述
            "seed": -1,  # 随机种子，作为确定扩散初始状态的基础，默认 - 1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致.
            # [-1~2 ^ 64 - 1]，默认值：-1   -1时，会随机生成一个种子。其他即为正常取值。
            "aspect_ratio": "16:9"  # 生成视频的尺寸，从以下中选择，会对应不同的分辨率：'16:9'：1280×720（默认） '9:16' ：720×1280
            # '1:1' ： 960×960 '4:3'：960×720 '3:4' ： 720×960 '21:9' ：1680×720
        }
        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in text_to_video_s20_pro, will escape.")

        print(f"Request1: {cut_print_form(form)}")
        response = self.visual_service.cv_sync2async_submit_task(form)
        # res = requests.post(URL, data=json.dumps(form))
        # response = res.json()
        print(response)
        print(f"Response1: {cut_print(response)}")
        result = response.get("data")

        task_id = result.get("task_id")
        print(f"TASK_ID: {task_id}")

        # task_id = "17484170879463117490"

        video_url = ""
        start_time = time.time()
        try_cnt = 1
        while not video_url:
            print(f"trying {try_cnt} ...")
            if time.time() - start_time < 1000:
                form2 = {
                    "req_key": "jimeng_vgfm_t2v_l20",
                    "task_id": task_id
                }
                print(f"Request2: {cut_print_form(form2)}")
                response2 = self.visual_service.cv_sync2async_get_result(form2)
                # res2 = requests.post(URL, data=json.dumps(form2))
                # response2 = res2.json()
                print(response2)
                print(f"Response2: {cut_print(response2)}")
                result2 = response2.get("data")
                if result2.get("video_url"):
                    video_url = result2.get("video_url")
                    break
                else:
                    time.sleep(10)
                    try_cnt += 1

        # resp_data, video_url
        whole_result = {
            "output_video": video_url,
            "video_url": video_url,
        }

        save_and_log("", "", result2, output_path, other_exist_info={"form": cut_print_form(form2)})

        print(f"Used [text_to_video_s20_pro] over.")
        return whole_result

    def image_to_video_s20_pro(self, prompt, image_data1, image_data2=None, output_path=None, params=None):
        '''图生视频
        https://www.volcengine.com/docs/85621/1544774
        '''
        print(f"\n===\nYou are using [image_to_video_s20_pro]...")

        if not output_path:
            output_path = f"{self.output_videos_path}/image_to_video/S20-pro/{time_handler.time_string_now()}.mp4"

        image_url1 = image_handler.image_data_to_remote_url(image_data1)
        image_url2 = ""
        if image_data2:
            image_url2 = image_handler.image_data_to_remote_url(image_data2)

        form = {
            "req_key": "jimeng_vgfm_i2v_l20",
            "prompt": prompt,  # 生成视频的的提示词，支持中英文，150字符以内，prompt书写参考上方描述
            "image_urls": [
                image_url1
            ],
            "seed": -1,  # 随机种子，作为确定扩散初始状态的基础，默认 - 1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致.
            # [-1~2 ^ 64 - 1]，默认值：-1   -1时，会随机生成一个种子。其他即为正常取值。
            "aspect_ratio": "16:9"  # 生成视频的尺寸，从以下中选择，会对应不同的分辨率：'16:9'：1280×720（默认） '9:16' ：720×1280
            # '1:1' ： 960×960 '4:3'：960×720 '3:4' ： 720×960 '21:9' ：1680×720
        }
        if image_url2:
            form["image_urls"].append(image_url2)

        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v
                else:
                    print(f"[ERROR]: {k} parameter not in image_to_video_s20_pro, will escape.")

        print(f"Request1: {cut_print_form(form)}")
        response = self.visual_service.cv_sync2async_submit_task(form)
        # res = requests.post(URL, data=json.dumps(form))
        # response = res.json()
        print(response)
        print(f"Response1: {cut_print(response)}")
        result = response.get("data")

        task_id = result.get("task_id")
        print(f"TASK_ID: {task_id}")

        # task_id = "17484170879463117490"

        video_url = ""
        start_time = time.time()
        try_cnt = 1
        while not video_url:
            print(f"trying {try_cnt} ...")
            if time.time() - start_time < 1000:
                form2 = {
                    "req_key": "jimeng_vgfm_i2v_l20",
                    "task_id": task_id
                }
                print(f"Request2: {cut_print_form(form2)}")
                response2 = self.visual_service.cv_sync2async_get_result(form2)
                # res2 = requests.post(URL, data=json.dumps(form2))
                # response2 = res2.json()
                print(response2)
                print(f"Response2: {cut_print(response2)}")
                result2 = response2.get("data")
                if result2.get("video_url"):
                    video_url = result2.get("video_url")
                    break
                else:
                    time.sleep(10)
                    try_cnt += 1

        # resp_data, video_url
        whole_result = {
            "output_video": video_url,
            "video_url": video_url,
        }

        save_and_log("", "", result2, output_path, other_exist_info={"form": cut_print_form(form2)})

        print(f"Used [image_to_video_s20_pro] over.")
        return whole_result


class TEST(unittest.TestCase):
    jimeng_api = JiMengAPI()

    def test_text_to_image(self):
        prompt = "线条小狗表情包"
        self.jimeng_api.text_to_image(prompt)

    def test_image_text_seed_edit(self):
        prompt = "将logo换成蓝色、白色的高科技元素的颜色。背景从上到下是白色、浅蓝色的简约的渐变色，右边是logo，logo里有高科技的数据流等元素，背景下方有万维网、电脑、人物、万物互联的元素、机器人等高科技的IT元素的轮廓点缀。"
        input_path = "../data/source_images/营赛洞见logo_黑底.png"

        self.jimeng_api.image_text_seed_edit(prompt, input_path, output_path=None)

    def test_inpainting_eraser(self):
        input_path = "../data/source_images/雅诗兰黛 抠图 蓝底.png"
        mask_path = "../data/source_images/雅诗兰黛 mask 白底.png"

        self.jimeng_api.inpainting_eraser(input_path, mask_path, output_path=None)

    def test_inpainting_edit(self):
        prompt = "小清新风格。商品展台背景图。背景是蓝天、白云、山、水，背景中间留白。画面右下方是网格的屏风，下面是大理石的展台，边上有绿植、小雏菊点缀。整体是浅蓝色、白色、浅绿色的色调。"
        input_path = "../data/source_images/雅诗兰黛 抠图 蓝底.png"
        mask_path = "../data/source_images/雅诗兰黛 mask 白底.png"

        self.jimeng_api.inpainting_edit(prompt, input_path, mask_path, output_path=None)

    def test_outpainting(self):
        prompt = ""
        input_path = "../data/source_images/营赛洞见logo_电路纹理.png"
        self.jimeng_api.outpainting(prompt, input_path, output_path=None, use_type="ratio")

        prompt = ""
        input_path = "../data/source_images/营赛洞见logo_电路纹理.png"
        mask_path = "../data/source_images/雅诗兰黛 mask 白底.png"
        canvas_info = {"canvas_path": mask_path}
        self.jimeng_api.outpainting(prompt, input_path, output_path=None, use_type="canvas", canvas_info=canvas_info)

    def test_image_to_image(self):  #
        prompt = "生成国潮的背景。"
        input_path = "../data/source_images/雅诗兰黛 mask 白底.png"
        controlnet_path = "../data/source_images/雅诗兰黛 抠图.png"
        style_path = "../data/source_images/故宫国潮.png"

        # input_path = "../data/test/O logo 冷蓝图案1.png"
        # controlnet_path = "../data/test/3d腾讯云参考图.png"  # 图片有问题？
        # style_path = "../data/test/O logo 冷蓝图案1.png"

        input_path = "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/护肤-可复美1.png"
        controlnet_data = [{
            "controlnet_path": "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/护肤-可复美1 背景黑.png",
            "type": "canny",
            "strength": 1
        }, {
            "controlnet_path": "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/护肤-可复美1.png",
            "type": "depth",
            "strength": 0.1
        }]

        style_data = None

        self.jimeng_api.image_to_image(prompt, input_path, output_path=None,
                                       controlnet_data=controlnet_data,
                                       style_data=style_data)

    def test_character_preservation(self):
        prompt = "小清新风格。商品展台背景图。背景是蓝天、白云、山、水，背景中间留白。画面右下方是网格的屏风，下面是大理石的展台，边上有绿植、小雏菊点缀。整体是浅蓝色、白色、浅绿色的色调。"
        input_path = "../data/source_images/雅诗兰黛 抠图.png"

        self.jimeng_api.character_preservation(prompt, input_path, output_path=None)

    def test_clearer(self):
        input_path = "/Users/admin/Files/评测/文生图/图片/source/O logo 冷蓝图案1.png"

        self.jimeng_api.clearer(input_path, output_path=None)

    def test_picture_seg(self):
        input_path = "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/美食-鲜花蛋糕1.png"
        # self.jimeng_api.picture_seg(input_path, output_path=None, save_mask=False)
        self.jimeng_api.picture_seg(input_path, output_path=None, save_mask=True)

    def test_product_repaint(self):
        # input_path = "/Users/admin/Files/评测/文生图/图片/source/小红书种草文案封图/案例图片/美食-鲜花蛋糕1.png"
        input_path = "https://static5.yingsaidata.com/ab7d47f094c7a546dee91a6e4b1ea9d2.png"
        input_path = "/Users/admin/Downloads/水彩图画风格。背景上方大面积留白，写有文字“雅诗兰黛”、“第七代小棕瓶精华”。画面下方是一瓶打开的雅诗兰黛小棕瓶修复精华，瓶身背后是很大的浅黄色的水滴形状的轮.jpeg"

        prompt = "背景下方是大理石桌面，背景上方是米白色的室内墙面，光影明媚。有可爱的手绘、简约线条的涂鸦简笔画点缀，比如爱心、气球等，最右边有一个手绘的卡通小女孩在趴着看蛋糕。整体是小清新风格。"
        self.jimeng_api.product_repaint(prompt, input_path, output_path=None)

    def test_image_correction(self):
        input_path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/蒂佳婷面膜/叠图4.png"
        image_base64 = image_handler.image_data_to_base64(input_path)
        image = image_handler.base64_to_image(image_base64)
        print(image, image.size, dir(image))
        self.jimeng_api.image_correction(input_path, output_path=None)

    def test_image_text_seed_edit_2(self):
        prompt = "将logo换成蓝色、白色的高科技元素的颜色。背景从上到下是白色、浅蓝色的简约的渐变色，右边是logo，logo里有高科技的数据流等元素，背景下方有万维网、电脑、人物、万物互联的元素、机器人等高科技的IT元素的轮廓点缀。"
        input_path = "/Users/admin/Files/评测/文生图/图片/source/招股书封面/O logo蓝色 黑底.png"

        self.jimeng_api.image_text_seed_edit_2(prompt, input_path, output_path=None)

    def test_dressing(self):
        model_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/春季连衣裙/AI模特/即梦/湖边草地/站着-歪头.jpg"
        garment_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/春季连衣裙/商品图-紫色.jpg"
        self.jimeng_api.dressing(model_path, garment_path)

    def test_video_download(self):
        url = "https://v26-artist.vlabvod.com/f642c74a1b645eb2ccd068ac2bc6cfcf/6826f450/video/tos/cn/tos-cn-v-148450/osBd5fmEOiBJQEDIkBFoSu4DgiNiEAocfbHHsn/?a=4066&ch=0&cr=0&dr=0&er=0&cd=0%7C0%7C0%7C0&br=6911&bt=6911&cs=0&ds=12&ft=5QYTUxhhe6BMyq9lwbkJD12Nzj&mime_type=video_mp4&qs=0&rc=ZmZlOzg8ZThmZTY5ZztnN0BpMzQ5cm05cmh1MzczNDM7M0AzMzVfYzJhNi8xYmBgMWEuYSNlbGVzMmRjZ2JhLS1kNGFzcw%3D%3D&btag=c0000e00008000&dy_q=1746778571&feature_id=7bed9f9dfbb915a044e5d473759ce9df&l=2025050916161177B0D480C4A6DB606CD6"
        res = requests.get(url, stream=True)
        with open(
                '/Users/admin/program/projects/multi_model_api_gradio/data/output_videos/text_to_video/test.mp4',
                'wb') as f:
            for chunk in res.iter_content(chunk_size=10240):
                f.write(chunk)

    def test_text_to_video(self):
        prompt = "昏黄的阳光下，是干枯的垂下的朵朵花朵的近景，随着微风轻轻摇曳 。"
        result = self.jimeng_api.text_to_video(prompt)
