import base64
import json
import urllib.request
import urllib.error
import idna  # 处理国际化域名

# 替换为你的订阅链接
subscription_url = "https://xn--2dk290r.xn--p8jhn1a2d1epgoe.com/s/1727f25ea6ac229a9fe8a6b900dcff16"

try:
    # 设置请求头模拟浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # 手动处理国际化域名 (IDN)
    parsed_url = urllib.parse.urlparse(subscription_url)
    encoded_netloc = idna.encode(parsed_url.netloc).decode('ascii')  # 转换为ASCII兼容格式
    fixed_url = urllib.parse.urlunparse((
        parsed_url.scheme,
        encoded_netloc,
        parsed_url.path,
        parsed_url.params,
        parsed_url.query,
        parsed_url.fragment
    ))
    
    # 创建请求对象
    req = urllib.request.Request(fixed_url, headers=headers)
    
    # 获取订阅内容
    with urllib.request.urlopen(req) as response:
        content = response.read()

    # 解码Base64内容
    decoded = base64.b64decode(content).decode('utf-8')

    # 分割多个服务器配置
    servers = decoded.splitlines()

    # 解析每个服务器配置
    for server in servers:
        server = server.strip()  # 清除空白字符
        if server.startswith("vmess://"):
            try:
                # 移除协议头并解码
                vmess_data = server[8:]
                # 处理base64填充问题
                padding = '=' * (4 - (len(vmess_data) % 4))
                vmess_json = base64.b64decode(vmess_data + padding).decode('utf-8')
                config = json.loads(vmess_json)
                print(f"服务器: {config.get('add')}:{config.get('port')}")
                print(f"用户ID: {config.get('id')}")
                print(f"传输协议: {config.get('net')}")
                print("------")
            except (UnicodeDecodeError, json.JSONDecodeError, base64.binascii.Error) as e:
                print(f"解析配置失败: {e}")
                continue

except urllib.error.HTTPError as e:
    print(f"HTTP错误: {e.code} {e.reason}")
except urllib.error.URLError as e:
    print(f"URL错误: {e.reason}")
except Exception as e:
    print(f"发生未知错误: {str(e)}")