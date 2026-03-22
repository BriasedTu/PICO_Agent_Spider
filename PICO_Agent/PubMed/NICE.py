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
        n=1
        
        new_tab=self.browser.new_tab(self.url)
        input("请手动搜索")
        
        while True:    
            pdf_urls = {}    
            print(f'第{n}页')
            if n>=88:
                print('没有结果了')
                break  # 找到提示文本，退出循环
            try:
                paper_info = new_tab.ele('xpath=//*[@id="results"]/tbody')
                paper_infos = paper_info.eles('tag=a')

            except:
                input("检查网页并更换代理")
                n-=1
                continue


            for paper in paper_infos:
                try:
                    
                    print('找到元素')
                    title = paper.text
                    title = re.sub(r'[\\/:*?"<>|]', '_', title)
                    if len(title)>100:
                        title=title[:100]
                    raw_link= paper.attr("href")
                    self.getpdf(raw_link=raw_link,title=title)
                    time.sleep(1)
                    
                except:
                    print("未找到元素")
            
            new_tab.ele("@class=glyphicon glyphicon-arrow-right").click()
            n+=1
            time.sleep(1)

    def getpdf(self,raw_link,title):
        try:
            
            pdf_tab = self.browser.new_tab(raw_link)
            paper_url=pdf_tab.ele('xpath:/html/body/main/div[2]/div/div/div/div/div/div[1]/a').attr("href")
            pdf_paper=self.browser.new_tab(paper_url)
            link=pdf_paper.url
            pdf_paper.download.add(link, rename=title, save_path=self.download_path)
            pdf_paper.close()
            pdf_tab.close()
        except:
            print("未找到pdf")
        
            


if __name__ == '__main__':
    crawler = WebsiteCrawler(start_url='', num=1)
    crawler.crawl() 