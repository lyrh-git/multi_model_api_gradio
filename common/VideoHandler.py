import base64
import copy
import hashlib
import imghdr
import io
import json
import math
import os
import re
import unittest

import PIL.Image
import cv2
import numpy as np
from PIL import Image
import requests
from moviepy import VideoFileClip, AudioFileClip
import cv2
import numpy as np
from pydub import AudioSegment

from FileHandler import FileHandler
from config import NGINX as NGINX_URL
from TimeHandler import TimeHandler

time_handler = TimeHandler()
file_handler = FileHandler()


class VideoHandler:
    UPLOAD_VIDEO_STATUS_PATH = "/Users/admin/program/projects/multi_model_api_gradio/data/upload_file_manage/upload_video_status.json"

    def __init__(self):
        data = file_handler.read_json_lines(self.UPLOAD_VIDEO_STATUS_PATH)
        self.upload_video_dict = {key: value for dictionary in data for key, value in dictionary.items()}
        # for k, v in self.upload_video_dict.items():
        #     print(k, v)

    def get_video_remote_url(self, video_path):
        # for k, v in self.upload_video_dict.items():
        #     print(k, v)

        if video_path in self.upload_video_dict:
            video_url = self.upload_video_dict[video_path]
            print(f"Existed video {video_path} , url: {video_url}")
            return video_url
        else:
            video_url = self.video_path_to_remote_url(video_path)
            self.add_video_remote_url(video_path, video_url)
            return video_url

    def add_video_remote_url(self, video_path, video_url):
        self.upload_video_dict[video_path] = video_url
        with open(self.UPLOAD_VIDEO_STATUS_PATH, "a") as f:
            f.write(json.dumps({video_path: video_url}, ensure_ascii=False))
            f.write("\n")

    def video_path_to_remote_url(self, video_path):

        print(f"Uploading video {video_path} ...")

        url = "https://wisemaa.yingsaidata.com/files/upload"

        video_name = os.path.basename(video_path)

        files = {"file": (video_name, open(rf'{video_path}', "rb"))}

        # [
        #     # ('file', (video_name, open(rf'{video_path}', "rb"), f'video/{video_name.split(".")[-1]}'))
        #     ('file', (video_name, open(rf'{video_path}', "rb"))  # 成功！
        #     # xxx失败xxx ('file', (file_name, image_bytes_buffer, f'image/{image_type}'))  # 失败（文件为空）：requests files: [('file', ('松下吹风机.png', <_io.BufferedReader>, 'image/png'))]
        #     # √√√成功√√√ ('file', (file_name, open(image_data, "rb"), f'image/{image_type}'))  # 成功： <_io.BufferedReader name='/Users/admin/program/projects/multi_model_api_gradio/data/flask/upload/松下吹风机.png'>
        # ]

        # print(f"requests files: {files}")
        headers = {}

        response = requests.request("POST", url, headers=headers, data=None, files=files)
        print(response, response.text)

        result = response.json()
        print(result)
        video_url = result.get("data", dict()).get("url", None)
        if not video_url:
            print(f"Upload video failed, message: {result}")
        else:
            print(f"Upload video {video_path} successfully, url: {video_url}")

        return video_url

    def identify_video_format(self, video_path):
        try:
            # 打开视频文件
            clip = VideoFileClip(video_path)
            # 获取视频的元数据
            meta_data = clip.metadata
            # 关闭视频文件
            clip.close()
            # 返回视频格式
            return meta_data['major_brand']
        except Exception as e:
            print(f"无法识别视频格式: {e}")
            return "mp4"


    def concat_videos_with_tail_frame_stop(self, videos_list, output_path):
        # 创建一个矩形蒙版
        def create_mask(frame_shape, x, y, width, height):
            print(frame_shape, x, y, width, height)
            mask = np.zeros(frame_shape[:2], dtype="uint8")
            cv2.rectangle(mask, (x, y), (x + width, y + height), 255, -1)  # 填充白色矩形 （实心矩形框 -1）
            return mask

        frames = []
        for video_path in videos_list:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            fps = math.ceil(fps)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_count = 0
            frame = None
            while frame_count < total_frames:
                ret, frame = cap.read()
                frames.append(frame)
                frame_count += 1

            _frame = copy.deepcopy(frame)
            mask = create_mask(_frame.shape, _frame.shape[1] // 6,  _frame.shape[0] // 6, _frame.shape[1] // 6 * 4, _frame.shape[0] // 6 * 4)
            # 应用蒙版，这里我们将其设置为全黑（你也可以设置为其他颜色
            masked_frame = cv2.bitwise_and(_frame, _frame, mask=mask)

            frames += [masked_frame] * fps

        # 获取第一帧的尺寸（假设所有帧的尺寸相同）
        frame_width = frames[0].shape[1]
        frame_height = frames[0].shape[0]

        # 定义输出视频的参数
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*f'mp4v'), fps, (frame_width, frame_height))

        # 写入帧到输出文件
        for frame in frames:
            out.write(frame)

        out.release()  # 释放VideoWriter对象


    def get_audio_from_video(self, video_path, audio_path):
        audio_clip = AudioFileClip(video_path)
        audio_clip.write_audiofile(audio_path)

class TEST(unittest.TestCase):
    video_handler = VideoHandler()

    def test_get_video_remote_url(self):
        paths = [
            # '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/手机壳/视频素材/手机壳-官方视频1.mp4',
            # '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/手机壳/视频素材/手机壳-视频3.mp4',
            # '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频素材/书灯-用户实拍1.mp4',
            # '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频素材/书灯-宣传视频2.mp4',
            '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频素材/书灯-用户实拍2.mp4',
            '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频素材/书灯-用户实拍3.mp4',
            '/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/手表/视频素材/手表-用户视频1.mp4']

        # video_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/挂脖风扇/视频素材/挂脖风扇-用户视频-视频2.mp4"
        for video_path in paths:
            self.video_handler.get_video_remote_url(video_path)

    def test_concat_videos_with_tail_frame_stop(self):
        videos_list = ["/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频片段裁剪/part1.mov",
                       "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频片段裁剪/part3.mov"]
        output_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/书灯/视频片段裁剪/part1-part3.mov"
        self.video_handler.concat_videos_with_tail_frame_stop(videos_list, output_path)


    def test_get_audio_from_video(self):
        video_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/手表/视频素材/手表-用户视频1.mp4"
        audio_path = "/Users/admin/program/projects/Myproject/data/source/视频生成/商品素材/手表/视频素材/手表-用户视频1.mp3"
        self.video_handler.get_audio_from_video(video_path, audio_path)