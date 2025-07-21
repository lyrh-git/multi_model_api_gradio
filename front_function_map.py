import re

from config import SETTINGS, OUTPUT_SETTINGS

from api_sdk.jimeng_sdk import JiMengAPI
from api_sdk.fangzhou_sdk import FangzhouAPI
from api_sdk.volcengine_sdk import VolcengineAPI
from api_sdk.text_sdk import TextAPI
from api_sdk.other_sdk import OtherAPI

from diy_sdk import DiyAPI

from common.ImageHandler import ImageHandler

jimeng_api = JiMengAPI()
other_api = OtherAPI()
fangzhou_api = FangzhouAPI()
image_handler = ImageHandler()
diy_api = DiyAPI()
volcengine_api = VolcengineAPI()
text_api = TextAPI()

def common_get_info(task, ls, pre_keys, key_rename=None):
    if not key_rename:
        key_rename = dict()
    key_names = SETTINGS.get(task).keys()
    info, params = dict(), dict()
    for i, k in enumerate(list(key_names)):
        if k not in pre_keys:
            params[key_rename.get(k, k)] = ls[i]
        else:
            info[key_rename.get(k, k)] = ls[i]
    if params:
        info["params"] = params
    print(f"\n\n\n======\nFinal input info: {info}")
    return info


def common_sort_result(key, result):
    keys = OUTPUT_SETTINGS.get(key).keys()  # 保证按前端页面的顺序输出
    other_result = dict()
    for k in keys:
        other_result[k] = result.get(k, f"Error: can't fetch {k} result.")
    sort_result = list(other_result.values())
    if len(sort_result) == 1:
        sort_result = sort_result[0]
    return sort_result


def handle_text_chat_one_turn(*ls):
    result = text_api.text_chat_one_turn(**common_get_info(task="text_chat_one_turn",
                                                           ls=ls,
                                                           pre_keys=["prompt", "model"]))
    return common_sort_result("text_chat_one_turn", result)


def handle_text_to_image(*ls):  # *ls传不定长参数
    # text_to_image(self, prompt, negative_prompt="", model="文生图2.0L", output_path=None, params=None)
    result = jimeng_api.text_to_image(**common_get_info(task="text_to_image",
                                                        ls=ls,
                                                        pre_keys=["prompt", "negative_prompt", "model"],
                                                        key_rename={"num_generate": "num_images"}))

    return common_sort_result("text_to_image", result)


def handle_image_text_seed_edit(*ls):
    # image_text_seed_edit(self, prompt, input_data, output_path=None, params=None)
    result = jimeng_api.image_text_seed_edit(**common_get_info(task="image_text_seed_edit",
                                                               ls=ls,
                                                               pre_keys=["prompt", "input_image"],
                                                               key_rename={"input_image": "input_data"}))

    return common_sort_result("image_text_seed_edit", result)


def handle_image_text_seed_edit_2(*ls):
    # image_text_seed_edit(self, prompt, input_data, output_path=None, params=None)
    result = jimeng_api.image_text_seed_edit(**common_get_info(task="image_text_seed_edit_2",
                                                               ls=ls,
                                                               pre_keys=["prompt", "input_image"],
                                                               key_rename={"input_image": "input_data"}))

    return common_sort_result("image_text_seed_edit_2", result)


def handle_character_preservation(*ls):
    # character_preservation(self, prompt, input_data, output_path=None, params=None)
    result = jimeng_api.character_preservation(**common_get_info(task="character_preservation",
                                                                 ls=ls,
                                                                 pre_keys=["prompt", "input_image"],
                                                                 key_rename={"input_image": "input_data"}))

    return common_sort_result("character_preservation", result)


def handle_inpainting_eraser(*ls):
    # inpainting_eraser(self, input_data, mask_data, output_path=None, params=None)
    result = jimeng_api.inpainting_eraser(**common_get_info(task="inpainting_eraser",
                                                            ls=ls,
                                                            pre_keys=["prompt", "input_image", "mask_image"],
                                                            key_rename={"input_image": "input_data",
                                                                        "mask_image": "mask_data"}))

    return common_sort_result("inpainting_eraser", result)


def handle_inpainting_edit(*ls):
    # inpainting_edit(self, prompt, input_data, mask_data, output_path=None, params=None)
    result = jimeng_api.inpainting_edit(**common_get_info(task="inpainting_edit",
                                                          ls=ls,
                                                          pre_keys=["prompt", "input_image", "mask_image"],
                                                          key_rename={"input_image": "input_data",
                                                                      "mask_image": "mask_data"}))

    return common_sort_result("inpainting_edit", result)


def handle_outpainting__ratio(*ls):
    # outpainting(self, prompt, input_path, output_path=None, use_type="ratio", ratio_info=None, canvas_info=None)
    info = common_get_info(task="outpainting__ratio",
                           ls=ls,
                           pre_keys=["prompt", "input_image"],
                           key_rename={"input_image": "input_path"})
    info["use_type"] = "ratio"
    info["ratio_info"] = info["params"]
    info.pop("params")

    result = jimeng_api.outpainting(**info)
    return common_sort_result("outpainting__ratio", result)


def handle_outpainting__canvas(*ls):
    # outpainting(self, prompt, input_path, output_path=None, use_type="ratio", ratio_info=None, canvas_info=None)
    info = common_get_info(task="outpainting__canvas",
                           ls=ls,
                           pre_keys=["prompt", "input_image"],
                           key_rename={"input_image": "input_path"})
    info["use_type"] = "canvas"
    info["canvas_info"] = info["params"]
    info["canvas_info"]["canvas_path"] = info["canvas_info"]["canvas_image"]
    info["canvas_info"].remove("canvas_image")
    info.pop("params")

    result = jimeng_api.outpainting(**info)
    return common_sort_result("outpainting__canvas", result)


def handle_image_to_image(*ls):
    # image_to_image(self, prompt, input_data, output_path=None, controlnet_data=None, style_data=None, params=None)
    key_names = SETTINGS.get("image_to_image").keys()
    info, controlnet_data, style_data, params = dict(), dict(), dict(), dict()
    for i, k in enumerate(list(key_names)):
        if "image" in k:
            if "control" in k:
                controlnet_data["controlnet_path"] = ls[i]
            elif "style" in k:
                style_data["style_path"] = ls[i]
            elif "input" in k:
                info["input_data"] = ls[i]
            else:
                info[k] = ls[i]
        elif "control" in k:
            controlnet_data[k] = ls[i]
        elif "style" in k:
            style_data[k] = ls[i]
        elif k in ["prompt"]:
            info[k] = ls[i]
        else:
            params[k] = ls[i]
    if not controlnet_data.get("controlnet_path", None):
        controlnet_data = None
    if not style_data.get("style_path", None):
        style_data = None

    if controlnet_data:
        info["controlnet_data"] = dict()
        for k, v in controlnet_data.items():
            info["controlnet_data"][re.sub("^(controlnet__)", "", k)] = v
    if style_data:
        info["style_data"] = dict()
        for k, v in style_data.items():
            info["style_data"][re.sub("^(style__)", "", k)] = v
    info["params"] = params

    result = jimeng_api.image_to_image(**info)
    return common_sort_result("image_to_image", result)


def handle_image_to_image2(*ls):
    key_names = SETTINGS.get("image_to_image2").keys()
    info, controlnet_data, params = dict(), dict(), dict()
    for i, k in enumerate(list(key_names)):
        if "image" in k:
            if "control" in k:
                controlnet_data["controlnet_path"] = ls[i]
            elif "input" in k:
                info["input_data"] = ls[i]
            else:
                info[k] = ls[i]
        elif "control" in k:
            controlnet_data[k] = ls[i]
        elif k in ["prompt"]:
            info[k] = ls[i]
        else:
            params[k] = ls[i]
    if not controlnet_data.get("controlnet_path", None):
        controlnet_data = None

    if controlnet_data:
        info["controlnet_data"] = dict()
        for k, v in controlnet_data.items():
            info["controlnet_data"][re.sub("^(controlnet__)", "", k)] = v
    info["params"] = params

    result = jimeng_api.image_to_image(**info)
    return common_sort_result("image_to_image2", result)


def handle_clearer(*ls):
    args = common_get_info(task="clearer", ls=ls, pre_keys=["input_image"], key_rename={"input_image": "input_data"})
    result_format_map = {
        "png": 0,
        "jpeg": 1
    }
    if "result_format" in args["params"]:
        args["params"]["result_format"] = result_format_map.get(args["params"]["result_format"], 0)
    result = jimeng_api.clearer(**args)

    return common_sort_result("clearer", result)


def handle_clearer_lqir(*ls):
    args = common_get_info(task="clearer_lqir", ls=ls, pre_keys=["input_image"],
                           key_rename={"input_image": "input_data"})
    result_format_map = {
        "png": 0,
        "jpeg": 1
    }
    if "result_format" in args["params"]:
        args["params"]["result_format"] = result_format_map.get(args["params"]["result_format"], 0)
    result = jimeng_api.clearer_lqir(**args)

    return common_sort_result("clearer_lqir", result)


def handle_picture_seg(*ls):
    args = common_get_info(task="picture_seg", ls=ls, pre_keys=["input_image"],
                           key_rename={"input_image": "input_data", "enhance_edge": "refine_mask"})
    save_mask = args["params"].get("output_mask")
    args["save_mask"] = save_mask
    args["params"].pop("output_mask")

    mask_contrary = args["params"].get("mask_contrary")
    args["params"].pop("mask_contrary")

    result = jimeng_api.picture_seg(**args)

    if save_mask and len(result.get("output_images")) > 1 and mask_contrary:
        image2 = result.get("output_images")[1]
        result["output_images"][1] = image_handler.get_image_contrary(image2)

    return common_sort_result("picture_seg", result)


def handle_product_repaint(*ls):
    positive_prompt = ""
    input_data, mask_data, ref_data, composition_data, light_data, params = dict(), dict(), dict(), dict(), dict(), dict()

    # print("\n\n========\n\n")
    # for a, b in enumerate(ls):
    #     print(f"i {a}, ls[i] {b}")
    # print("\n\n========\n\n")

    i = 0
    for key, value in SETTINGS.get("product_repaint").items():
        # print(f"key {key}, i {i}, ls[i] {ls[i]}")
        if key == "switch__mask":
            if not ls[i]:
                mask_data = None
            i += 1
            for k, v in value.get("select_components", dict()).get(True, dict()).items():
                # print(f"{i} | mask_data[{k}] = {ls[i]}")
                if mask_data is not None:
                    mask_data[k] = ls[i]
                i += 1
        elif key == "switch__ref":
            if not ls[i]:
                ref_data = None
            i += 1
            for k, v in value.get("select_components", dict()).get(True, dict()).items():
                # print(f"{i} | ref_data[{k}] = {ls[i]}")
                if ref_data is not None:
                    ref_data[k] = ls[i]
                i += 1
        elif key == "switch__composition":
            if not ls[i]:
                composition_data = None
            i += 1
            for k, v in value.get("select_components", dict()).get(True, dict()).items():
                if k == "composition_type":
                    if composition_data is not None:
                        # print(f"{i} | composition_data[{k}] = {ls[i]}")
                        composition_data["composition_type"] = ls[i]
                    i += 1
                    for _k, _v in v.get("choices_components", dict()).items():
                        if not _k:
                            continue
                        for __k, __v in _v.items():
                            if composition_data and _k == composition_data["composition_type"]:
                                # print(f"{i} | composition_data[{__k}] = {ls[i]}")
                                if composition_data is not None:
                                    composition_data[re.sub(f"^{_k}__", "", __k)] = ls[
                                        i]  # manual__canvas_height -> canvas_height
                            i += 1
        elif key == "switch__light":
            if not ls[i]:
                light_data = None
            i += 1
            for k, v in value.get("select_components", dict()).get(True, dict()).items():
                if k == "light_type":
                    if light_data is not None:
                        # print(f"{i} | light_data[{k}] = {ls[i]}")
                        light_data["light_type"] = ls[i]
                    i += 1
                    for _k, _v in v.get("choices_components", dict()).items():
                        if not _k:
                            continue
                        for __k, __v in _v.items():
                            if light_data and _k == light_data["light_type"]:
                                # print(f"{i} | light_data[{__k}] = {ls[i]}")
                                if light_data is not None:
                                    light_data[re.sub(f"^{_k}__", "", __k)] = ls[i]
                            i += 1
        elif key == "positive_prompt":
            positive_prompt = ls[i]
            i += 1
        elif key == "input_image":
            input_data = ls[i]
            i += 1
        elif re.search("^markdown__", key):
            i += 1
            continue
        else:
            params[key] = ls[i]
            i += 1

    print(f"\n\n\n___final elements count: {i + 1}")
    print(f"positive_prompt: {positive_prompt}\n"
          f"input_data: {input_data}\n"
          f"mask_data: {mask_data}\n"
          f"ref_data: {ref_data}\n"
          f"composition_data: {composition_data}\n"
          f"light_data: {light_data}\n"
          f"params: {params}\n\n\n"
          )
    result = jimeng_api.product_repaint(positive_prompt=positive_prompt, input_data=input_data,
                                        mask_data=mask_data, ref_data=ref_data,
                                        composition_data=composition_data,
                                        light_data=light_data, params=params)
    return common_sort_result("product_repaint", result)


def handle_dressing(*ls):
    args = common_get_info(task="dressing", ls=ls, pre_keys=["model_image", "garment_image", "protect_mask_image"],
                           key_rename={
                               "model_image": "model_data",
                               "garment_image": "garment_data",
                               "protect_mask_image": "protect_mask_data"
                           }
                           )
    return common_sort_result("dressing", jimeng_api.dressing(**args))


def handle_image_correction(*ls):
    args = common_get_info(task="image_correction", ls=ls, pre_keys=["input_image"],
                           key_rename={"input_image": "input_data"})
    return common_sort_result("image_correction", jimeng_api.image_correction(**args))


def handle_diy__ai_product_image(*ls):
    args = common_get_info(task="diy__ai_product_image", ls=ls, pre_keys=["input_image"],
                           key_rename={"input_image": "input_data"})
    return common_sort_result("diy__ai_product_image", diy_api.ai_product_image(**args))


def handle_picture_to_text__minicpm(*ls):
    # character_preservation(self, prompt, input_data, output_path=None, params=None)
    result = other_api.picture_to_text__minicpm(**common_get_info(task="picture_to_text__minicpm",
                                                                  ls=ls,
                                                                  pre_keys=["input_image", "prompt"],
                                                                  key_rename={
                                                                      "input_image": "image"}))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("picture_to_text__minicpm", result)


def handle_picture_to_text__fangzhou(*ls):
    # character_preservation(self, prompt, input_data, output_path=None, params=None)
    result = fangzhou_api.picture_to_text__fangzhou(**common_get_info(task="picture_to_text__fangzhou",
                                                                      ls=ls,
                                                                      pre_keys=["input_image", "prompt", "model"],
                                                                      key_rename={
                                                                          "input_image": "image"}))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("picture_to_text__fangzhou", result)


def handle_text_to_video_s20_pro(*ls):
    # character_preservation(self, prompt, input_data, output_path=None, params=None)
    result = jimeng_api.text_to_video_s20_pro(**common_get_info(task="text_to_video_s20_pro",
                                                                ls=ls,
                                                                pre_keys=["prompt"]))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("text_to_video_s20_pro", result)


def handle_image_to_video_s20_pro(*ls):
    result = jimeng_api.image_to_video_s20_pro(**common_get_info(task="image_to_video_s20_pro",
                                                                 ls=ls,
                                                                 pre_keys=["prompt", "start_image", "end_image"],
                                                                 key_rename={
                                                                     "start_image": "image_data1",
                                                                     "end_image": "image_data2"
                                                                 }))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("image_to_video_s20_pro", result)


def handle_video_generation(*ls):
    result = volcengine_api.video_generation(**common_get_info(task="video_generation",
                                                               ls=ls,
                                                               pre_keys=["model", "prompt", "start_image", "end_image"],
                                                               key_rename={
                                                                   "start_image": "image_data1",
                                                                   "end_image": "image_data2"
                                                               }))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("video_generation", result)


def handle_diy__auto_text_image_to_video(*ls):
    result = diy_api.auto_text_image_to_video(**common_get_info(task="diy__auto_text_image_to_video",
                                                                ls=ls,
                                                                pre_keys=["input_image",
                                                                          "image_to_text__prompt",
                                                                          "image_to_text__model",
                                                                          "text_to_text__prompt",
                                                                          "text_to_text__model"], ))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("diy__auto_text_image_to_video", result)


def handle_diy__scene_text_image_to_video(*ls):
    result = diy_api.scene_text_image_to_video(**common_get_info(task="diy__scene_text_image_to_video",
                                                                ls=ls,
                                                                pre_keys=["input_image",
                                                                          "video_type"]))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("diy__scene_text_image_to_video", result)

def handle_diy__video_split_analyze(*ls):
    result = diy_api.video_split_analyze(**common_get_info(task="diy__video_split_analyze",
                                                                ls=ls,
                                                                pre_keys=["input_video",
                                                                          "prompt"],
                                                                key_rename={
                                                                    "input_video": "video_data"
                                                                    }
                                                                ))  # config传入的名字与sdk入参名字的映射
    return common_sort_result("diy__video_split_analyze", result)




def get_tab_function(key):
    func_map = {
        "text_chat_one_turn": handle_text_chat_one_turn,

        "text_to_image": handle_text_to_image,
        "image_text_seed_edit": handle_image_text_seed_edit,
        "image_text_seed_edit_2": handle_image_text_seed_edit_2,
        "character_preservation": handle_character_preservation,
        "image_to_image": handle_image_to_image,
        "image_to_image2": handle_image_to_image2,
        "inpainting_eraser": handle_inpainting_eraser,
        "inpainting_edit": handle_inpainting_edit,
        "outpainting__ratio": handle_outpainting__ratio,
        "clearer": handle_clearer,
        "clearer_lqir": handle_clearer_lqir,
        "picture_seg": handle_picture_seg,
        "product_repaint": handle_product_repaint,
        "dressing": handle_dressing,
        "image_correction": handle_image_correction,
        "diy__ai_product_image": handle_diy__ai_product_image,

        "picture_to_text__minicpm": handle_picture_to_text__minicpm,
        "picture_to_text__fangzhou": handle_picture_to_text__fangzhou,

        "text_to_video_s20_pro": handle_text_to_video_s20_pro,
        "image_to_video_s20_pro": handle_image_to_video_s20_pro,

        "video_generation": handle_video_generation,

        "diy__auto_text_image_to_video": handle_diy__auto_text_image_to_video,
        "diy__scene_text_image_to_video": handle_diy__scene_text_image_to_video,
        "diy__video_split_analyze": handle_diy__video_split_analyze
    }
    return func_map.get(key)
