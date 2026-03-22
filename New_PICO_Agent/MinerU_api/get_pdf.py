import requests
import time

token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIxODkwNjk2NCIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2MjQxODcyOSwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTk5NDEyMDQ1MzgiLCJvcGVuSWQiOm51bGwsInV1aWQiOiI3ZWJiMTdhNS05OWQwLTQzNGEtOTE4Yi1lNmY5ZThiOTZjMmQiLCJlbWFpbCI6IiIsImV4cCI6MTc2MzYyODMyOX0.oyk0HcNUEr9mtMGGhuo1mdObu67YXYfNpllniAZNFRbOjDb88D3RngmcTqbS--vYEKKdMnSO47_fMZnsBNpkGA"
url = "https://mineru.net/api/v4/file-urls/batch"
header = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}
data = {
    "files": [
        {"name":"demo.pdf", "data_id": "abcd"}
    ]
}
file_path = [r"E:\Python Project\Spider\PICO_Agent\PDFTEST\10.1002-14651858.CD000222.pub4.pdf"]
try:
    response = requests.post(url,headers=header,json=data)
    if response.status_code == 200:
        result = response.json()
        print('response success. result:{}'.format(result))
        if result["code"] == 0:
            batch_id = result["data"]["batch_id"]
            urls = result["data"]["file_urls"]
            print('batch_id:{},urls:{}'.format(batch_id, urls))
            for i in range(0, len(urls)):
                with open(file_path[i], 'rb') as f:
                    res_upload = requests.put(urls[i], data=f)
                    if res_upload.status_code == 200:
                        print(f"{urls[i]} upload success\n")
                    else:
                        print(f"{urls[i]} upload failed\n")
        else:
            print('apply upload url failed,reason:{}'.format(result.msg))
    else:
        print('response not success. status:{} ,result:{}'.format(response.status_code, response))
    time.sleep(20)
    url2 = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"

    print("以下是结果\n")
    res = requests.get(url, headers=header)
    status_data = res.json()
            
    batch_results = status_data["data"]["extract_result"]

    print(batch_results["full_zip_url"])
    print(batch_results["state"])
    print(batch_results["err_msg"])

except Exception as err:
    print(err)