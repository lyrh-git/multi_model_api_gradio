import copy
import json
import time
import unittest
import re
import numpy as np
from PIL import Image

import requests

from ImageHandler import ImageHandler
from TimeHandler import TimeHandler
from VideoHandler import VideoHandler
from jimeng_sdk import JiMengAPI, save_and_log
from fangzhou_sdk import FangzhouAPI
from text_sdk import TextAPI
from volcengine_sdk import VolcengineAPI

from common.logger import setup_logging

time_handler = TimeHandler()
image_handler = ImageHandler()
video_handler = VideoHandler()

logger = setup_logging("diy_sdk__logger")

class DiyAPI:
    def __init__(self):
        self.jimeng_api = JiMengAPI()
        self.fangzhou_api = FangzhouAPI()
        self.text_api = TextAPI()
        self.volcengine_api = VolcengineAPI()

        self.output_images_path = "/Users/admin/program/projects/multi_model_api_gradio/data/output_images/diy/"
        self.output_videos_path = "/Users/admin/program/projects/multi_model_api_gradio/data/output_videos/diy"
    def ai_product_image(self, input_data, output_path=None, params=None):
        '''商品图，图片解读、文生图、AI图抠图、AI图涂抹、商品图抠图、叠图'''
        print(f"\n===\nYou are using [DIY ai_product_image]...")
        start_time = time.time()

        image_base64 = image_handler.image_data_to_base64(input_data)
        image = image_handler.base64_to_image(image_base64)
        width, height = image.size

        if not output_path:
            output_path = f"{self.output_images_path}/ai_product_image/{time_handler.time_string_now()}.jpg"

        # picture_to_text_prompt = "用一段流畅的文字详细描述这张图片。"
        picture_to_text_prompt = "用一段流畅简洁精炼的文字描述这张商品展示图，你需要重点描述这个产品的名称、类型、形状（瓶/罐/枝/根/件/条）、颜色、打开关闭状态、拍摄角度、外部内部结构、位于图片中的位置、颜色浅淡、明暗等，同时需要重点描述背景的展示环境、背景颜色、光影、明暗等。"
        # 用一段流畅简洁精炼的文字描述这张商品展示图，你需要重点描述这个产品的名称、类型、形状（瓶/罐/枝/根/件/条）、颜色、打开关闭状态、拍摄角度、外部内部结构、位于图片中的位置、颜色浅淡、明暗等，同时需要重点描述背景的展示环境、背景颜色、光影、明暗等，你需要特别注意商品的展示方式，比如静置、人物手持等。

        if params and "picture_to_text_prompt" in params:
            picture_to_text_prompt = params["picture_to_text_prompt"]

        result1 = self.fangzhou_api.picture_to_text__fangzhou(input_data, picture_to_text_prompt)
        image_description = result1.get("text")
        print(f"[IMAGE DESCRIPTION]: {image_description}")

        description_to_label_prompt = """这张图是个商品展示图，如果要将这个图作为小红书封面，你需要结合这个图中的产品的类型、特征，为这个图添加一个吸引人的大标题和小标题。然后结合这个图中的产品的类型、格调、形状、颜色，结合展示图的背景环境、背景颜色，设计添加到背景的标题的文字的合适的颜色、大小、位置、字体等。需要用一段流畅的话描述，比如：“图片背景空白区域写有小红书爆款风格的网感艺术大字“吹风机界的纳米水光针”，具有吸引力，字体酷炫，另外也有小字“秒吹干！”，配合一些吹动的风等涂鸦线条，可爱充满活力。”\n\n
# 这个商品展示图描述如下：
{image_description}"""
        if params and "description_to_label_prompt" in params:
            description_to_label_prompt = params["description_to_label_prompt"]

        description_to_label_query = description_to_label_prompt.format(image_description=image_description)
        label_text = self.fangzhou_api.query_chat(description_to_label_query, platform="fangzhou",
                                                  model_name="Doubao-1.5-pro-32k")
        print(f"[LABEL TEXT]: {label_text}")

        ai_img_prompt = "小红书封面海报。{label_text}{image_description}"
        if params and "ai_img_prompt" in params:
            ai_img_prompt = params["ai_img_prompt"]

        ai_image_query = ai_img_prompt.format(label_text=label_text,
                                              image_description=re.sub("\n+", "", image_description, re.S))
        result2 = self.jimeng_api.text_to_image(ai_image_query, model="文生图2.1",
                                                params={
                                                    "width": width,
                                                    "height": height,
                                                    "use_pre_llm": True,
                                                    "num_images": 1})
        # AI图生成
        ai_image = result2.get("output_images")[0]

        # # AI图抠取实体
        # result3 = self.jimeng_api.picture_seg(ai_image, save_mask=True)
        # ai_image_seg_mask = result3.get("output_images")[1]
        #
        # # AI图主体涂抹
        # result4 = self.jimeng_api.inpainting_eraser(input_data=ai_image, mask_data=ai_image_seg_mask)
        # ai_image_erased = result4.get("output_images")[0]
        #
        # # 产品图主体抠取
        # result5 = self.jimeng_api.picture_seg(image)
        # product_seg = result5.get("output_images")[0]
        #
        # print(f"ai_image_erased: {type(ai_image_erased)} \n{str(ai_image_erased)[:100]}\n\n"
        #       f"product_seg: {type(product_seg)} \n{str(product_seg)[:100]}")

        # concat_image = image_handler.image_overlay([ai_image_erased, product_seg])

        replace_smaller_ratio = None
        if params and "replace_smaller_ratio" in params:
            replace_smaller_ratio = params["replace_smaller_ratio"]
        seg_erased_concat_images = self.image_seg_perspective_transform_overlay(image, ai_image,
                                                                                replace_smaller_ratio=replace_smaller_ratio)

        # result6 = self.jimeng_api.image_correction(concat_image)
        # concat_image_corrected = result6.get("output_images")[0]
        #
        # text_seed_edit_prompt = "美化图片。"
        # if params and "text_seed_edit_prompt" in params:
        #     text_seed_edit_prompt = params["text_seed_edit_prompt"]
        #
        # result7 = self.jimeng_api.image_text_seed_edit(text_seed_edit_prompt, concat_image)
        # concat_image_edited = result7.get("output_images")[0]
        #
        # result8 = self.jimeng_api.clearer(concat_image)
        # concat_image_cleared = result8.get("output_images")[0]

        end_time = time.time()

        result = {
            "image_description": image_description,
            "label_text": label_text,
            "binary_data_base64": [image_handler.image_data_to_base64(seg_erased_concat_images[-1])]
        }

        whole_result = {
            "image_description": image_description,
            "label_text": label_text,
            "output_images": [
                                 ai_image
                                 # , ai_image_seg_mask, ai_image_erased, product_seg, concat_image,
                                 # concat_image_corrected, concat_image_edited, concat_image_cleared
                             ] + seg_erased_concat_images,
        }

        save_and_log(None, input_data, result, output_path)

        print(f"Used [DIY ai_product_image] over.")
        print(f"used time: {end_time - start_time}")
        return whole_result

    def get_image_seg_points_width_height(self, _image):
        # 计算四个点的坐标
        def get_picture_seg_four_points(contours_point):
            points = np.array(contours_point[0][0])
            x_min, x_max, y_min, y_max = np.min(points[:, 0]), np.max(points[:, 0]), np.min(points[:, 1]), np.max(
                points[:, 1])
            four_points = np.array([[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]])
            return four_points

        # 抠取实体图并获取四个角点
        image_seg_result = self.jimeng_api.picture_seg(_image, save_mask=True)
        image_seg_obj = image_seg_result.get("output_images")[0]
        image_seg_mask_obj = image_seg_result.get("output_images")[1]
        points = image_seg_result.get("contours_point")
        points_four = get_picture_seg_four_points(points)
        seg_width = points_four[1][0] - points_four[0][0]
        seg_height = points_four[3][1] - points_four[0][1]
        return image_seg_obj, image_seg_mask_obj, points_four, seg_width, seg_height

    def image_seg_perspective_transform_overlay(self, _source_image, _target_image, replace_smaller_ratio=None):
        print(f"Start <image_seg_perspective_transform_overlay> ...")

        # 抠取实体图并获取四个角点
        source_seg_image, source_seg_mask_image, source_points_four, source_seg_width, source_seg_height = self.get_image_seg_points_width_height(
            _source_image)
        print(f"source_points_four: {source_points_four}\n"
              f"source seg width, height: {source_seg_width}, {source_seg_height}")

        # 抠取目标位置实体图并获取四个角点
        target_seg_image, target_seg_mask_image, target_points_four, target_seg_width, target_seg_height = self.get_image_seg_points_width_height(
            _target_image)
        print(f"target_points_four: {target_points_four}, "
              f"target seg width, height: {target_seg_width}, {target_seg_height}")

        seg_bias = 2  # 抠图实体之后切割到实体边缘的预留像素点，免得切割的过于突兀

        # 10, 8
        if replace_smaller_ratio:  # 0.8 -> 8, 6.4
            target_seg_width_smaller = target_seg_width * replace_smaller_ratio
            target_seg_height_smaller = target_seg_height * replace_smaller_ratio
        else:
            target_seg_width_smaller = target_seg_width
            target_seg_height_smaller = target_seg_height

        # 计算尺寸变换的比例
        # ratio_width = target_seg_width / source_seg_width  # 0.7   2 , 大于1取小的，小于1取小的
        # ratio_height = target_seg_height / source_seg_height  # 0.6   1.5
        ratio_width = target_seg_width_smaller / source_seg_width  # 0.7   2 , 大于1取小的，小于1取小的
        ratio_height = target_seg_height_smaller / source_seg_height  # 0.6   1.5

        # 3, 9 -> 2.1333, 6.4
        ratio = min(ratio_width, ratio_height)
        resized_width = int(source_seg_width * ratio)
        resized_height = int(source_seg_height * ratio)
        print(f"resized ratio (source->target): {ratio}\n"
              f"resized width, resized height: {resized_width}, {resized_height}")

        # x=3 y=3  15 -> 10 -> 8

        # 计算抠图实体将要放置在背景图中的位置偏移量（在目标实体的位置x居中，y靠下）
        width_gap = int((target_seg_width - resized_width) / 2)
        # height_gap = int((target_seg_height - resized_height) / 2)
        height_gap = int(target_seg_height - resized_height)
        paste_start_x = target_points_four[0][0] + width_gap
        paste_start_y = target_points_four[0][1] + height_gap + seg_bias
        print(f"paste bias x, y: {paste_start_x, paste_start_y}")

        # 抠图的实体裁剪
        ## 定义裁剪区域的四元组（左上角x, 左上角y, 右下角x, 右下角y）
        source_seg_image_cut_area = (int(source_points_four[0][0] - seg_bias), int(source_points_four[0][1] - seg_bias),
                                     int(source_points_four[2][0] + seg_bias), int(source_points_four[2][1] + seg_bias))
        source_seg_image_cut = source_seg_image.crop(source_seg_image_cut_area)
        # 抠图的实体按照目标实体的大小进行尺寸变换
        source_seg_image_cut_resized = source_seg_image_cut.resize((resized_width, resized_height),
                                                                   Image.Resampling.LANCZOS)

        # 目标图主体涂抹
        target_image = image_handler.base64_to_image(image_handler.image_data_to_base64(_target_image))
        erase_result = self.jimeng_api.inpainting_eraser(input_data=target_image, mask_data=target_seg_mask_image)
        background_image_obj = erase_result.get("output_images")[0]
        erased_image = copy.deepcopy(background_image_obj)

        r, g, b, mask = source_seg_image_cut_resized.split()  # 提取叠加的主图图片中包含的透明通道
        background_image_obj.paste(source_seg_image_cut_resized, (paste_start_x, paste_start_y),
                                   mask=mask)  # 背景图上叠加抠图改变大小后的主图。

        dir_path = "/Users/admin/program/projects/multi_model_api_gradio/data/test/image_seg_perspective_transform/"
        source_seg_image.save(f"{dir_path}source_seg_image.png")
        source_seg_image_cut.save(f"{dir_path}source_seg_image_cut.png")
        source_seg_image_cut_resized.save(f"{dir_path}source_seg_image_cut_resized.png")
        background_image_obj.save(f"{dir_path}background_image_obj.png")

        print(f"Finish <image_seg_perspective_transform_overlay>.")
        out = [source_seg_image, source_seg_mask_image, target_seg_image, target_seg_mask_image, erased_image,
               background_image_obj]
        print([type(x) for x in out])
        return out

    def auto_text_image_to_video(self, input_image, image_to_text__prompt, image_to_text__model,
                                 text_to_text__prompt, text_to_text__model,
                                 image_text_to_video__model="图生视频-首帧 | doubao-seedance-1-0-lite-i2v-250428",
                                 params=None):
        '''图生文，文生文，图文生视频 '''
        print(f"\n===\nYou are using [DIY auto_text_image_to_video]...")
        start_time = time.time()

        whole_result = dict()

        if not params:
            params = dict()

        logger.info("\n\n\n")
        logger.info(f"\n=== auto_text_image_to_video ===\n"
                    f"Input: \n"
                    f"input_image: {input_image}\n"
                    f"image_to_text__prompt: {image_to_text__prompt}\n"
                    f"image_to_text__model: {image_to_text__model}\n"
                    f"text_to_text__prompt: {text_to_text__prompt}\n"
                    f"image_text_to_video__model: {image_text_to_video__model}\n"
                    f"params: {params}\n"
                    )

        # 图生文 image_to_text
        result1 = self.fangzhou_api.picture_to_text__fangzhou(input_image, image_to_text__prompt, image_to_text__model)
        image_description = result1.get("text", "")
        print(f"[IMAGE DESCRIPTION]: {image_description}")

        logger.info(f"第一步 - 图生文:\n"
                    f"[IMAGE DESCRIPTION]: {image_description}")

        whole_result["image_description"] = image_description

        print(f"image_to_text used time: {time.time() - start_time}")
        start_time = time.time()

        # 文生文 text_to_text
        text_to_text__query = text_to_text__prompt.format(image_description=image_description,
                                                          product_name=params.get("product_name", "商品"))
        result2 = self.text_api.text_chat_one_turn(text_to_text__query, text_to_text__model)
        result2_text = result2.get("answer", "")

        whole_result["t2t_answer"] = result2_text

        def handle_video_description(text):
            t = re.search("\n#\s*视频描述[:：\n]+(.*)", "\n" + text, flags=re.S)
            if t:
                return t.group(1).strip()
            else:
                return text

        image_to_video_query = handle_video_description(result2_text)
        print(f"[IMAGE_TO_VIDEO_QUERY]: {image_to_video_query}")

        logger.info(f"第二步 - 文生文:\n"
                    f"[IMAGE_TO_VIDEO_QUERY]: {image_to_video_query}")

        whole_result["text_to_text__query"] = text_to_text__query
        whole_result["image_to_video_query"] = image_to_video_query

        print(f"text_to_text used time: {time.time() - start_time}")
        start_time = time.time()

        # 图文生视频 image_text_to_video
        result3 = self.volcengine_api.video_generation(model=image_text_to_video__model,
                                                       prompt=image_to_video_query,
                                                       image_data1=input_image,
                                                       params=params)
        video_url = result3.get("video_url", "")
        print(f"[VIDEO_URL]: {video_url}")

        logger.info(f"第三步 - 图文生视频:\n"
                    f"[VIDEO_URL]: {video_url}\n"
                    f"output_path: {result3.get('output_path')}\n"
                    f"generate time: {time.time()}")

        whole_result["output_video"] = video_url
        whole_result["video_url"] = video_url

        print(f"image_text_to_video used time: {time.time() - start_time}")

        return whole_result

    def scene_text_image_to_video(self, input_image, video_type, params=None):
        from prompt.scene_text_image_to_video_prompt import product_effect_prompt, product_atmosphere_prompt, \
            product_creativity_prompt

        print(f"\n===\nYou are using [DIY scene_text_image_to_video]...")

        video_prompt_map = {
            "商品效果展示": product_effect_prompt,
            "商品氛围展示-风格展示": product_atmosphere_prompt,
            "商品氛围展示-创意展示": product_creativity_prompt
        }
        image_to_text__prompt = "详细解读这张图片"
        image_to_text__model = "Doubao-vision-pro-32k-241028"
        text_to_text__prompt = video_prompt_map.get(video_type, "")
        text_to_text__model = "fangzhou | Deepseek-r1-250528"

        text_to_text__query = text_to_text__prompt
        video_params = params.copy()
        for k in list(params.keys()):
            if "{" + k + "}" in text_to_text__query:
                text_to_text__query = text_to_text__query.replace("{" + k + "}", str(params.get(k, "")))

        whole_result = {
            "image_to_text__prompt": image_to_text__prompt,
            "image_to_text__model": image_to_text__model,
            "text_to_text__model": text_to_text__model,
            "text_to_text__prompt": text_to_text__prompt
        }

        result = self.auto_text_image_to_video(input_image, image_to_text__prompt, image_to_text__model,
                                               text_to_text__query,  #
                                               text_to_text__model,
                                               image_text_to_video__model="图生视频-首帧 | doubao-seedance-1-0-pro-250528",
                                               params=video_params)
        whole_result.update(result)

        return whole_result

    def video_split_analyze(self, video_data, prompt, params=None):

        print(f"\n===\nYou are using [video_split_analyze]...")

        print(video_data, type(video_data))  # str

        def scenes_concat(scenes):
            return "\n\n\n".join([f"{'%.2f' % x.get('start_time')}s ~ {'%.2f' % x.get('end_time')}s：{x.get('interpretation')}" for x in scenes])

        # 上传video视频
        video_url = video_handler.get_video_remote_url(video_data)
        video_name = re.split("[\\/]", video_url, flags=re.S)[-1]


        logger.info(f"第一步 - 视频上传:\n"
                    f"[Video Data]: {video_data}\n"
                    f"[Video Url]: {video_url}")

        # whole_result = {
        #     "output_videos": [video_url],
        #     "video_url": video_url,
        #     "scenes_count": str(1),
        #     "scenes_text": "origin",
        #     "output_video": video_url
        # }
        #
        # return whole_result

        # 模式：
        # 'content': 'ContentDetector - 基于内容变化检测场景切换',
        # 'threshold': 'ThresholdDetector - 基于像素亮度阈值检测',
        # 'adaptive': 'AdaptiveDetector - 自适应检测，结合多种特征',
        # 'histogram': 'HistogramDetector - 基于颜色直方图检测'
        form = {
            "url": video_url,
            "question": prompt,  # "帮我解析一下这个视频信息"
            "mode": "content",
            "threshold": 0.3
        }
        if prompt:
            form.update({"question": prompt})
        if params:
            for k, v in params.items():
                if k in form:
                    form[k] = v


        logger.info(f"第二步 - 视频场景切割解析:\n"
                    f"[Form]: {form}")

        URL = "https://wisemaa.yingsaidata.com/video/interpretation"

        print(f"Request: {form}")
        res = requests.post(URL, data=json.dumps(form))
        response = res.json()
        print(f"Response: {response}")
        result = response

        # result = {'code': 0, 'message': '请求成功', 'data': {'scenes': [{'scene_number': 1, 'start_time': 0.0, 'end_time': 4.637966666666666, 'duration': 4.637966666666666, 'start_frame': 0, 'end_frame': 139, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/6e7ec78dc44240edb5d8384597e70855.mp4', 'interpretation': '视频展示了一个放置在浅色木质桌面上的书本形状的折叠灯，灯光柔和，呈现出温暖的黄色。灯的左侧有两本书，分别是《THE FASHION BUSINESS MANUAL》和《LIFE STYLE》，右侧有一个小型的白色花盆，里面种植着多肉植物。背景是一张灰色的沙发，沙发上有几个灰色的靠垫。整个场景显得温馨而宁静，灯光的柔和与周围环境的简洁形成了和谐的对比。'}, {'scene_number': 2, 'start_time': 4.637966666666666, 'end_time': 16.7167, 'duration': 12.078733333333334, 'start_frame': 139, 'end_frame': 501, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/a3417313d10b40eabe336e72cbb0379d.mp4', 'interpretation': '这个视频展示了一款创意折叠书灯的使用场景。视频开始时，镜头聚焦在一个打开的书灯上，书灯呈现出扇形展开的形态，发出柔和的黄色光芒。背景中可以看到几本书和一个白色的台灯，营造出温馨的阅读氛围。\n\n随着镜头的逐渐拉远，书灯的全貌更加清晰，周围的环境也变得更加明显。背景中的书籍和台灯逐渐模糊，书灯成为画面的焦点。镜头继续拉远，书灯被放置在一个木质的床头柜上，旁边可以看到一部分床和枕头，进一步强调了书灯在卧室中的使用场景。\n\n视频的最后部分，书灯被展示在一个不同的环境中，背景是一个深色的墙面和一个装饰画。书灯此时呈现出圆形展开的形态，旁边的文字“Creative Handmade Folding Processes”说明了这款书灯的创意手工折叠工艺。\n\n整个视频通过不同的视角和背景展示了书灯的多功能性和美观性，突出了其作为创意家居装饰品的特点。'}, {'scene_number': 3, 'start_time': 16.7167, 'end_time': 19.8198, 'duration': 3.1031, 'start_frame': 501, 'end_frame': 594, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/0e1e175a10804ee7b35549711991bab9.mp4', 'interpretation': '视频展示了一盏手工折叠的创意灯具。灯具呈现出扇形的设计，灯光柔和，照亮了周围的环境。背景中有一个带有圆形图案的装饰，整体氛围温馨而富有创意。视频中的文字“Creative Handmade Folding Processes”强调了这盏灯具的手工折叠工艺和创意设计。'}, {'scene_number': 4, 'start_time': 19.8198, 'end_time': 21.755066666666668, 'duration': 1.9352666666666667, 'start_frame': 594, 'end_frame': 652, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/e44d591fed8e47cfbef62681dccfd418.mp4', 'interpretation': '视频展示了一款创意手工折叠灯。这款灯的设计独特，采用了手工折叠工艺，呈现出扇形的外观。灯光柔和，营造出温馨的氛围。背景为暖色调，进一步增强了灯光的温暖感。视频中的文字“Creative Handmade Folding Processes”强调了这款灯的创意手工折叠工艺，突出了其独特的制作过程和艺术价值。整体画面简洁而富有艺术感，展示了这款灯的美观与实用性。'}, {'scene_number': 5, 'start_time': 21.755066666666668, 'end_time': 25.392033333333334, 'duration': 3.636966666666667, 'start_frame': 652, 'end_frame': 761, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/798cbb3ddcd043c7a1612149d8548c06.mp4', 'interpretation': '视频展示了一款可折叠的创意灯具，灯具的形状可以灵活改变。视频分为四个部分，分别展示了灯具在不同形状下的状态：\n\n1. **左上角**：灯具展开成扇形，放置在桌面上。\n2. **右上角**：灯具部分折叠，呈现出半开的状态，放置在桌面上。\n3. **左下角**：灯具完全展开成圆形，放置在桌面上。\n4. **右下角**：灯具垂直折叠，呈现出长条形，挂在墙上。\n\n视频上方有文字“Flexible To Change The Shape”，强调了灯具形状的灵活性。背景环境较为昏暗，突出灯具的柔和光线和独特设计。'}, {'scene_number': 6, 'start_time': 25.392033333333334, 'end_time': 30.7307, 'duration': 5.338666666666667, 'start_frame': 761, 'end_frame': 921, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/07059a05990a451882dd0b601c3a326b.mp4', 'interpretation': '视频展示了一个人双手操作一个折叠式书本灯的过程。\n\n1. **初始状态**：书本灯处于闭合状态，呈立方体形状，颜色为浅木色。\n2. **打开书本灯**：双手握住书本灯的两侧，轻轻向外展开，书本灯逐渐打开，内部的LED灯亮起，发出温暖的黄色光芒。\n3. **完全展开**：书本灯完全展开后，呈现出扇形的结构，灯光均匀地散发出来，照亮周围环境。\n4. **闭合书本灯**：双手再次握住书本灯的两侧，轻轻向内折叠，书本灯逐渐闭合，灯光随之熄灭。\n\n整个过程展示了书本灯的设计和功能，强调了其便携性和美观性。'}, {'scene_number': 7, 'start_time': 30.7307, 'end_time': 41.77506666666667, 'duration': 11.044366666666667, 'start_frame': 921, 'end_frame': 1252, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/c23bc65e45454062a7cd450fd0fc4ce5.mp4', 'interpretation': '视频展示了一款可折叠便携式台灯的使用过程。首先，一只手将台灯从展开状态逐渐折叠成一个小巧的立方体形状，展示了其便携性。接着，手将折叠好的台灯放入一个白色的手提包中，进一步强调了其便携性。最后，视频展示了台灯的充电功能，手将充电线插入插座，说明这款台灯内置电池且可充电。视频通过这些步骤，清晰地展示了台灯的折叠便携性和充电功能。'}, {'scene_number': 8, 'start_time': 41.77506666666667, 'end_time': 51.051, 'duration': 9.275933333333333, 'start_frame': 1252, 'end_frame': 1530, 'video_url': 'https://static5.yingsaidata.com/video_segments/20250624/0ae0a3e67e964064ae6ec7ef2043adb5.mp4', 'interpretation': '这个视频展示了一款创意折叠台灯的特点和使用场景。视频开始时，画面聚焦在一只手正在插入充电线到台灯的充电口，旁边的文字说明“Bulit-in Battery & Rechargeable Table Lamp”（内置电池和可充电台灯）。接着，镜头切换到展示两个不同形态的台灯，一个是展开的圆形，另一个是扇形，旁边的文字说明“Uniwolk Creative Handmade Folding Lamp”（Uniwolk创意手工折叠台灯）。背景是一个温馨的室内环境，灯光柔和，营造出温暖的氛围。整个视频通过展示台灯的充电功能和不同形态，突出了其创意和实用性。'}]}}


        scenes = result.get("data", dict()).get("scenes", [])
        scenes_text = scenes_concat(scenes)

        scenes_urls = [x.get("video_url") for x in scenes]

        output_path = f"{self.output_videos_path}/video_split_analyze/{video_name}-{form['mode']}-{len(scenes)}.mp4"

        video_handler.concat_videos_with_tail_frame_stop(scenes_urls, output_path)

        # output_path = "/Users/admin/program/projects/multi_model_api_gradio/data/output_videos/diy/video_split_analyze/caa57dca3e1f41d6813b1ca7d592570f.mp4-8.mp4"

        whole_result = {
            # "concat_videos_with_tail_frame_stop": output_path,
            "output_video": output_path,
            "video_url": video_url,
            "scenes_count": str(len(scenes)),
            "scenes_text": scenes_text
        }

        logger.info(f"[Whole Result]: {whole_result}")

        print(f"Used [video_split_analyze] over.")
        return whole_result




class TEST(unittest.TestCase):
    diy_api = DiyAPI()

    def test_text_to_image(self):
        path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/松下吹风机/松下吹风机.png"
        self.diy_api.ai_product_image(path)

    def test_image_seg_perspective_transform(self):
        # self.jimeng_api.picture_seg("/Users/admin/Files/评测/文生图/图片/source/商品图加字/SK-II面霜/ai图4.png")

        # source_path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/SK-II面霜/产品图.png"
        # target_path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/SK-II面霜/ai图4.png"
        # background_path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/SK-II面霜/ai图4 涂抹.png"

        # self.diy_api.image_seg_perspective_transform_overlay(source_path, target_path, replace_smaller_ratio=0.8)

        source_path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/TF白麝香/产品图.png"
        target_path = "/Users/admin/Files/评测/文生图/图片/source/商品图加字/TF白麝香/ai图3.png"
        self.diy_api.image_seg_perspective_transform_overlay(source_path, target_path)
