from DrissionPage import Chromium
from DrissionPage import SessionPage
from DrissionPage.common import Keys
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import time
from typing import List, Dict

class TreeWebsiteCrawler:
    def __init__(self, start_url: str):

        self.browser = Chromium()
        self.start_url = start_url
        self.lock=Lock()
        self.url_firsts=[]
        
    def crawl(self, url):
        """主爬取流程"""

        new_tab=self.browser.new_tab(url) 

        # 首次访问初始页面
        while True:

            # 1. 收集当前页面的所有二级链接
            url_secs = []
            sec_class_eles = new_tab.eles('@class=ms-link ms-exposure')
            for sec_class_ele in sec_class_eles:
                href = sec_class_ele.attr("href")
                if href:
                    url_secs.append(href)
            print(f"当前页面的所有二级链接: {url_secs}")
            
            # 2. 处理当前页的每个二级链接
            for i, url_sec in enumerate(url_secs):
                try:
                    # 记录当前标签页ID
                    original_tab_id = new_tab.tab_id
                    
                    # 导航到二级页面
                    new_tab.get(url_sec)
                    
                    title_ele = new_tab.ele('@class=fujian_box_name', timeout=5)
                    title = title_ele.text if title_ele else f"unknown_{i}"
                    
                    button_ele = new_tab.ele('@id=fileDownload', timeout=5)
                    button_ele.click()

                    pdf_id=self.browser.wait.new_tab()
                    pdf_tab=self.browser.get_tab(pdf_id)
                    pdf_url = pdf_tab.url

                    if pdf_url.endswith('.pdf'):
                        pdf_tab.download.add(pdf_url, rename=title)
                        print("下载任务"+ title + "已添加")
                    else:
                        print(f"警告：获取的URL不是PDF: {pdf_url}")
                    new_tab = self.browser.get_tab(original_tab_id)
                    self.browser.close_tabs(tabs_or_ids=pdf_id)
                    
                    new_tab.back()# 返回列表页
                    # 等待列表页重新加载
                    new_tab.ele('@class=ms-link ms-exposure', timeout=10)
                    
                except Exception as e:
                    print(f"处理链接 {url_sec} 时出错: {str(e)}")
                    # 出错时直接回到初始列表页
                    new_tab.get(url)
                    new_tab.ele('@class=ms-link ms-exposure', timeout=10)
            
            # 3. 翻页操作（保持当前标签页状态）
            if not self.go_to_next_page(new_tab):
                break

            # 4. 等待新页面加载完成（必要步骤）
            new_tab.ele('@class=ms-link ms-exposure', timeout=10)
        
        # 循环结束后关闭标签页
            new_tab.close()

        
    def go_to_next_page(self,tab) -> bool:
        """
        尝试翻到下一页
        :return: 是否成功翻页
        """
        try:
            # 查找下一页按钮 (根据实际网站调整选择器)
            next_btn = tab.ele('@text:下一页',timeout=3)           
            if next_btn and not next_btn.stale:
                # 有些网站下一页按钮可能是禁用的
                if "disabled" in next_btn.attr("class", ""):
                    return False   
                next_btn.click()
                return True
                    
        except Exception as e:
            return False  
            
        return False
    def multiple_start(self):#启动
        try:
            # 访问初始页面
            tab = self.browser.latest_tab 
            tab.get(self.start_url)

            first_class_eles=tab.eles("@class=ot-shortcode-social-icon social-twitter soc-bef hover-color-twitter")
            #print(first_class_eles)
            for first_class_ele in first_class_eles:
                self.url_firsts.append(first_class_ele.attr("href"))

            print(self.url_firsts[0])
            self.crawl(self.url_firsts[0])
                
                # 等待所有任务完成



        except:
            print("访问初始页面失败")
            return



            
            

if __name__ == '__main__':
    crawler = TreeWebsiteCrawler(start_url='https://www.medsci.cn/guideline/index.do')
    crawler.multiple_start() 
