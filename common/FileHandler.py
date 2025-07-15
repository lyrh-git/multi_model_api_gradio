import json
import os
import re
import numpy
import openpyxl
import pandas as pd


class FileHandler:
    def __init__(self):
        pass

    def read_txt(self, path):
        for encoding in ["utf-8", "gbk"]:
            try:
                with open(path, "r", encoding=encoding) as f:
                    text = f.read()
                    return text
            except Exception as e:
                print(e)
        return ""

    def read_txt_lines(self, path):
        for encoding in ["utf-8", "gbk"]:
            try:
                with open(path, "r", encoding=encoding) as f:
                    data = f.readlines()
                    return data
            except Exception as e:
                print(e)
        return list()

    def write_txt(self, data, path, encoding="utf-8"):
        with open(path, "w", encoding=encoding) as f:
            f.write(data)

    def write_txt_lines(self, data, path, encoding="utf-8"):
        with open(path, "w", encoding=encoding) as f:
            f.writelines(data)

    def read_json(self, path):
        for encoding in ["utf-8", "gbk"]:
            try:
                with open(path, "r", encoding=encoding) as f:
                    obj = json.load(f)
                    return obj
            except Exception as e:
                print(e)
        return dict()

    def read_json_lines(self, path):
        objs = list()
        for encoding in ["utf-8", "gbk"]:
            print(encoding)
            try:
                with open(path, "r", encoding=encoding) as f:
                    for x in f:
                        # print(x)
                        obj = json.loads(x)
                        objs.append(obj)
                    return objs
            except Exception as e:
                print(e)
                objs = list()
        return objs

    def write_json(self, data, path, encoding="utf-8"):
        with open(path, "w", encoding=encoding) as f:
            f.write(json.dumps(data, ensure_ascii=False))

    def write_json_lines(self, data, path, encoding="utf-8"):
        with open(path, "w", encoding=encoding) as f:
            for x in data:
                f.write(json.dumps(x, ensure_ascii=False))
                f.write("\n")

    def read_excel(self, path, sheet_name=""):
        try:
            if sheet_name:
                df = pd.read_excel(path, engine="openpyxl", sheet_name=sheet_name)
            else:
                df = pd.read_excel(path, engine="openpyxl")
            return df
        except Exception as e:
            print(e)
        return pd.DataFrame()


    def json2excel(self, json_path=None, excel_path=None, json_data=None, dict_to_str=True):
        if json_path:
            json_data = self.read_json_lines(json_path)
        if not json_data:
            raise Exception("json data not exist")

        if dict_to_str:
            for obj in json_data:
                for k in obj.keys():
                    if isinstance(obj[k], dict):
                        obj[k] = json.dumps(obj[k], ensure_ascii=False, indent=4)  # json格式更加优化

        df = pd.DataFrame(json_data)
        if excel_path:
            df.to_excel(excel_path, index=False)
        return df

    def json2excel_sorted(self, json_path=None, excel_path=None, json_data=None, dict_to_str=True, sorted_by=None, reverse=False):
        if json_path:
            json_data = self.read_json_lines(json_path)
        if not json_data:
            raise Exception("json data not exist")

        if sorted_by and not isinstance(sorted_by, list):
            sorted_by = [sorted_by]

        data = sorted(json_data, key=lambda obj: [obj.get(x, str(x)) for x in sorted_by], reverse=reverse)
        self.json2excel(json_data=data, excel_path=excel_path)

    def excel2json(self, df=None, excel_path=None, json_path=None, sheet_name=None, fillna=None):
        if excel_path:
            df = self.read_excel(excel_path, sheet_name=sheet_name)
            if fillna is not None:
                df = df.fillna(fillna)
            # print(df)
        if df is None:
            raise Exception("df not exist")
        data = list()
        columns = df.columns
        for x in df.values:
            data.append(dict(zip(columns, x)))
        if json_path:
            self.write_json_lines(data, json_path)
        return data








