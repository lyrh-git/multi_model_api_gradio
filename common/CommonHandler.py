import json
import os
import re
import unittest
# import OpenCC
import zhconv


# from half_json.core import JSONFixer

import json_repair
from json_repair import repair_json

# json_fixer = JSONFixer()

# t2s = OpenCC("t2s")
# s2t = OpenCC("s2t")


class JSONHandler:
    def inner_value_to_dict(self, dt, pop_nan=False):
        # print(f"inner handle: {dt}")
        if isinstance(dt, dict):
            for k in list(dt.keys()):
                t = self.inner_value_to_dict(dt.get(k), pop_nan=pop_nan)
                # print("value:", t)
                if not t and pop_nan and (isinstance(t, list) or isinstance(t, tuple) or isinstance(t, dict) or isinstance(t, str) or t is None):
                    # print("pop")
                    dt.pop(k)
                else:
                    dt[k] = t
            return dt
        elif isinstance(dt, list):
            out_dt = list()
            for x in dt:
                # print(x)
                t = self.inner_value_to_dict(x, pop_nan=pop_nan)
                # print(t)
                if not t and pop_nan and (isinstance(t, list) or isinstance(t, tuple) or isinstance(t, dict) or isinstance(t, str) or t is None):
                    # print("pop")
                    pass
                else:
                    out_dt.append(t)
            return out_dt
        elif isinstance(dt, str) and re.match("^\{.*\}$", dt.strip(), flags=re.S):
            dt = dt.strip()
            try:
                transfer_dt = json.loads(dt)
                # print(f"transfer str to tojson dict: \n{dt}\n{transfer_dt}")
                return transfer_dt
            except Exception as e1:
                try:
                    # dt_fix = json_fixer.fix(dt)
                    dt_fix = self.check_json(dt)
                    if dt_fix.success:
                        transfer_dt = json.loads(dt_fix.line)
                        return transfer_dt
                    else:
                        jsonrepair = pythonmonkey.require('jsonrepair').jsonrepair
                        transfer_dt = json.loads(jsonrepair(dt).replace(" ", ""))
                        return transfer_dt
                except Exception as e2:
                    return dt
        else:
            return dt

    def check_json(self, text):
        if isinstance(text, dict):
            text = str(text)
        text_repair = repair_json(text, ensure_ascii=False)
        print(text_repair)
        return json.loads(text_repair)

class StringHandler:
    def similar(self, sent1, sent2, min_len=1, join_sep="", replace_symbol=True):
        words1, words2 = list(), list()
        if isinstance(sent1, str):
            words1 = list(sent1)
        if isinstance(sent2, str):
            words2 = list(sent2)
        # print(words1, words2)

        if replace_symbol:
            words1 = [re.sub("[^\u4E00-\u9FA50-9a-zA-Z]", "", x) for x in words1]
            words1 = [x for x in words1 if x]
            words2 = [re.sub("[^\u4E00-\u9FA50-9a-zA-Z]", "", x) for x in words2]
            words2 = [x for x in words2 if x]

        if not sent1 or not sent2:
            return 0, list()

        common_words = list()
        i = 0
        now_words = list()
        while i < len(words1):
        # for w1 in words1:
            now_words = list()
            for w2 in words2:
                # print(words1[i], w2)
                if i < len(words1) and words1[i] == w2:
                    now_words.append(w2)
                    i += 1
                    # print(i)
                elif now_words:
                    break
            # i += 1
            if not now_words:
                i += 1
            # print(i, now_words)
            if len(now_words) >= min_len:
                common_words.append(now_words)
        common_sents = [join_sep.join(x) for x in common_words]
        # print(common_sents)
        similarity = sum([len(x) for x in common_sents]) / sum([len(x) for x in words1])
        # print(similarity)
        return similarity, common_sents

    def simplified_to_traditional(self, s):
        return zhconv.convert(s, 'zh-hant')
        # return s2t.convert(s)

    def traditional_to_simplified(self, s):
        return zhconv.convert(s, "zh-hans")
        # return t2s.convert(s)

class Test(unittest.TestCase):
    json_handler = JSONHandler()
    string_handler = StringHandler()

    def test_json_inner_value_to_dict(self):
        # dt = {"code": 0, "data": {"list": [{"BGC声量": "0", "PGC声量": "1,342", "UGC声量": "768", "begin_date": "2024-07-07", "end_date": "2024-08-05", "object_info": "{\"品牌名\":\"五粮春\",\"品牌指数\":{\"品牌指数\":63.41,\"传播度\":64.54,\"参与度\":72.05,\"美誉度\":70.24,\"转化度\":46.79},\"品牌热词\":\"满减/39度/特曲/52度/45度/浓香/口感醇厚/折扣/回味悠长/回味/玉米/旗舰店/瓶装/限量/高粱/活动/公司/酒体/口感浓郁/礼盒/白酒者/大米/口感柔和/超市/糯米/送礼/高端/五粮液/口感/礼盒装/宴请/口感细腻/电商/浓香型/包装精美/促销/盒装/日常饮/性价比/价格高/小麦/整箱/包装/生肖酒/京东/商务/纪念酒/收藏/礼品/收藏价值\"}", "总声量": "2,110", "总触达量": "34,495,741"}]}, "message": "success", "sql_list": []}
        dt = {
            "code": 0,
            "data": {
                "indicator": {
                    "code": 0,
                    "message": "",
                    "data": {
                        "list": None
                    }
                }
            },
            "message": "success"
        }
        result = self.json_handler.inner_value_to_dict(dt, pop_nan=True)
        print(json.dumps(result, indent=4, ensure_ascii=False))

    def test_similar(self):
        sents = [
            ["宝玑米身体冷霜，让你成为冬季的“香饽饽”！", "宝玑米，让你冬季成为香饽饽"],
            ["今天很开心", "今天不开心"],
            ["今天,好", "今天"],
            ["""
宝玑米身体冷霜，你真的不做香水吗？！

宝玑米身体冷霜，真的有两把刷子！一直在还原东方植物香氛，居然配出了华妃娘娘的欢宜香，连嬛嬛和安小鸟一直苦心研究的鹅梨帐中香也做出来了！

宝玑米身体冷霜是实实在在的好东西，质地润而不粘，一抹就化开了，很容易吸收，长达 8 小时的保湿，在这样的秋冬季节用自然是极好的。

雪落栀子、雾隐梅园、空庭芍药、鹅梨帐中香四款味道，都值得一试。

空庭芍药，好御姐的芍药玫瑰香！闻着仿佛看到了，宠贯六宫，满蒙八旗也不敌华妃娘娘凤仪万千。

鹅梨帐中香，清甜温婉的清梨香！优雅温婉，端庄大气，是大胖橘深爱的侍寝香。

雾隐梅园，“逆风如解意，容易莫摧残”是嬛嬛除夕夜在倚梅园祈福时的纯净美好，清冷的花香带着木质香。

雪落栀子，好一朵带着露水绿叶的栀子花！纯元皇后所用之香大致如此，唤起深埋心底的情愫，年少所爱之人自是念念不忘的。

还有同款香薰蜡烛和香包，不同的使用场景更方便小主们选择，“礼盒的图案源自于宝相花纹，寓意着圆满；瓶身设计使用了中式花窗➕江南苏绣的东方元素，中式美学果然是好看的。

华妃娘娘“做衣如做人，一定要花团锦簇，轰轰烈烈才好”那自然所有的味道都要拿下啦！还有限定周边，贴纸➕香卡➕亚克力立牌➕气囊支架➕足金黄金小像➕盲盒。

宝玑米身体冷霜，你值得拥有！""",
             """宝玑米✖甄嬛传‼华妃娘娘的欢宜香原来是这个

宝玑米你真的有两把刷子一直在还原东方植物香氛，居然配出华妃娘娘的欢宜香，连嬛嬛和安小鸟一直苦心研究的鹅梨帐中香也做出来了💯

宝玑米身体冷霜是实实在在的好东西，质地润而不粘，一抹就化开了很容易吸收，长达8小时的保湿，在这样的秋冬季节用自然是极好[萌萌哒R]
雪落栀子、雾隐梅园、空庭芍药、鹅梨帐中香四款味道，都值得小主们一试

空庭芍药
好御姐的芍药玫瑰香！闻着仿佛看到了，宠贯六宫，满蒙八旗也不敌华妃娘娘凤仪万千

鹅梨帐中香
清甜温婉的清梨香！优雅温婉，端庄大气，是大胖橘深爱的侍寝香

雾隐梅园
“逆风如解意，容易莫摧残”是嬛嬛除夕夜在倚梅园祈福时的纯净美好，清冷的花香带着木质香

雪落栀子
好一朵带着露水绿叶的栀子花！纯元皇后所用之香大致如此，唤起深埋心底的情愫，年少所爱之人自是念念不忘的

[派对R]还有同款香薰蜡烛和香包不同的使用场景更方便小主们选择，”礼盒的图案源自于宝相花纹，寓意着圆满；瓶身设计使用了中式花窗➕江南苏绣的东方元素，中式美学果然是好看的

华妃娘娘“做衣如做人，一定要花团锦簇，轰轰烈烈才好”那自然所有的味道都要拿下啦✅还有限定周边，贴纸➕香卡➕亚克力立牌➕气囊支架➕足金黄金小像➕盲盒
#宝玑米身体冷霜#宝玑米#甄嬛传#甄嬛传联名 #甄嬛传十级观众 #甄嬛传重温",
"""]
        ]
        for sent1, sent2 in sents:
            similarity, common_sents = self.string_handler.similar(sent1, sent2, min_len=2)
            print(f"\n\nsent1: {sent1}\nsent2: {sent2}\nsimilarity:{similarity}\ncommon_sents: {common_sents}")

    def test_check_json(self):
        test_dir = "/Users/admin/program/projects/multi_model_api_gradio/data/test/json_repair"
        filenames = os.listdir(test_dir)
        paths = [f"{test_dir}/{x}" for x in filenames if "repair" not in x]
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                result = self.json_handler.check_json(text)
                with open(path.replace(".json", "_repaired.json"), "w", encoding="utf-8") as w:
                    w.write(json.dumps(result, ensure_ascii=False))