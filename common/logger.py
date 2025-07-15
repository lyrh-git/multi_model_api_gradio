import logging

def setup_logging(filename):

    log_dir_path = "/Users/admin/program/projects/multi_model_api_gradio/log/"
    # 创建日志记录器
    logger = logging.getLogger(f'{filename}')
    logger.setLevel(logging.INFO)
    # 创建一个处理器，用于写入日志文件
    file_handler = logging.FileHandler(f'{log_dir_path}/{filename}.log', mode='a', encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # 创建日志格式器，设置为 JSON 格式
    formatter = logging.Formatter('%(asctime)s %(message)s')
    file_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    return logger