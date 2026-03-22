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
        new_tab=self.browser.new_tab(self.url)
        time.sleep(1)
        new_tab.ele('x=//*[@id="current"]/div/div[1]/div[3]/div[1]/span[2]/span/div/a[4]').click(by_js=True)


        
        for Xnum in range (1,85):     
            try:
                xpath = '//*[@id="table"]/tbody/tr['+str(Xnum)+']/td[2]/a'
                paper_info = new_tab.ele(f"x={xpath}")
                paper_url = paper_info.attr("href")
                print(paper_url)
                
                paper_tab = self.browser.new_tab(paper_url) #打开新标签页，用于定位pdf文件
                title = paper_tab.ele("@class=page-title").text #pdf的title
                pdf_element = paper_tab.ele("@id=guidelinesLinks")

                
                button = pdf_element.ele("tag:a@|text():Full guideline@|text():(PDF)",timeout=1)
                if button:
                    new_link= button.attr("href")
                    
                    self.pdf_urls[title]= new_link
                    print(f'找到元素{Xnum}的pdf')
                else:
                    print(f'未找到元素{Xnum}')
                paper_tab.close()

            except:
                    print("出现错误")
        new_tab.close()
        crawler.getpdf()
        

    def getpdf(self):
        try:
            pdf_tab = self.browser.latest_tab
            for a_title in self.pdf_urls:

                url=self.pdf_urls[a_title]


                pdf_tab.download.add(url, rename=a_title, save_path=r"E:\Python Project\Spider\New_PICO_Agent\SIGN\SIGN")
                print("下载任务"+ a_title + "已添加")

        except:
            print("未找到元素")





if __name__ == '__main__':
    crawler = WebsiteCrawler(start_url='https://www.sign.ac.uk/guidelines/', num=1)
    crawler.crawl() 
    crawler.browser.quit()

