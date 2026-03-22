from DrissionPage import ChromiumPage

def modify_request(request):
    if '/portal-guider/download' in request.url:
        # 修改请求体
        new_body = request.post_data
        new_body['downloadType'] = 0  # 关键修改
        request.continue_(post_data=new_body)
    else:
        request.continue_()

page = ChromiumPage()
page.listen.start("/portal-guider/downLoad")
page.listen.request(modify_request)

# 访问页面并触发下载
page.get('https://www.medsci.cn/guideline/show_article.do?id=F54751c00a3519c2')
page.ele('button:has-text("下载")').click()  # 根据实际按钮调整