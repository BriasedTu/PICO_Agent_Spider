from DrissionPage import Chromium
import os
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
        link_eles = new_tab.eles("@class=list-pages__link")


        
        for link_ele in link_eles:     
            try:
                
                paper_url = link_ele.attr("href")
                #print(paper_url)
                
                paper_tab = self.browser.new_tab(paper_url) #打开新标签页，用于定位pdf文件
                
                title = paper_tab.ele("#PageTitle").text #pdf的title
                content = paper_tab.ele("@class=col-12 col-lg-9 body-container").text
                self.generate_markdown_file(title, content) #基础md文件

                button = paper_tab.ele("tag:span@|text():Download PDF",timeout=1)

                if button:
                    self.getpdf(button,title)  
                else:
                    print(f'未找到{title}的pdf文件')
                paper_tab.close()

            except:
                    print("网页遍历出现错误")
        new_tab.close()
        
        

    def getpdf(self,button,title):
        '''尝试下载pdf'''
        try:
            
            button.click(by_js=True)
            pdf_tab = self.browser.latest_tab
            pdf_tab.listen.start(targets=".pdf")
            pdf_tab.run_js("location.reload();")
            try:
                pdf_response = pdf_tab.listen.wait(count=1,timeout=5)  # 增加超时时间
                if pdf_response:
                    pdf_url = pdf_response.url  # 获取 PDF 的 URL
                    # 下载 PDF
                    pdf_tab.download.add(pdf_url, rename=title, save_path=r"E:\Python Project\Spider\New_PICO_Agent\IDSA\IDSA")
                    print(f"下载任务 {title} 已添加")
                else:
                    print(f"无法捕获 {title} 的 PDF 请求")
            except Exception as e:
                print(f"等待 PDF 请求超时或出错: {e}")
            pdf_tab.close()

        except:
            print("pdf获取出现错误")
    
    def generate_markdown_file(self, title, content):
        """生成Markdown文件"""
        
        target_dir = r""
        os.makedirs(target_dir, exist_ok=True)
        safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
        safe_title = safe_title[:100] if len(safe_title) > 100 else safe_title
        
        filename = f"{safe_title}.md"
        filepath = os.path.join(target_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"已成功创建Markdown文件: {filename}")
        except Exception as e:
            print(f"创建Markdown文件失败: {e}")





if __name__ == '__main__':
    crawler = WebsiteCrawler(start_url='https://www.idsociety.org/practice-guideline/all-practice-guidelines/', num=1)
    crawler.crawl() 
    crawler.browser.quit()

