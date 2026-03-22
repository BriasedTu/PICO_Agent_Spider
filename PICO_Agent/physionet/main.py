from DrissionPage import Chromium
import pandas as pd

# 初始化浏览器
browser = Chromium()
tab = browser.latest_tab
tab.get('https://physionet.org/about/database/')

# 提取所有 <li> 元素
eles = tab.eles('tag:li')

# 存储数据的列表
data = []

for element in eles:
    # 提取 <a> 标签内的 Name 和 Url
    a_tag = element.ele('tag:a')
    if a_tag:  # 确保 <a> 标签存在
        name = a_tag.text
        url = a_tag.attr('href')
        # 提取整个 <li> 的文本作为 Introduction
        introduction = element.text
        # 添加到 data 列表
        data.append({
            "Name": name,
            "Url": url,
            "Introduction": introduction
        })

# 转换为 DataFrame 并保存为 CSV
df = pd.DataFrame(data)
df.to_excel("physionet_databases.xlsx", index=False)

# 打印确认
print("数据已成功保存到 'physionet_databases.xlsx'")


