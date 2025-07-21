import PIL
import gradio
import gradio as gr
import numpy as np
from PIL import Image
from gradio import Brush

from config import SETTINGS, OUTPUT_SETTINGS
from front_function_map import get_tab_function

def tab_name_en_zh_map(tab_en):
    en_zh = {
        "text_chat_one_turn": "文生文 - 单轮对话 - 本地",
        "text_to_image": "文生图 - 即梦",
        "image_text_seed_edit": "全局精调 - 即梦",
        "image_text_seed_edit_2": "图生图（实时生图） - 即梦",
        "character_preservation": "角色特征保持 - 即梦",
        "image_to_image": "图生图 xl pro - 即梦",
        "image_to_image2": "图生图2.0 - 即梦",
        "inpainting_eraser": "局部涂抹 - 即梦",
        "inpainting_edit": "局部精调 - 即梦",
        "outpainting__ratio": "扩图（比例） - 即梦",
        "clearer": "清晰化 - 即梦",
        "clearer_lqir": "图像增强 - 即梦",
        "picture_seg": "抠图 - 即梦",
        "product_repaint": "AI商品图 - 即梦",
        "dressing": "图片换装 - 即梦",
        "image_correction": "图片方向矫正",
        "diy__ai_product_image": "自定义 - 商品图加字",

        "picture_to_text__minicpm": "图生文 - minicpm",
        "picture_to_text__fangzhou": "图生文 - fangzhou",

        "text_to_video_s20_pro": "文生视频S2.0 pro - 即梦",
        "image_to_video_s20_pro": "图生视频S2.0 pro - 即梦",

        "video_generation": "视频生成 - 方舟",

        "diy__auto_text_image_to_video": "自定义 - 图生视频",
        "diy__scene_text_image_to_video": "自定义 - 图生视频（分场景）",
        "diy__video_split_analyze": "自定义 - 视频切割解析"
    }
    return en_zh.get(tab_en, None)


def draw_choices_components(choice_component, choices_components_dict, input_parameters, default_value):
    all_components = list()
    for choice, inner_components_dict in choices_components_dict.items():
        with gr.Row():
            for k, v in inner_components_dict.items():
                o_components = draw_each_component(k, v, input_parameters=input_parameters)
                if not isinstance(o_components, list):
                    o_components = [o_components]
                for o_component in o_components:
                    if k not in input_parameters:
                        print(f"generate {len(input_parameters)} input parameter: {k} {o_component}")
                        input_parameters[k] = o_component
                    o_component.visible = True if choice == default_value else False
                    # o_component.visible = True
                    all_components.append(o_component)

    def choice_change(st):
        out_data = list()
        for choice, inner_components_dict in choices_components_dict.items():
            for k, v in inner_components_dict.items():
                out_data.append(gr.update(visible=False if choice != st else True))
            if not choice or not st:
                for _k, _v in inner_components_dict.items():
                    out_data.append(gr.update(visible=False))

        return out_data

    choice_component.change(choice_change, [choice_component], all_components)

    return all_components

def draw_select_component(select_component, components_dict, input_parameters):
    '''折叠面板'''
    all_components = list()
    for select, inner_components_dict in components_dict.items():
        with gr.Column():
            for k, v in inner_components_dict.items():
                o_components = draw_each_component(k, v, input_parameters=input_parameters)
                if not isinstance(o_components, list):
                    o_components = [o_components]
                for o in o_components:
                    if k not in input_parameters:
                        print(f"generate {len(input_parameters)} input parameter: {k} {o}")
                        input_parameters[k] = o
                    o.visible = False
                    all_components.append(o)
    def select_change(st):
        out_data = list()
        for select, inner_components_dict in components_dict.items():
            for k, v in inner_components_dict.items():
                out_data.append(gr.update(visible=False if select != st else True))
                if "choices_components" in v:
                    out_data.append(gr.update(visible=False))  # 每次选中单选，单选下面的组件除了复选框都全部隐藏
                    for _choice, _choice_items in v.get("choices_components", {}).items():
                        for _k, _v in _choice_items.items():
                            out_data.append(gr.update(visible=False))  # 每次选中单选，单选下面的组件除了复选框都全部隐藏

        return out_data
    select_component.change(select_change, [select_component], all_components)
    return all_components


def draw_each_component(key, info, with_mask=False, input_parameters=None):
    t = info.get("type")
    component, components = None, list()

    if "choices" in info:
        component = gr.Dropdown(choices=info.get("choices"), value=info.get("default"),
                                type="value", label=key, info=info.get("explanation", ""))
        if "choices_components" in info:
            if input_parameters is not None and key not in input_parameters:
                print(f"generate {len(input_parameters)} input parameter: {key} {component}")
                input_parameters[key] = component
            components = [component] + draw_choices_components(component, info["choices_components"], input_parameters, default_value=info.get("default"))
            # components = draw_choices_components(component, info["choices_components"], input_parameters, default_value=info.get("default"))
    else:
        if t == "markdown":
            component = gr.Markdown(info.get("default"))
        elif t == str:
            component = gr.Textbox(value=info.get("default"), label=key,
                                   placeholder=info.get("default"), info=info.get("explanation", ""))
            if "elem_id" in info:
                component.elem_id = info.get("elem_id")

        elif t in [int, float]:
            if "range" in info:
                component = gr.Slider(value=info.get("default"), minimum=info.get("range")[0], maximum=info.get("range")[1],
                                      step=info.get("step") if "step" in info else 1 if t == int else 0.1,
                                      label=key, info=info.get("explanation", ""))
        elif t == bool:
            component = gr.Checkbox(value=info.get("default"), label=key, info=info.get("explanation", ""))
            if "select_components" in info:
                if input_parameters is not None and key not in input_parameters:
                    print(f"generate {len(input_parameters)} input parameter: {key} {component}")
                    input_parameters[key] = component  # 先赋个值占顺序
                components = [component] + draw_select_component(component, info["select_components"], input_parameters)
                # components = draw_select_component(component, info["select_components"], input_parameters)

        elif t in [PIL.Image, gradio.components.image.Image]:
            if with_mask and "input" in key:  # 局部涂抹，局部精调都需要；图生图（需要接抠实体，不是mask）
                component = gr.ImageMask(type="numpy", sources=["upload"],
                                         width=500, height=500,
                                         # brush=Brush(colors=["rgba(0,0,0,0.5)"], color_mode="fixed"))
                                         brush=Brush(colors=["#FFFFFF"], color_mode="fixed"))
            else:
                component = gr.Image(type="pil", height=200, width=200,
                                     label=key, placeholder=info.get("explanation"))

        elif t == list:
            print(info)
            if info.get("inner_type") in [PIL.Image, gradio.components.image.Image]:
                print("here is image list")
                component = gr.Gallery(label="Output Images", elem_id=key)
            elif info.get("inner_type") in ["video"]:
                print("here is video list")
                component = gr.Gallery(label="Output Videos", elem_id=key, allow_preview=True)
        elif t == "video":
            component = gr.Video(show_download_button=True)
        else:
            print("Error component: ", key, info, t)

    if component:
        if input_parameters is not None and key not in input_parameters:
            print(f"generate {len(input_parameters)} input parameter: {key} {component}")
            input_parameters[key] = component
    return component if not components else components


def get_mask(canvas):
    # print(im.keys())  # composite是合一起  layers   background
    mask_array = canvas["layers"][0]
    for x in canvas["layers"][1:]:
        mask_array += x
    mask_array = mask_array / len(canvas["layers"])

    input_width, input_height = mask_array.shape[1], mask_array.shape[0]
    print(f"Mask size - width: {input_width}, height: {input_height}")
    if mask_array.shape[-1] == 4:  # RGBA格式
        # 将涂抹区域设为白色，其他区域设为黑色
        mask_binary = np.zeros((input_height, input_width), dtype=np.uint8)
        mask_binary[mask_array[:, :, 3] > 0] = 255  # 只考虑alpha通道
    else:  # RGB格式
        # 将涂抹区域设为白色，其他区域设为黑色
        mask_binary = np.zeros((input_height, input_width), dtype=np.uint8)
        mask_binary[np.any(mask_array[:, :, :3] > 0, axis=-1)] = 255

    return Image.fromarray(mask_binary.astype('uint8'))


def get_background(canvas):
    return Image.fromarray(canvas["background"].astype('uint8'))

def draw_tab_components():
    with gr.Blocks(title='多模态API', css="css/front_style.css") as demo:

        gr.Markdown("## 多模态API")

        for tab_name in SETTINGS.keys():
            if not tab_name_en_zh_map(tab_name):
                continue
            print(f"\n======\nDrawing tab {tab_name}")

            with gr.Tab(tab_name_en_zh_map(tab_name)):
                with gr.Row():
                    with gr.Column():
                        info = SETTINGS.get(tab_name)
                        input_parameters = dict()
                        if any(["image" in k for k in info.keys()]):  # 图片放在最前面
                            if any([_k in info for _k in ["mask_image"]]):
                                image_mask = draw_each_component("input_image", info.get("input_image"), with_mask=True)  # 原图画布
                                with gr.Row():  # 排版涂抹的图在上预览在下
                                    background_image = gr.Image(type="pil", height=200, width=200, label="原图")
                                    preview_layer = gr.Image(type="pil", height=200, width=200,
                                                             label="mask预览")  # mask展示

                                image_mask.change(get_mask, outputs=preview_layer, inputs=[image_mask],
                                                  show_progress="hidden")
                                image_mask.change(get_background, outputs=background_image, inputs=[image_mask],
                                                  show_progress="hidden")

                                input_parameters["input_image"] = background_image
                                input_parameters["mask_image"] = preview_layer

                                with gr.Row():
                                    for k, v in info.items():
                                        if "image" in k and k not in ["input_image", "mask_image"]:
                                            # input_parameters[k] = draw_each_component(k, v, with_mask=False)
                                            draw_each_component(k, v, with_mask=False, input_parameters=input_parameters)
                                            if input_parameters[k] is None:
                                                print(k)
                            else:
                                with gr.Row():
                                    for k, v in info.items():
                                        if "image" in k:
                                            # input_parameters[k] = draw_each_component(k, v, with_mask=False)
                                            draw_each_component(k, v, with_mask=False, input_parameters=input_parameters)
                                            if input_parameters[k] is None:
                                                print(k)

                        output_parameters = dict()
                        with gr.Column():
                            for k, v in info.items():
                                if "image" not in k:
                                    # input_parameters[k] = draw_each_component(k, v)
                                    draw_each_component(k, v, input_parameters=input_parameters)
                                    if input_parameters[k] is None:
                                        print(k)
                        tab_func = get_tab_function(tab_name)  # 获取调用api的方法
                        btn = gr.Button("运行")



                    with gr.Column():
                        # output_images = gr.Gallery(label="Output Images", elem_id="output_gallery")
                        if tab_name in OUTPUT_SETTINGS:
                            for k, v in OUTPUT_SETTINGS.get(tab_name).items():
                                print(k, v)
                                output_parameters[k] = draw_each_component(k, v, with_mask=False)
                # if tab_name not in OUTPUT_SETTINGS:
                #     btn.click(tab_func, inputs=list(input_parameters.values()), outputs=output_images)
                # else:
                #     # print([output_images] + list(output_parameters.values()))
                #     btn.click(tab_func, inputs=list(input_parameters.values()), outputs=[output_images] + list(output_parameters.values()))
                # print(list(output_parameters.values()))
                btn.click(tab_func, inputs=list(input_parameters.values()), outputs=list(output_parameters.values()))
                # btn_input = list(input_parameters.values())
                # btn_input = btn_input[0] if len(btn_input) == 1 else btn_input
                # btn_output = list(output_parameters.values())
                # btn_output = btn_output[0] if len(btn_output) == 1 else btn_output
                # print(btn_input)
                # print(btn_output)
                # btn.click(tab_func, inputs=btn_input, outputs=btn_output)

            print(f"Tab {tab_name} input parameters count: {len(input_parameters)}")
            print(f"Tab {tab_name} output arameters count: {len(output_parameters)}")

    return demo

if __name__ == '__main__':
    # draw_tab_components().launch(server_name="192.168.20.232", server_port=8888, share=True)
    # draw_tab_components().launch(server_name="0.0.0.0", server_port=8888, share=True)
    # draw_tab_components().launch(server_name="0.0.0.0", server_port=8800, share=True)
    draw_tab_components().launch(server_name="192.168.20.113", server_port=8888, share=True)