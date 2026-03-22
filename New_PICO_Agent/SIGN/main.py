from DrissionPage import Chromium
import re 
import time


class WebsiteCrawler:
    def __init__(self, start_url: str, num: int):
        self.browser = Chromium()
        self.url = start_url
        self.num = num
        self.pdf_urls = {}


    def crawl(self):
        
        time.sleep(1)
        n=0

        
        while True:     
            new_tab=self.browser.new_tab(re.sub(r'(startPage=)\d+',r'\1n',self.url))
            print(f'第{n+1}页')
            if n>=9:
                print('没有结果了')
                break  # 找到提示文本，退出循环



            paper_infos = new_tab.eles("@class=card border-bottom mb-24 pb-24  d-flex flex-row")

            for paper in paper_infos:
                try:
                    if paper.ele("@class=d-inline-flex align-items-end btn btn-pdf p-0",timeout=1):
                        print('找到元素')
                        title = paper.ele("@class=text-reset animation-underline").text
                        button = paper.ele("@class=d-inline-flex align-items-end btn btn-pdf p-0")
                        raw_link= button.attr("href")
                        new_link = re.sub(r'\breader\b', 'epdf', raw_link)
                        self.pdf_urls[title]= new_link
                    
                except:
                    print("未找到元素")
            new_tab.close()
            n+=1
        crawler.getpdf()

    def getpdf(self):
        try:
            pdf_tab = self.browser.latest_tab
            for a_title in self.pdf_urls:

                url=self.pdf_urls[a_title]
                pdf_tab.listen.start(targets="www.ahajournals.org/doi/pdfdirect/")
                pdf_tab.get(url)
                pdf_real=pdf_tab.wait(count=1)
                pdf_real_url=pdf_real.requset.url
                
                pdf_tab.listen.stop()

                pdf_tab.download.add(pdf_real_url, rename=a_title, save_path="D:\pyproject\Spider\AmercianHeartAssociation\AmercianHeartAssociation")
                print("下载任务"+ a_title + "已添加")

        except:
            print("未找到元素")





if __name__ == '__main__':
    crawler = WebsiteCrawler(start_url='https://www.ahajournals.org/action/doSearch?field1=Title&text1=guidance&field2=AllField&text2=&publication=&Ppub=&access=on&startPage=0&pageSize=100', num=1)
    crawler.crawl() 
    crawler.browser.quit()
    #crawler2 = WebsiteCrawler(start_url='https://diabetesjournals.org/journals/search-results?q=guidance&sort=Date+-+Newest+First&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&qb=%7b%22q%22%3a%22guidance%22%7d&page=1', num=2)
    #crawler2.crawl() 
    #crawler2.browser.quit()
