from DrissionPage import SessionPage
import time
import os
from urllib.parse import urljoin, quote
from pathvalidate import sanitize_filename
import re

class WebsiteCrawler:
    def __init__(self, start_url: str):
        self.page = SessionPage()
        self.base_url = 'https://diabetesjournals.org'
        self.start_url = start_url
        self.download_path = r"D:\pyproject\Spider\AmericanDiabetesAssociation"
        os.makedirs(self.download_path, exist_ok=True)
        # 设置请求头模拟浏览器
        self.page.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })

    def crawl(self):
        n = 1
        while True:
            # 构造分页URL
            page_url = f"{self.start_url}&page={n}" if n > 1 else self.start_url
            print(f"正在处理第 {n} 页: {page_url}")
            
            # 发送请求获取页面内容
            self.page.get(page_url)
            time.sleep(1)  # 适当延迟避免请求过快
            
            # 检查是否到达末页
            if self.page.ele('text=No results found. Please modify your search and try again.', timeout=1):
                print("已到达最后一页，爬取结束。")
                break
            
            # 获取所有论文条目
            items = self.page.eles('.results-list-item')
            if not items:
                print("未找到论文条目，爬取终止。")
                break
            
            # 处理每个论文条目
            for item in items:
                self.process_item(item)
            
            n += 1

    def process_item(self, item):
        """处理单个论文条目"""
        # 检查是否为免费文章
        free_icon = item('.icon-availability_free', timeout=0)
        if not free_icon:
            return
        
        try:
            # 获取标题并清理非法字符
            title_elem = item('.sri-title')
            title = sanitize_filename(title_elem.text) if title_elem else "Untitled"
            print(f"处理文章: {title}")
            
            # 获取DOI - 这是关键
            doi_elem = item('xpath:.//span[contains(text(), "DOI:")]/following-sibling::span')
            if not doi_elem:
                print("未找到DOI信息，跳过")
                return
                
            doi = doi_elem.text.strip()
            print(f"获取到DOI: {doi}")
            
            # 构建PDF下载URL
            pdf_url = self.get_pdf_url(doi)
            if not pdf_url:
                return
            
            # 下载PDF文件
            self.download_pdf(pdf_url, title)
            
        except Exception as e:
            print(f"处理论文条目时出错: {str(e)}")

    def get_pdf_url(self, doi):
        """构建PDF下载URL并处理重定向"""
        # 构建下载请求URL
        download_url = f"{self.base_url}/action/downloadPDF?doi={quote(doi)}"
        print(f"构建下载URL: {download_url}")
        
        # 创建临时页面处理重定向
        temp_page = SessionPage()
        temp_page.headers.update(self.page.headers)  # 使用相同headers
        temp_page.get(download_url)
        
        # 检查是否重定向到PDF
        if '.pdf' in temp_page.url.lower():
            print(f"获取到真实PDF URL: {temp_page.url}")
            return temp_page.url
        
        # 处理可能的中间页面
        direct_pdf_link = temp_page('a:has-text("PDF")', timeout=1)
        if direct_pdf_link:
            pdf_url = direct_pdf_link.attr('href')
            if pdf_url:
                absolute_url = urljoin(self.base_url, pdf_url)
                print(f"从中间页获取PDF URL: {absolute_url}")
                return absolute_url
        
        print(f"无法获取PDF URL，最终页面: {temp_page.url}")
        return None

    def download_pdf(self, pdf_url, title):
        """下载PDF文件"""
        # 确保URL是有效的PDF
        if not pdf_url.lower().endswith('.pdf'):
            # 尝试从URL参数中提取PDF链接
            match = re.search(r'file=(.*?\.pdf)', pdf_url, re.IGNORECASE)
            if match:
                pdf_url = match.group(1)
                print(f"从参数中提取PDF URL: {pdf_url}")
            else:
                print(f"非PDF链接跳过: {pdf_url}")
                return
        
        # 设置保存路径
        filename = f"{title}.pdf"
        save_path = os.path.join(self.download_path, filename)
        
        # 执行下载
        try:
            self.page.download(pdf_url, save_path=save_path, overwrite=True)
            print(f"✓ 成功下载: {title}")
        except Exception as e:
            print(f"下载失败: {title} | 错误: {str(e)}")
            # 尝试使用临时页面下载
            try:
                temp_page = SessionPage()
                temp_page.download(pdf_url, save_path=save_path, overwrite=True)
                print(f"✓ 使用临时会话成功下载: {title}")
            except Exception as e2:
                print(f"二次下载失败: {title} | 错误: {str(e2)}")

if __name__ == '__main__':
    start_url = 'https://diabetesjournals.org/journals/search-results?q=guideline&allJournals=1&f_ContentType=Journal+Articles&fl_SiteID=3&page=1&sort=Date+-+Newest+First'
    crawler = WebsiteCrawler(start_url)
    crawler.crawl()