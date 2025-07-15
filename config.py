from gradio import Image

# NGINX = "https://6873-58-250-250-208.ngrok-free.app"  # ngrok
NGINX = "http://dbs2ux.natappfree.cc"  # natapp
# NGINX = "http://momo.free.idcfengye.com"  # sunny-ngrok

DEFAULT_NEGATIVE_PROMPT = "nsfw, nude, smooth skin, unblemished skin, mole, low resolution, blurry, worst quality, mutated hands and fingers, poorly drawn face, bad anatomy, distorted hands, limbless, national flag"


SETTINGS = {
    "text_chat_one_turn": {
        "prompt": {
            "type": str,
            "default": "你是什么模型？",
            "explanation": "单轮文本提示词"
        },
        "model": {
            "type": list,
            "choices": [
                # 'qianfan | chatglm2-6b-32k',
                'hunyuan | hunyuan-pro',
                'hunyuan | hunyuan-turbo',
                'fangzhou | Doubao-1.5-pro-32k',
                'fangzhou | Doubao-pro-32k-240828',
                'fangzhou | Doubao-pro-32k',
                'fangzhou | Doubao-pro-32k-func',
                'fangzhou | Doubao-pro-128k',
                'fangzhou | Doubao-lite-4k',
                'fangzhou | fangzhou_chat_agent',
                'fangzhou | Deepseek-V3',
                'fangzhou | Deepseek-r1-250120',
                'fangzhou | Deepseek-r1-250528',
                'qwen2 | qwen2-72b',
                'donson | glm4:9b-chat-fp16',
                'donson | qwen:72b-chat-v1.5-fp16',
                'self | xhs_zhongcao_sft'],
            "default": "fangzhou | Deepseek-r1-250528",
            "explanation": "本地部署模型"
        }
    },

    "text_to_image":
        {
            "prompt": {
                "type": str,
                "default": "线条小狗表情包",
                "explanation": "正向词"
            },
            "negative_prompt": {
                "type": str,
                "default": DEFAULT_NEGATIVE_PROMPT,
                "explanation": "负向词"
            },
            "model": {
                "type": list,
                "choices": ["文生图2.0L", "文生图2.1", "文生图3.0"],
                "default": "文生图3.0",
                "explanation": ""
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子，作为确定扩散初始状态的基础，默认-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成图片极大概率效果一致"
            },
            "scale": {
                "type": float,
                "range": [1, 10],
                "default": 2.5,  # 3.0版本2.5，其他3.5
                "explanation": "影响文本描述的程度"
            },
            "ddim_steps": {
                "type": int,
                "range": [1, 200],
                "default": 16,
                "explanation": "生成图像的步数，建议使用默认值，过大会造成延迟增加而服务超时；2.1 -> 25 [1, 200] 推荐[1, 50]; 2.0 -> 16 [1-50]"
            },
            "width": {
                "type": int,
                "range": [1, 5000],
                "default": 576,
                "explanation": "推荐[256, 768]"
            },
            "height": {
                "type": int,
                "range": [1, 5000],
                "default": 1024,
                "explanation": "推荐[256, 768]"
            },
            "use_pre_llm": {
                "type": bool,
                "default": False,
                "explanation": "开启文本扩写，会针对输入prompt进行扩写优化，如果输入prompt较短建议开启，如果输入prompt较长建议关闭"
            },
            "use_sr": {
                "type": bool,
                "default": True,
                "explanation": "True：文生图+AIGC超分；False：文生图。内置的超分功能，开启后可将上述宽高均乘以2返回，此参数打开后延迟会有增加"
            },
            "num_generate": {
                "type": int,
                "range": [1, 10],
                "default": 2,
                "explanation": "生成图片的数量"
            }

        },

    "image_text_seed_edit":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "prompt": {
                "type": str,
                "default": "重绘成彩色雕版图画的风格。",
                "explanation": "正向词"
            },
            "negative_prompt": {
                "type": str,
                "default": "",
                "explanation": "负向词"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子，作为确定扩散初始状态的基础，默认-1（随机）。若随机种子为相同正整数且其他参数均一致，则生成图片极大概率效果一致"
            },
            "scale": {
                "type": float,
                "range": [0, 1],
                "default": 0.5,
                "explanation": "影响文本描述的程度，该值越大代表文本描述影响程度越大，且输入图片影响程度越小"
            }
        },

    "image_text_seed_edit_2":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "prompt": {
                "type": str,
                "default": "重绘成彩色雕版图画的风格。",
                "explanation": "正向词"
            },
            "cfg": {
                "type": float,
                "range": [0.1, 10.0],
                "default": 3.0,
                "explanation": "控制提示词与出图相关性；参数越大，生成的图像与文本提示的相关性越高，但可能会失真。数值越小，相关性则越低，越有可能偏离提示或输入图像，但质量越好。默认值：3.0；取值范围：[0.1, 10.0]"
            },
            "strength": {
                "type": float,
                "range": [0.1, 1.0],
                "default": 0.9924999999999999,
                "explanation": "取值越小输出图与输入图关联参考性越大，取值越大与输入图参考性越小；默认值：0.9924999999999999（推荐）；取值范围：（0.1, 1.0）"
            },
            "steps": {
                "type": float,
                "range": [1, 8],
                "default": 4,
                "explanation": "生成图像的步数；推理步数 ，决定输出图像精细程度，过高会导致处理时长较长；默认值：4；取值范围：[1, 8]"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子；默认：-1（随机）"
            },
            "controlnet_conditioning_scale": {
                "type": float,
                "range": [1, 10],
                "default": 1,
                "explanation": "未暴露参数"
            }
        },

    "character_preservation":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "prompt": {
                "type": str,
                "default": "换成动漫手绘的风格。",
                "explanation": "正向词"
            },
            "desc_pushback": {
                "type": bool,
                "default": True,
                "explanation": "针对输入图内容进行反推，可使生成图片效果更稳定"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子"
            },
            "scale": {
                "type": float,
                "range": [1, 10],
                "default": 3.5,
                "explanation": "影响文本描述的程度，该值越大代表文本描述影响程度越大，且输入图片影响程度越小"
            },
            "ddim_steps": {
                "type": int,
                "range": [1, 200],
                "default": 9,
                "explanation": "生成图像的步数"
            },
            "width": {
                "type": int,
                "range": [1, 5000],
                "default": 576,
                "explanation": "推荐[256, 768]"
            },
            "height": {
                "type": int,
                "range": [1, 5000],
                "default": 1024,
                "explanation": "推荐[256, 768]"
            },
            "cfg_rescale": {
                "type": float,
                "range": [0, 1],
                "default": 0.7,
                "explanation": ""
            },
            "ref_ip_weight": {
                "type": float,
                "range": [0, 1],
                "default": 0.7,
                "explanation": "参考图主体外观的权重，越大生成结果和参考图中主体的相似度越高"
            },
            "ref_id_weight": {
                "type": float,
                "range": [0, 1],
                "default": 0.36,
                "explanation": "推荐取值范围[0.2, 0.4] 参考图人脸特征的权重，越大生成结果和参考图中人脸的相似度越高"
            },
            "use_sr": {
                "type": bool,
                "default": True,
                "explanation": " True：文生图+AIGC超分；False：文生图。内置的超分功能，开启后可将上述宽高均乘以2返回，此参数打开后延迟会有增加"
            }
        },

    "image_to_image":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "controlnet_image": {
                "type": Image,
                "default": "",
                "explanation": "实体参考图"
            },
            "style_image": {
                "type": Image,
                "default": "",
                "explanation": "风格参考图"
            },

            "prompt": {
                "type": str,
                "default": "添加背景为国潮风格。",
                "explanation": "正向词"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子"
            },
            "ddim_steps": {
                "type": int,
                "range": [1, 50],
                "default": 20,
                "explanation": "生成图像的步数"
            },
            "scale": {
                "type": float,
                "range": [1, 30],
                "default": 7.0,
                "explanation": "影响文本描述的程度，该值越大代表文本描述影响程度越大，且输入图片影响程度越小"
            },
            "controlnet__type": {
                "type": str,
                "choices": ["canny", "depth", "pose"],
                "default": "canny",
                "explanation": "controlnet保持构图的方案，canny轮廓边缘/depth景深/pose人物姿态"
            },
            "controlnet__strength": {
                "type": float,
                "range": [0.0, 1.0],
                "default": 0.4,
                "explanation": "controlnet强度, 为0的时候基本没有物体参考"
            },
            "style__id_weight": {
                "type": float,
                "range": [0.0, 1.0],
                "default": 0.2,
                "explanation": "ID保持的作用是人脸保持"
            },
            "style__style_weight": {
                "type": float,
                "range": [0.0, 1.0],
                "default": 0.0,
                "explanation": "风格迁移的强度"
            }
        },

    "image_to_image2":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "controlnet_image": {
                "type": Image,
                "default": "",
                "explanation": "实体参考图"
            },
            "prompt": {
                "type": str,
                "default": "重绘成动漫风格。",
                "explanation": "正向词"
            },
            "scale": {
                "type": float,
                "range": [1, 30],
                "step": 0.1,
                "default": 3.0,
                "explanation": "影响文本描述的程度"
            },
            "ddim_steps": {
                "type": int,
                "range": [1, 50],
                "default": 16,
                "explanation": "生成图像的步数; 过高可能会超时"
            },
            "use_rephraser": {
                "type": bool,
                "default": True,
                "explanation": "开启中文prompt扩写"
            },
            "use_sr": {
                "type": bool,
                "default": True,
                "explanation": "开启AIGC超分; true：文生图+AIGC超分; false：文生图;"
            },
            "sr_seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "超分模型随机种子; 当use_sr开启时有效;"
            },
            "sr_strength": {
                "type": float,
                "range": [0.0, 1.0],
                "step": 0.1,
                "default": 0.4,
                "explanation": "只在超分模型生效"
            },
            "sr_scale": {
                "type": float,
                "range": [1, 30],
                "step": 0.1,
                "default": 3.5,
                "explanation": "在超分模型上，影响文本描述的程度"
            },
            "sr_steps": {
                "type": int,
                "range": [1, 50],
                "step": 1,
                "default": 10,
                "explanation": "超分模型生成图像的步数；"
            },

            "controlnet__type": {
                "type": str,
                "choices": ["canny", "depth", "pose"],
                "default": "canny",
                "explanation": "controlnet保持构图的方案，canny轮廓边缘/depth景深/pose人物姿态"
            },
            "controlnet__strength": {
                "type": float,
                "range": [0.0, 1.0],
                "default": 0.4,
                "explanation": "controlnet强度, 为0的时候基本没有物体参考"
            }
        },

    "inpainting_eraser":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "mask_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "scale": {
                "type": float,
                "range": [1, 20],
                "default": 7,
                "explanation": "影响文本描述的程度"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": 0,
                "explanation": "随机种子"
            },
            "steps": {
                "type": int,
                "range": [1, 50],
                "default": 30,
                "explanation": "生成图像的步数"
            },
            "dilate_size": {
                "type": int,
                "range": [1, 100],
                "default": 15,
                "explanation": "mask膨胀半径"
            },
            "strength": {
                "type": float,
                "range": [0.0, 1.0],
                "default": 0.8,
                "explanation": "越小越接近原图，越大越接近文本控制，如果设成0就和原图一模一样"
            },
            "quality": {
                "type": str,
                "choices": ["H", "M", "L"],
                "default": "M",
                "explanation": "质量参数，默认为M。H，质量最高，速度稍慢；M，质量中等，速度一般 L；质量较低，速度最快"
            }
        },

    "inpainting_edit":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "mask_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "prompt": {
                "type": str,
                "default": "换成水彩图画的风格",
                "explanation": "正向词"
            },
            "scale": {
                "type": float,
                "range": [1, 20],
                "default": 5,
                "explanation": "影响文本描述的程度"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子"
            },
            "steps": {
                "type": int,
                "range": [1, 50],
                "default": 25,
                "explanation": "生成图像的步数"
            }
        },

    "outpainting__ratio":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "prompt": {
                "type": str,
                "default": "",
                "explanation": "正向词"
            },
            "scale": {
                "type": float,
                "range": [1, 20],
                "default": 7.0,
                "explanation": "影响文本描述的程度"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": 0,
                "explanation": "随机种子"
            },
            "steps": {
                "type": int,
                "range": [1, 50],
                "default": 30,
                "explanation": "采样步数，生成图像的精细程度，越大效果可能更好，但相应的耗时会剧增"
            },
            "strength": {
                "type": float,
                "range": [0, 1.0],
                "default": 0.8,
                "explanation": "越小越接近原图，越大越接近文本控制，如果设成0就和原图一模一样"
            },
            "top": {
                "type": float,
                "range": [0, 1.0],
                "default": 0.1,
                "explanation": "向上扩展比例"
            },
            "bottom": {
                "type": float,
                "range": [0, 1.0],
                "default": 0.1,
                "explanation": "向下扩展比例"
            },
            "left": {
                "type": float,
                "range": [0, 1.0],
                "default": 0.1,
                "explanation": "向左扩展比例"
            },
            "right": {
                "type": float,
                "range": [0, 1.0],
                "default": 0.1,
                "explanation": "向右扩展比例"
            }
        },

    "outpainting__canvas":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "canvas_image": {
                "type": Image,
                "default": "",
                "explanation": "画布"
            },
            "prompt": {
                "type": str,
                "default": "",
                "explanation": "正向词"
            },
            "scale": {
                "type": float,
                "range": [1, 20],
                "default": 7.0,
                "explanation": "影响文本描述的程度"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子"
            },
            "steps": {
                "type": int,
                "range": [1, 50],
                "default": 30,
                "explanation": "采样步数，生成图像的精细程度，越大效果可能更好，但相应的耗时会剧增"
            },
            "strength": {
                "type": float,
                "range": [0, 1.0],
                "default": 0.8,
                "explanation": "越小越接近原图，越大越接近文本控制，如果设成0就和原图一模一样"
            }
        },

    "clearer":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "model_quality": {
                "type": list,
                "choices": ["HQ", "MQ", "LQ"],
                "default": "MQ",
                "explanation": "选取哪种模型进行超分，LQ适用于低质量图片，HQ适用于高质量图片。"
            },
            "result_format": {
                "type": list,
                "choices": ["png", "jpeg"],
                "default": "png",
                "explanation": "0 代表结果图片为png格式，1 代表结果图片为jpeg格式"
            },
            "jpg_quality": {
                "type": int,
                "range": [0, 100],
                "default": 95,
                "explanation": "值越高代表生成jpg图片的质量越高"
            }
        },

    "clearer_lqir":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "resolution_boundary": {
                "type": list,
                "choices": ["144p", "240p", "360p", "480p", "540p", "720p", "1080p", "2k"],
                "default": "2k",
                "explanation": "图片分辨率 原分辨率低于选项，内部走超分，原分辨率高于选项，内部走模糊；''144p': [192, 144]; '240p': [320, 240]; '360p': [480, 360]; '480p': [640, 480]; '540p': [960, 540]; '720p': [1280, 720]; '1080p': [1920, 1080]; '2k': [2048, 1152]'"
            },
            "enable_hdr": {
                "type": bool,
                "default": False,
                "explanation": "是否开启hdr能力"
            },
            "enable_wb": {
                "type": bool,
                "default": False,
                "explanation": "是否开启白平衡能力"
            },
            "result_format": {
                "type": list,
                "choices": ["png", "jpeg"],  # 0 代表结果图片为png格式；1 代表结果图片为jpeg格式
                "default": "jpeg",
                "explanation": "结果图片格式"
            },
            "hdr_strength": {
                "type": float,
                "range": [0, 1.0],
                "default": 1.0,
                "explanation": "值越高代表生成jpg图片的质量越高"
            }
        },

    "picture_seg":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "enhance_edge": {
                "type": int,
                "range": [0, 2],
                "default": 0,
                "explanation": "边缘增强强度"
            },
            "output_mask": {
                "type": bool,
                "default": True,
                "explanation": "是否输出mask图"
            },
            "mask_contrary": {
                "type": bool,
                "default": False,
                "explanation": "抠图mask是否反相"
            }
        },

    "product_repaint":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "positive_prompt": {
                "type": str,
                "default": "",
                "explanation": "正向词；英文会好些？"
            },
            "seg_prompt": {
                "type": str,
                "default": "",
                "explanation": "自动扣图-指定物体；默认就会自动抠出主体，一般无需输入。图片内有多个不同的物体时，必要时可通过提示抠出需要的物体"
            },
            "fixed_positive_prompt": {
                "type": str,
                "default": "masterpiece,realistic,photography,product,8K,highres,best quality,bright,ultra detail,high detail,foreground,correct projection,",
                "explanation": "固定积极提示词"
            },
            "negative_prompt": {
                "type": str,
                "default": "(human,animal,person,character,girl,boy,old,alien,skeleton,figure,doll,bird:1.1),noise,film grain,dirty,caustics,orange ray,magic,fantasy,fog,outline,simple line,cartoon,anime,comic,",
                "explanation": "负面提示词"
            },
            "fixed_negative_prompt": {
                "type": str,
                "default": "(nsfw:1.1),(worst quality,low quality:1.1),jpeg,jpg,normal quality,low resolution,lowres,watermark,wrong lighting,wrong projection,(blurry:1.1),(blurry background:1.2),bokeh,(Depth of field:1.2),dof,melt,(blur:1.2),blur background,illogical,horror, american,logo,text,word,title,headline,",
                "explanation": "固定负面提示词"
            },

            "product_weight": {
                "type": float,
                "range": [0, 1.3],
                "default": 0.85,
                "explanation": "产品还原强度。范围：0~1.3 （注意：超过1.3会报错）；默认已开启光影变化，产品还原程度。越低越容易受氛围、环境的光影影响"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子"
            },
            "product_safe_switch": {
                "type": bool,
                "default": False,
                "explanation": "产品还原度-安全模式；默认：false；开启后，强制还原产品细节。消除产品的任何光影变化。（与环境融合度有所下降）"
            },
            "product_edge_weight": {
                "type": float,
                "range": [0, 1],
                "default": 0,
                "explanation": "产品与环境分离程度；默认：0.0；范围：0~1（注意：数值过高时，高概率让产品悬空）；如果发现产品边缘有畸形，或有异常粘连时。可以调到0.1~0.2"
            },

            # mask
            "markdown__mask": {
                "type": "markdown",
                "default": "### 遮罩控件"  # 第8个前端控件
            },
            "switch__mask": {
                "type": bool,
                "default": False,  # 第9个前端控件
                "explanation": "switch__mask",
                "select_components": {
                    True: {
                        "mask_invert_switch": {
                            "type": bool,
                            "default": True,
                            "explanation": "遮罩图片反转，默认开启，反转输入遮罩图; 默认：true"  # 第10个前端控件
                        },
                        "mask_image_input": {
                            "type": Image,
                            "default": "",
                            "explanation": "遮罩蒙版图片"  # 11
                        }
                    },
                    False: {}
                }
            },
            # ref
            "markdown__ref": {
                "type": "markdown",
                "default": "### 参考图控件"  # 12
            },
            "switch__ref": {
                "type": bool,
                "default": False,
                "explanation": "switch__ref",  # 13
                "select_components": {
                    True: {
                        "ref_image_input": {
                            "type": Image,
                            "default": "",
                            "explanation": "参考图"  # 14
                        },
                        "ref_weight": {
                            "type": float,
                            "range": [0, 1],
                            "default": 0.75,
                            "explanation": "参考图强度，0~2（注意：保持在0~1之间最佳）"  # 15
                        },
                        "ref_end_at": {
                            "type": float,
                            "range": [0, 1],
                            "default": 0.75,
                            "explanation": "参考图引导结束时间；范围：0~1；参考图引导的结束时间，1=完整引导，0.5=生成到50%时结束引导，让模型自由发挥，获得更好的细节"
                            # 16
                        }
                    },
                    False: {}
                }
            },
            # composition
            "markdown__composition": {
                "type": "markdown",
                "default": "### 构图控件"  # 17
            },
            "switch__composition": {
                "type": bool,
                "default": False,
                "explanation": "switch__composition",  # 18
                "select_components": {
                    True: {
                        "composition_type": {
                            "type": list,
                            "choices": ["", "origin", "auto", "manual"],
                            "default": "",
                            "explanation": "构图模式",  # 19
                            "choices_components": {
                                "": {},
                                "origin": {
                                    "longer_side": {
                                        "type": int,
                                        "range": [768, 4000],
                                        "default": 1600,
                                        "step": 8,
                                        "explanation": "输出分辨率，默认：1600；按产品输入图的长边缩放分辨率，保持原图比例，（推荐输入能被8整除的数，例如：768，1024，1280，1440，1600，2000···）仅影响输出分辨率，不影响生图过程"
                                        # 20
                                    }
                                },
                                "auto": {
                                    "auto__canvas_width": {
                                        "type": int,
                                        "range": [768, 4000],
                                        "default": 1000,
                                        "explanation": "画布宽度（像素）"  # 21
                                    },
                                    "auto__canvas_height": {
                                        "type": int,
                                        "range": [768, 4000],
                                        "default": 1000,
                                        "explanation": "画布高度（像素）"  # 22
                                    },
                                    "auto_offset_x": {
                                        "type": int,
                                        "range": [0, 100],
                                        "default": 50,
                                        "explanation": "x轴偏移（百分比）"  # 23
                                    },
                                    "auto_offset_y": {
                                        "type": int,
                                        "range": [0, 100],
                                        "default": 50,
                                        "explanation": "y轴偏移（百分比）"  # 24
                                    },
                                    "auto_scale": {
                                        "type": float,
                                        "range": [0, 1],
                                        "default": 0.7,
                                        "explanation": "scale大小（百分比）"  # 25
                                    }
                                },
                                "manual": {
                                    "manual__canvas_width": {
                                        "type": int,
                                        "range": [768, 4000],
                                        "default": 1000,
                                        "explanation": "画布宽度（像素）"  # 26

                                    },
                                    "manual__canvas_height": {
                                        "type": int,
                                        "range": [768, 4000],
                                        "default": 1000,
                                        "explanation": "画布高度（像素）"  # 27
                                    },
                                    "offset_x": {
                                        "type": int,
                                        "range": [0, 1000],
                                        "default": 0,
                                        "explanation": "x轴偏移（像素）"  # 28
                                    },
                                    "offset_y": {
                                        "type": int,
                                        "range": [0, 1000],
                                        "default": 0,
                                        "explanation": "y轴偏移（像素）"  # 29
                                    },
                                    "crop_prodcut_switch": {
                                        "type": bool,
                                        "default": True,
                                        "explanation": "# 自动裁切至商品大小；默认：true (手动构图开启时，该字段才生效可选）；true：裁剪至商品大小；false：保持输入图片大小"
                                        # 30
                                    }
                                }
                            }
                        }
                    },
                    False: {}
                }
            },
            # light
            "markdown__light": {
                "type": "markdown",
                "default": "### 光源控件"  # 31
            },
            "switch__light": {
                "type": bool,
                "default": False,
                "explanation": "switch__light",  # 32
                "select_components": {
                    True: {
                        "light_type": {
                            "type": list,
                            "choices": ["", "preset", "upload"],
                            "default": "",
                            "explanation": "光源模式",  # 33
                            "choices_components": {
                                "": {},
                                "preset": {
                                    "light_position": {
                                        "type": str,
                                        "choices": ["Left Light", "Right Light", "Top Light", "Bottom Light",
                                                    "Top Left Light", "Top Right Light",
                                                    "Bottom Left Light", "Bottom Right Light"],  # 34
                                        "default": "Top Left Light",
                                        "explanation": '''预设光源类型， 左光源："Left Light"；右光源："Right Light"；顶光源："Top Light"；底光源："Bottom Light"；
                                                          左上光源："Top Left Light" 【开启预设光后默认】；# 右上光源："Top Right Light"；
                                                          左下光源："Bottom Left Light"；右下光源："Bottom Right Light"'''
                                    }
                                },
                                "upload": {
                                    "light_image_input": {
                                        "type": Image,
                                        "default": "",
                                        "explanation": "遮罩蒙版图片"  # 35
                                    }
                                }
                            }
                        }
                    },
                    False: {}
                }
            }
        },

    "dressing":
        {
            "model_image": {
                "type": Image,
                "default": "",
                "explanation": "模特图"
            },
            "protect_mask_image": {
                "type": Image,
                "default": "",
                "explanation": "模特保护区域mask图"
            },
            "garment_image": {
                "type": Image,
                "default": "",
                "explanation": "服装图，当前仅支持配置一件服装，可以是上衣、裤子、鞋子或帽子其中之一"
            },
            "do_sr": {
                "type": bool,
                "default": True,
                "explanation": "是否对结果进行超分处理 默认值：true"
            },
            "seed": {
                "type": int,
                "range": [-1, 2 ** 32 - 1],
                "default": -1,
                "explanation": "随机种子参数，默认为-1，表示系统随机生成seed 默认值：-1"
            },
            "keep_head": {
                "type": bool,
                "default": True,
                "explanation": "是否保持模特原图的头（包括发型） 默认值：true"
            },
            "keep_hand": {
                "type": bool,
                "default": True,
                "explanation": "是否保持模特原图的手 默认值：true"
            },
            "keep_foot": {
                "type": bool,
                "default": True,
                "explanation": "是否保持模特原图的足 默认值：true"
            },
            "num_steps": {
                "type": int,
                "range": [25, 50],
                "default": 50,
                "explanation": "模型推理步数，和算法效果、处理时间相关 默认值：50 取值范围： [25, 50]"
            },
            "keep_upper": {
                "type": bool,
                "default": False,
                "explanation": "是否保持模特原图的上装 默认值：false"
            },
            "keep_lower": {
                "type": bool,
                "default": False,
                "explanation": "是否保持模特原图的下装 默认值：false"
            },
            "tight_mask": {
                "type": str,
                "choices": ["tight", "loose", "bbox"],
                "default": "loose",
                "explanation": "模特图遮挡区域范围；tight: 上窄下窄 loose: 上窄下宽（默认） bbox: 上宽下宽"
            },
            "p_bbox_iou_ratio": {
                "type": float,
                "range": [0.1, 0.5],
                "step": 0.1,
                "default": 0.3,
                "explanation": "当画面有多个人时，每个人的bbox与主体相交的比例；默认值：0.3；取值范围：[0.1, 0.5]"
            },
            "p_bbox_expand_ratio": {
                "type": float,
                "range": [1.0, 1.5],
                "step": 0.1,
                "default": 1.1,
                "explanation": "bbox在inference时扩大的比例；默认值：1.1；取值范围：[1.0, 1.5]"
            },
            "max_process_side_length": {
                "type": int,
                "range": [1080, 4096],
                "step": 0.1,
                "default": 4096,
                "explanation": "当输入图像时，最大的边长若超过该数值，会先resize到图像到该最大边长；默认值：1920；取值范围：[1080, 4096]"
            }
        },

    "image_correction":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            }
        },

    "diy__ai_product_image":
        {
            "input_image": {
                "type": Image,
                "default": "",
                "explanation": ""
            },
            "picture_to_text_prompt": {
                "type": str,
                "default": "用一段流畅简洁精炼的文字描述这张商品展示图，你需要重点描述这个产品的名称、类型、形状（瓶/罐/枝/根/件/条）、颜色、打开关闭状态、拍摄角度、外部内部结构、位于图片中的位置、颜色浅淡、明暗等，同时需要重点描述背景的展示环境、背景颜色、光影、明暗等。",
                "explanation": "图片解读的prompt"
            },
            "description_to_label_prompt": {
                "type": str,
                "default": """这张图是个商品展示图，如果要将这个图作为小红书封面，你需要结合这个图中的产品的类型、特征，为这个图添加一个吸引人的大标题和小标题。然后结合这个图中的产品的类型、格调、形状、颜色，结合展示图的背景环境、背景颜色，设计添加到背景的标题的文字的合适的颜色、大小、位置、字体等。需要用一段流畅的话描述，比如：“图片背景空白区域写有小红书爆款风格的网感艺术大字“吹风机界的纳米水光针”，具有吸引力，字体酷炫，另外也有小字“秒吹干！”，配合一些吹动的风等涂鸦线条，可爱充满活力。”\n\n
# 这个商品展示图描述如下：
{image_description}""",
                "explanation": "根据图片解读信息生成添加的文字的prompt。"
            },
            "ai_img_prompt": {
                "type": str,
                "default": "小红书封面海报。{label_text}{image_description}",
                "explanation": "文生图的prompt，添加的文字+图片解读->AI生图"
            },
            "text_seed_edit_prompt": {
                "type": str,
                "default": "美化图片。",
                "explanation": "美化图片的prompt"
            },
            "replace_smaller_ratio": {
                "type": float,
                "default": 1.0,
                "range": [0, 1],
                "step": 0.01,
                "explanation": "产品实体替换到背景时的缩放比例"
            }
        },

    "picture_to_text__minicpm": {
        "input_image": {
            "type": Image,
            "default": "",
            "explanation": ""
        },
        "prompt": {
            "type": str,
            "default": "",
            "explanation": ""
        }
    },

    "picture_to_text__fangzhou": {
        "input_image": {
            "type": Image,
            "default": "",
            "explanation": ""
        },
        "prompt": {
            "type": str,
            "default": "",
            "explanation": ""
        },
        "model": {
            "type": list,
            "choices": ["Doubao-vision-pro-32k-241028", "Doubao-vision-lite-32k"],
            "default": "Doubao-vision-pro-32k-241028",
            "explanation": ""
        },
    },

    "text_to_video_s20_pro": {
        "prompt": {
            "type": str,
            "default": "请生成一个唯美的空镜视频",
            "explanation": "生成视频的的提示词，支持中英文，150字符以内，prompt书写参考上方描述"
        },
        "aspect_ratio": {
            "type": list,
            "choices": ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
            "default": "16:9",
            "explanation": "生成视频的尺寸，从以下中选择，会对应不同的分辨率：'16:9'：1280×720（默认） '9:16' ：720×1280 '1:1' ： 960×960 '4:3'：960×720 '3:4' ： 720×960 '21:9' ：1680×720"
        },
        "seed": {
            "type": int,
            "range": [-1, 2 ** 64 - 1],
            "default": -1,
            "explanation": "随机种子，作为确定扩散初始状态的基础，默认 - 1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致. [-1~2 ^ 64 - 1]，默认值：-1   -1时，会随机生成一个种子。其他即为正常取值。"
        },
    },

    "image_to_video_s20_pro": {
        "start_image": {
            "type": Image,
            "default": "",
            "explanation": "首帧图"
        },
        "end_image": {
            "type": Image,
            "default": "",
            "explanation": "尾帧图"
        },
        "prompt": {
            "type": str,
            "default": "手持商品旋转展示",
            "explanation": "生成视频的的提示词，支持中英文，150字符以内，prompt书写参考上方描述"
        },
        "aspect_ratio": {
            "type": list,
            "choices": ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
            "default": "16:9",
            "explanation": "生成视频的尺寸，从以下中选择，会对应不同的分辨率：'16:9'：1280×720（默认） '9:16' ：720×1280 '1:1' ： 960×960 '4:3'：960×720 '3:4' ： 720×960 '21:9' ：1680×720"
        },
        "seed": {
            "type": int,
            "range": [-1, 2 ** 64 - 1],
            "default": -1,
            "explanation": "随机种子，作为确定扩散初始状态的基础，默认 - 1（随机）。若随机种子为相同正整数且其他参数均一致，则生成内容极大概率效果一致. [-1~2 ^ 64 - 1]，默认值：-1   -1时，会随机生成一个种子。其他即为正常取值。"
        },
    },

    "video_generation": {
        "start_image": {
            "type": Image,
            "default": "",
            "explanation": "首帧图"
        },
        "end_image": {
            "type": Image,
            "default": "",
            "explanation": "尾帧图"
        },
        "prompt": {
            "type": str,
            "default": "给我生成一张在未来科技赛博朋克世界的视频。",
            "explanation": "生成视频的的提示词，支持中英文，150字符以内"
        },
        "model": {
            "type": list,
            "choices": [
                "文生视频 | doubao-seedance-1-0-pro-250528",
                "图生视频-首帧 | doubao-seedance-1-0-pro-250528",
                "文生视频 | doubao-seedance-1-0-lite-t2v-250428",
                "图生视频-首帧 | doubao-seedance-1-0-lite-i2v-250428",
                "图生视频-首尾帧 | wan2-1-14b-flf2v-250417"
            ],
            "default": "文生视频 | doubao-seedance-1-0-pro-250528",
            "explanation": ""
        },
        "resolution": {
            "type": list,
            "choices": ["480p", "720p", "1080p"],
            "default": "1080p",
            "explanation": "视频分辨率，枚举值： 480p  720p（默认）"
        },
        "ratio": {
            "type": list,
            "choices": ["keep_ratio", "16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
            "default": "keep_ratio",
            "explanation": "wan2.1-14b-i2v 默认值 keep_ratio, doubao-seaweed 图生视频，默认值：根据所上传图片的比例，自动选择最合适的宽高比。doubao-seedance-1-0-lite-i2v，默认值：根据所上传图片的比例，自动选择最合适的宽高比。16:9  4:3  1:1  3:4  9:16  21:9  9:21  keep_ratio：所生成视频的宽高比与所上传图片的宽高比保持一致。"
        },
        "duration": {
            "type": list,
            "choices": [3, 4, 5, 6, 7, 8, 9, 10],
            "default": 5,
            "explanation": "生成视频时长，单位：秒。枚举值： 5（默认）  10"
        },

        "seed": {
            "type": int,
            "range": [-1, 2 ** 32 - 1],
            "default": -1,
            "explanation": "种子整数，用于控制生成内容的随机性。取值范围：[-1, 2^32-1]之间的整数。当不指定seed值或令seed取值为-1时，会使用随机数替代。改变seed值，是相同的请求获得不同结果的一种方法。对相同的请求使用相同的seed值会产生类似的结果，但不保证完全一致。"
        },
        "camerafixed": {
            "type": bool,
            "default": False,
            "explanation": "是否固定摄像头。枚举值： true：固定摄像头。平台会在用户提示词中追加固定摄像头，实际效果不保证。 false：不固定摄像头。（默认)"
        }
    },

    "diy__auto_text_image_to_video": {
        "input_image": {
            "type": Image,
            "default": "",
            "explanation": "首帧图"
        },
        "image_to_text__prompt": {
            "type": str,
            "elem_id": "diy__auto_text_image_to_video____image_to_text__prompt",
            "default": "详细解读这张图片",
            "explanation": "图生文提示词"
        },
        "image_to_text__model": {
            "type": list,
            "choices": ["Doubao-vision-pro-32k-241028", "Doubao-vision-lite-32k"],
            "default": "Doubao-vision-pro-32k-241028",
            "explanation": "图生文模型"
        },
        "product_name": {
            "type": str,
            "default": "",
            "explanation": "商品名"
        },
        "text_to_text__prompt": {
            "type": str,
            "elem_id": "diy__auto_text_image_to_video____text_to_text__prompt",
            "default": """这是一个 {product_name} 的商品图，你需要结合图片信息，理解要展示的商品主体，然后为这个图片生成一个以它为首帧的{duration}s的视频的视频描述。
输出格式：
# 视频描述：
xxx

------
图片信息如下：{image_description}""",
            "explanation": "生成基于图片生成视频的文字指令，用{image_description}作为上一步图片解读结果的占位符"
        },
        "text_to_text__model": {
            "type": list,
            "choices": ['qianfan | chatglm2-6b-32k',
                        'hunyuan | hunyuan-pro',
                        'hunyuan | hunyuan-turbo',
                        'fangzhou | Doubao-1.5-pro-32k',
                        'fangzhou | Doubao-pro-32k-240828',
                        'fangzhou | Doubao-pro-32k',
                        'fangzhou | Doubao-pro-32k-func',
                        'fangzhou | Doubao-pro-128k',
                        'fangzhou | Doubao-lite-4k',
                        'fangzhou | fangzhou_chat_agent',
                        'fangzhou | Deepseek-V3',
                        'fangzhou | Deepseek-r1-250120',
                        'fangzhou | Deepseek-r1-250528',
                        'qwen2 | qwen2-72b',
                        'donson | glm4:9b-chat-fp16',
                        'donson | qwen:72b-chat-v1.5-fp16',
                        'self | xhs_zhongcao_sft'],
            "default": "fangzhou | Deepseek-r1-250528",
            "explanation": "文生文模型"
        }
    },


    "diy__scene_text_image_to_video": {
        "input_image": {
            "type": Image,
            "default": "",
            "explanation": "首帧图"
        },
        "video_type": {
            "type": list,
            "choices": ["商品效果展示", "商品氛围展示-风格展示", "商品氛围展示-创意展示"],
            "default": "商品效果展示",
            "explanation": "生成视频的类型"
        },
        "product_name": {
            "type": str,
            "default": "",
            "explanation": "商品名"
        },
        "resolution": {
            "type": list,
            "choices": ["480p", "720p", "1080p"],
            "default": "1080p",
            "explanation": "视频分辨率"
        },
        "ratio": {
            "type": list,
            "choices": ["keep_ratio", "16:9", "9:16", "1:1", "4:3", "3:4", "21:9"],
            "default": "keep_ratio",
            "explanation": "视频比例"
        },
        "duration": {
            "type": list,
            "choices": [5, 10],
            "default": 5,
            "explanation": "视频时长"
        },

    },

    "diy__video_split_analyze": {
        "input_video": {
            "type": "video",
            "default": "",
            "explanation": "原视频"
        },
        "prompt": {
            "type": str,
            "default": "帮我解析一下这个视频信息",
            "explanation": "视频生文的指令"
        },
        "mode": {
            "type": list,
            "choices": ["content", "threshold", "adaptive", "histogram"],
            "default": "adaptive",
            "explanation": "'content': 'ContentDetector - 基于内容变化检测场景切换', "
                           "'threshold': 'ThresholdDetector - 基于像素亮度阈值检测', "
                           "'adaptive': 'AdaptiveDetector - 自适应检测，结合多种特征', "
                           "'histogram': 'HistogramDetector - 基于颜色直方图检测'"
        },
        "threshold": {
            "type": float,
            "range": [0, 1],
            "default": 0.3,
            "explanation": "阈值",
            "step": 0.05
        }

    }

}

OUTPUT_SETTINGS = dict()
for key in ['text_to_image', 'image_text_seed_edit', 'image_text_seed_edit_2', 'character_preservation',
            'image_to_image', 'image_to_image2',
            'inpainting_eraser', 'inpainting_edit', 'outpainting__ratio', "clearer", "clearer_lqir", "picture_seg",
            "product_repaint", "dressing", "image_correction", "diy__ai_product_image"]:
    OUTPUT_SETTINGS[key] = {
        "output_images": {
            "type": list,
            "inner_type": Image
        }
    }

# for key in ["diy__video_split_analyze"]:
#     OUTPUT_SETTINGS[key] = {
#         "output_videos": {
#             "type": list,
#             "inner_type": "video"
#         }
#     }

for key in ['text_to_video_s20_pro', 'image_to_video_s20_pro', "video_generation",
            "diy__auto_text_image_to_video", "diy__scene_text_image_to_video",
            "diy__video_split_analyze"
            ]:
    OUTPUT_SETTINGS[key] = {
        "output_video": {
            "type": "video"
        }
    }

# print(OUTPUT_SETTINGS.keys())

output_settings_append = {
    "text_chat_one_turn": {
        "answer": {
            "type": str,
            "default": "...",
            "explanation": "模型回答"
        }
    },

    "text_to_image": {
        "llm_result": {
            "type": str,
            "default": "...",
            "explanation": "prompt优化结果"
        }
    },
    "image_text_seed_edit": {
        "vlm_result": {
            "type": str,
            "default": "...",
            "explanation": "图生文中间结果"
        }
    },
    "image_to_image": {
        "prompt": {
            "type": str,
            "default": "...",
            "explanation": "prompt英文"
        }
    },
    "image_to_image2": {
        "prompt": {
            "type": str,
            "default": "...",
            "explanation": ""
        }
    },
    "diy__ai_product_image": {
        "image_description": {
            "type": str,
            "default": "...",
            "explanation": ""
        },
        "label_text": {
            "type": str,
            "default": "...",
            "explanation": ""
        }
    },

    "picture_to_text__minicpm": {
        "text": {
            "type": str,
            "default": "...",
            "explanation": "图生文结果"
        }
    },
    "picture_to_text__fangzhou": {
        "text": {
            "type": str,
            "default": "...",
            "explanation": "图生文结果"
        }
    },

    "text_to_video": {
        "video_url": {
            "type": str,
            "default": "...",
            "explanation": "文生视频输出视频链接"
        }
    },

    "diy__auto_text_image_to_video": {
        "image_description": {
            "type": str,
            "default": "...",
            "explanation": "图生文结果，首帧图图片描述信息"
        },
        "t2t_answer": {
            "type": str,
            "default": "...",
            "explanation": "文生文结果"
        },
        "image_to_video_query": {
            "type": str,
            "default": "...",
            "explanation": "基于首帧图生成的图文生视频的指令"
        },

    },

    "diy__scene_text_image_to_video": {
        "image_to_text__prompt": {
            "type": str,
            "default": "...",
            "explanation": "图生文指令"
        },
        "image_to_text__model": {
            "type": str,
            "default": "...",
            "explanation": "图生文模型"
        },
        "image_description": {
            "type": str,
            "default": "...",
            "explanation": "图生文结果，首帧图图片描述信息"
        },
        "text_to_text__query": {
            "type": str,
            "default": "...",
            "explanation": "文生文输入"
        },
        "text_to_text__model": {
            "type": str,
            "default": "...",
            "explanation": "文生文模型"
        },
        "image_to_video_query": {
            "type": str,
            "default": "...",
            "explanation": "文生文结果"
        },

    },
    "diy__video_split_analyze": {
        "video_url": {
            "type": str,
            "default": "...",
            "explanation": "视频上传到obs的链接"
        },
        "scenes_count": {
            "type": str,
            "default": "...",
            "explanation": "视频切割片段数目"
        },
        "scenes_text": {
            "type": str,
            "default": "...",
            "explanation": "视频切割解析后的文本"
        }
    }
}

for k, v in output_settings_append.items():
    if k in OUTPUT_SETTINGS:
        OUTPUT_SETTINGS[k].update(output_settings_append.get(k))
    else:
        OUTPUT_SETTINGS[k] = v

# for k, v in OUTPUT_SETTINGS.items():
#     print(k)
#     print(v)
