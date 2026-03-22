from DrissionPage import Chromium
import time


class WebsiteCrawler:
    def __init__(self, start_url: str, num: int):
        self.browser = Chromium()
        self.url = start_url
        self.num = num


    def crawl(self):
        new_tab=self.browser.new_tab(self.url)
        time.sleep(1)
        n=1

        
        while True:
            if self.num == 1:
                if n!=1:
                    new_tab=self.browser.new_tab("https://diabetesjournals.org/journals/search-results?q=guideline&sort=Date+-+Newest+First&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&page=" + str(n))
                if new_tab.ele('text=No results found', timeout=1):
                    print('没有结果了')
                    break  # 找到提示文本，退出循环
            else:
                if n!=1:
                    new_tab=self.browser.new_tab("https://diabetesjournals.org/journals/search-results?q=guidance&sort=Date+-+Newest+First&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&qb=%7b%22q%22%3a%22guidance%22%7d&page=" + str(n))
                if new_tab.ele('text=No results found', timeout=1):
                    print('没有结果了')
                    break  # 找到提示文本，退出循环


            paper_infos = new_tab.eles("@class=item-info")
            

            for paper in paper_infos:
                try:
                    if paper.ele("@class=icon-availability_free", timeout=1):
                    
                        title = paper.ele("@class=sri-title customLink al-title").text
                        button = paper.ele("@class=sri-pdflink item item-with-dropdown")
                        pdf_id = button.click.for_new_tab()  # 点击并获取新tab对象
                        pdf_id.set.activate()
                        pdf_tab=self.browser.get_tab(pdf_id)
                        pdf_url = pdf_tab.url

                        if pdf_url.__contains__('.pdf'):
                            pdf_tab.download.add(pdf_url, rename=title, save_path="")
                            print("下载任务"+ title + "已添加")
                        else:
                            print(f"警告：获取的URL不是PDF: {pdf_url}")
                        
                        pdf_tab.close()
                                                
                except:
                    print("未找到元素")
            new_tab.close()
            n+=1

if __name__ == '__main__':
    #crawler = WebsiteCrawler(start_url='https://diabetesjournals.org/journals/search-results?q=guideline&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&page=1&sort=Date+-+Newest+First', num=1)
    #crawler.crawl() 
    #crawler.browser.quit()
    crawler2 = WebsiteCrawler(start_url='https://diabetesjournals.org/journals/search-results?q=guidance&sort=Date+-+Newest+First&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&qb=%7b%22q%22%3a%22guidance%22%7d&page=1', num=2)
    crawler2.crawl() 
    crawler2.browser.quit()
