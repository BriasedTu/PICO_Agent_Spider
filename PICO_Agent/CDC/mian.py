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
            pdf_urls = {} 
            x=re.sub(
                r'(dpage=)\d+', 
                r'\g<1>' + str(n),  # 用\g<1>避免歧义，拼接n的值
                self.url
            )
            
            new_tab=self.browser.new_tab(x)
            print(f'第{n+1}页')
            if self.num==1:#到达结尾页，没有结果了
                if n>=13:
                    print('没有结果了')
                    break  
            else:
                if n>=9:
                    print('没有结果了')
                    break  
            try:

                paper_infos = new_tab.eles("@class=result")
            except:
                input("检查网页并更换代理")
                n-=1
                continue


            for paper in paper_infos:#二级标签查找
                try:
                    if paper.ele("@class=result",timeout=1):
                        print('找到元素')
                        title = paper.ele("@class=result-title").text
                        title = re.sub(r'[\\/:*?"<>|]', '_', title)
                        if len(title)>100:
                            title=title[:100]
                        button = paper.ele("@class=result-title")
                        raw_link= button.attr("href")
                        new_link = re.sub(r'\breader\b', 'epdf', raw_link)
                        pdf_urls[title] = new_link
                    
                except:
                    print("未找到元素")
            crawler.getpdf(pdf_urls=pdf_urls)
            new_tab.close()
            n+=1
            input("记得换代理")


    def getpdf(self,pdf_urls):
        
            
        for a_title in pdf_urls:
            
            

            url=pdf_urls[a_title]
            pdf_tab=self.browser.new_tab(url)
            time.sleep(2)
            try:
                d_pdf=pdf_tab.ele('xpath=//*[@id="app-navbar"]/div[3]/div[3]/div/div[1]/div/ul[1]/li[1]/a')
                d_pdf.click.to_download(save_path="D:\pyproject\Spider\AmercianHeartAssociation\AmercianHeartAssociation",rename=a_title, by_js=True)
                time.sleep(2)
                print(f'正在下载{a_title}')
                pdf_tab.close()
            except:
                try:
                    c_pdf=pdf_tab.ele('xpath=//*[@id="app-navbar"]/div[3]/div[3]/a')
                    c_pdf.click.to_download(save_path="D:\pyproject\Spider\AmercianHeartAssociation\AmercianHeartAssociation",rename=a_title, by_js=True)
                    time.sleep(2)
                    print(f'正在下载{a_title}')
                    pdf_tab.close()
                except:
                    print(f"未找到元素{a_title}")
                    pdf_tab.close()
                    continue
                    






if __name__ == '__main__':
    crawler = WebsiteCrawler(start_url='https://search.cdc.gov/search/?query=guideline&any=guideline%20guidance%20guidelines&date1=Jan%201%2C%202024&date2=Jun%2023%2C%202025&dpage=1', num=1)
    crawler.crawl() 
    #crawler2=WebsiteCrawler(start_url='https://www.ahajournals.org/action/doSearch?field1=Title&text1=guidance&field2=AllField&text2=&publication=&Ppub=&access=on&startPage=0&pageSize=100', num=2)
    #crawler.crawl() 
    

    #crawler2 = WebsiteCrawler(start_url='https://diabetesjournals.org/journals/search-results?q=guidance&sort=Date+-+Newest+First&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&qb=%7b%22q%22%3a%22guidance%22%7d&page=1', num=2)
    #crawler2.crawl() 
    #crawler2.browser.quit()