from DrissionPage import Chromium
import re 
import time


class WebsiteCrawler:
    def __init__(self, start_url: str, num: int):
        self.browser = Chromium()
        self.url = start_url
        self.num = num
        self.pdf_urls = {}
        self.download_path = ""


    def crawl(self):
        
        time.sleep(1)
        n=0
        new_tab=self.browser.new_tab(self.url)
        
        input("请手动点击搜索按钮")
        
        while True:    
               
            print(f'第{n+1}页')

            if n>2:
                input("请手动点击年份") # 找到提示文本，退出循环
            try:
                paper_infos = new_tab.eles("@class=shelf-content")
            except:
                input("检查网页并更换代理")
                n-=1
                continue


            for paper in paper_infos:
                try:
                    if paper.ele("@class=jquery-once-2-processed",timeout=1):
                        print('找到元素')
                        title = paper.ele("@class=guideline-title").text
                        title = re.sub(r'[\\/:*?"<>|]', '_', title)
                        if len(title)>100:
                            title=title[:100]

                        
                        button = paper.ele("@class=jquery-once-2-processed",timeout=1)
                        raw_link= button.attr("href")
                        
                        pdf_tab = self.browser.new_tab(raw_link)
                        b2=pdf_tab.ele("text:Full Report (PDF)")
                        b2.click.to_download(save_path="D:\pyproject\Spider\PubMed\WHO",by_js=True, rename=title)
                        pdf_tab.close()
                        time.sleep(1)  
                except:
                    print("未找到元素")
            
            new_tab.ele("@class=pager-next").click()
            n+=1
            time.sleep(1)


if __name__ == '__main__':
    crawler = WebsiteCrawler(start_url='', num=1)
    crawler.crawl() 