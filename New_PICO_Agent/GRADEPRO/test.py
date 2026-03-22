import re
import time
import json
import os
from DrissionPage import Chromium
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
from htmlprocess import GDTHtmlParser

class WebsiteCrawler:
    def __init__(self, start_url: str, output_dir: str = "guidelines_data"):
        print(f"[*] 正在初始化浏览器引擎...")
        self.browser = Chromium()
        self.url = start_url
        self.output_dir = output_dir
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"[+] 存储目录已就绪: {self.output_dir}")


    
    def listen(self,tab):
        tab.listen.start(targets="-",res_type="xhr")
        tab.get(self.url)
        res = tab.listen.wait()
        return res.response.body
    
    def extract_all_text_values(self, data, need_to_split, needkey='text', results=None):
        """
        递归遍历任意深度的字典/列表，寻找所有 key 为 'text' 的值
        """
        # 标记是否是第一次调用（顶层调用）
        is_top_level = False
        if results is None:
            results = []  # 【重要】必须用列表来收集，不能用字符串
            is_top_level = True

        # 情况 A: 如果当前节点是字典
        if isinstance(data, dict):
            for key, value in data.items():
                # 1. 找到了目标！保存值
                if key == needkey and value: # 确保 value 不是 None 或空
                    results.append(str(value)) # 添加到列表
                
                # 2. 继续向下钻取
                self.extract_all_text_values(value, need_to_split, results)
                
        # 情况 B: 如果当前节点是列表
        elif isinstance(data, list):
            for item in data:
                # 对列表里的每个元素递归调用
                self.extract_all_text_values(item, need_to_split, results)
        
        if is_top_level:
            separator = "\n" if need_to_split else " "
            return separator.join(results)
            
        return results
    
    def process_everything_to_json(self,data_dict):
        '''

        '''
        possiblekeys = ["oneRowSource","ietdPrintout","sofSource"]
        for key in possiblekeys:
            html_str = data_dict.get('profile', {}).get('extra', {}).get(key)
            
            if html_str:
                print("[*] 正在进行全自动结构化解析...")
                json_structure = self.html_to_structured_json(html_str) 
                # 3. 存回字典 
                data_dict['profile']['extra'][key] = json_structure
                # 打印结果预览
                print(f"    [+] 解析完成，共提取 {len(json_structure)} 个区块")
        return data_dict
    
    def process_SofSource(self,data_dict):
        '''
        用于提取pico的函数
        '''
        if not data_dict:
            return {}
        rawhtml = data_dict.get('profile', {}).get('extra', {}).get("oneRowSource")
        ntp = rawhtml.split('<table', 1)[0]

        soup = BeautifulSoup(ntp, 'html.parser')
        # 1. 定位包含信息的容器
        container = soup.find('div', class_='question-data')
        # 兜底：如果找不到这个类，尝试在 body 里直接找
        if not container:
            container = soup.body if soup.body else soup

        metadata = {}
        for div in container.find_all('div', recursive=False):
            key_node = div.find('b')
            if not key_node:
                continue
            raw_key = key_node.get_text(strip=True).replace(':', '')
            clean_key = raw_key.lower().replace('(s)', '').strip()
            value_node = div.find('label')  
            if value_node:
                value = value_node.get_text(strip=True)
            else:
                text_node = key_node.next_sibling
                value = str(text_node).strip() if text_node else ""
            if value: # 只有值不为空时才存
                metadata[clean_key] = value
        return metadata
    
    def process_Ietd(self,data_dict):
        '''
        提取background和coi
        '''
        rawdict_bg = data_dict.get('profile', {}).get('extra', {}).get("ietd",{}).get("templateData",{}).get("question",{}).get("sections",{}).get("background")
        rawdict_coi = data_dict.get('profile', {}).get('extra', {}).get("ietd",{}).get("templateData",{}).get("question",{}).get("sections",{}).get("coi")
        processed_bg = self.extract_all_text_values(data=rawdict_bg,need_to_split=True)
        processed_coi = self.extract_all_text_values(data=rawdict_coi,need_to_split=False)
        return processed_bg, processed_coi





    def clean(self,data_dict,p_title):#弃用该函数，改用newclean
        '''
        主处理函数,输出为完全处理后的dict
        '''
        cleaned_dict={}
        simpletag=["author","title"]

        # 获取question
        cleaned_dict["question"] = data_dict.get('profile', {}).get("title")
        if not cleaned_dict["question"]:
            qs = data_dict.get('profile', {}).get("sofTitle")
            if qs:
                cleaned_dict["question"] = "Should" + qs
            else:
                cleaned_dict["question"] = p_title
        
        picodata = self.process_SofSource(data_dict)
        background, coi = self.process_Ietd(data_dict)

        #获取pico
        cleaned_dict["pico"] = {}
        for key, value in picodata.items():
            cleaned_dict["pico"][key] = value
            if not cleaned_dict["pico"]["Intervention"]:
                cleaned_dict["pico"]["Intervention"] = data_dict.get('profile', {}).get('extra',{}).get("intervention")

        #获取background和coi
        cleaned_dict["Background"] = background
        cleaned_dict["Conflict_of_interest"] = coi


        

    def newclean(self,data_dict,p_title):
        '''
        主处理函数,输出为完全处理后的dict
        '''
        cleaned_dict={}
        parser = GDTHtmlParser()

        # 获取question
        cleaned_dict["question"] = data_dict.get('profile', {}).get("title")
        if not cleaned_dict["question"]:
            qs = data_dict.get('profile', {}).get("sofTitle")
            if qs:
                cleaned_dict["question"] = "Should" + qs
            else:
                cleaned_dict["question"] = p_title
        

        oneRowSource = data_dict.get('profile', {}).get('extra',{}).get("oneRowSource")
        ietdPrintout = data_dict.get('profile', {}).get('extra',{}).get("ietdPrintout")
        sofSource = data_dict.get('profile', {}).get('extra',{}).get("sofSource")
        
        cleanoneRowSource = parser.parse(oneRowSource)
        cleanietdPrintout = parser.parse(ietdPrintout)
        cleansofSource = parser.parse(sofSource)

        

    def crawl(self):
        tab = self.browser.latest_tab
        tab.listen.start(targets="1C8718CC-26FB-825B-9CB2-3972C2DD1780",res_type='xhr')
        tab.get(self.url)
        res = tab.listen.wait(timeout=20)
        if res:
            rawdict = res.response.body
        self.newclean(rawdict,"A579747-2186-359C-8751-F6245604F25D")
        


        with open("test7.json", "w", encoding="utf-8") as f:
            json.dump(rawdict, f, ensure_ascii=False, indent=4)
            
    




if __name__ == '__main__':
    # 爬取目标
    TARGET_URL = 'https://guidelines.gradepro.org/profile/1C8718CC-26FB-825B-9CB2-3972C2DD1780'
    
    crawler = WebsiteCrawler(start_url=TARGET_URL)
    try:
        crawler.crawl()
    except KeyboardInterrupt:
        print("\n[!] 用户中断操作")
    finally:
        print("\n[*] 正在安全退出...")
        crawler.browser.quit()




 在爬取过程中，我发现之前的爬取类虽然在"ietdPrintout"的爬取表现很好，但对于另外两个模块的表现比较一般。我觉得可以针对"oneRowSource"和"sofSource"分别再写一个专门的解析逻辑并打包成不同的类。现在先写"oneRowSource"的爬取逻辑，我先给你一部分被当前方法解析过的内容以及原始的html，