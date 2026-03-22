from DrissionPage import Chromium
import re 
import time

browser = Chromium()
pdf_tab = browser.latest_tab
url='https://www.ahajournals.org/doi/epdf/10.1161/CIRCRESAHA.112.270207'
pdf_tab.get(url)
d_pdf=pdf_tab.ele('xpath=//*[@id="app-navbar"]/div[3]/div[3]/div/div[1]/div/ul[1]/li[1]/a')
d_pdf.click.to_download(save_path="D:\pyproject\Spider\AmercianHeartAssociation\AmercianHeartAssociation",rename="1",by_js=True)
input("请输入任意字符退出")

