import os
import time
import requests
import json
from typing import List, Dict

POLL_INTERVAL = 30  # 秒，轮询间隔
MAX_RETRIES = 100    # 最大轮询次数
BATCH_SIZE = 50    # 每批文件数量
SAVE_PATH = r'D:\pyproject\Spider\PubMed\WHO_CN\WHO_CN'  # 下载保存路径

def get_pdf_files(folder_path: str) -> List[str]:
    """获取文件夹中所有PDF文件路径"""
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, file))
    return pdf_files

def process_batch(batch_files: List[str]) -> List[Dict]:
    """处理一批文件"""
    url1 = 'https://mineru.net/api/v4/file-urls/batch'
    header = {
        'Content-Type': 'application/json',
        'Authorization': ''  # 填入您的API密钥
    }
    
    # 构建文件元数据
    file_metas = [{
        "name": os.path.basename(f),
        "is_ocr": True,
        "data_id": f"doc_{idx}"  # 生成唯一ID
    } for idx, f in enumerate(batch_files)]
    
    data = {
        "enable_formula": True,
        "language": "en",
        "enable_table": True,
        "files": file_metas
    }

    try:
        response = requests.post(url1, headers=header, json=data)
        if response.status_code == 200:
            result = response.json()
            print('API响应成功:', result)
            
            if result["code"] == 0:
                batch_id = result["data"]["batch_id"]
                upload_urls = result["data"]["file_urls"]
                print(f"获取到批处理ID: {batch_id}")
                
                # 上传文件
                for file_path, url in zip(batch_files, upload_urls):
                    with open(file_path, 'rb') as f:
                        res_upload = requests.put(url, data=f)
                        if res_upload.status_code == 200:
                            print(f"文件上传成功: {os.path.basename(file_path)}")
                        else:
                            print(f"文件上传失败: {os.path.basename(file_path)}")
                
                # 轮询解析状态
                print("开始查询解析状态...")
                for attempt in range(MAX_RETRIES):
                    time.sleep(POLL_INTERVAL)
                    
                    # 查询解析状态
                    url2 = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
                    res = requests.get(url2, headers=header)
                    
                    if res.status_code != 200:
                        print(f"状态查询失败(尝试 {attempt+1}): {res.status_code}")
                        continue
                    
                    status_data = res.json()
                    if status_data.get("code") != 0:
                        print(f"状态查询错误(尝试 {attempt+1}): {status_data.get('msg', '未知错误')}")
                        continue
                    
                    batch_results = status_data["data"]["extract_result"]
                    all_completed = True
                    results = []
                    
                    for item in batch_results:
                        state = item["state"]
                        file_name = item["file_name"]
                        
                        if state not in ["done", "failed"]:
                            all_completed = False
                            print(f"文件处理中: {file_name} - 状态: {state}")
                        elif state == "done":
                            # 下载结果
                            zip_url = item["full_zip_url"]
                            print(f"下载处理结果: {file_name}")
                            
                            # 下载ZIP文件
                            zip_response = requests.get(zip_url)
                            if zip_response.status_code == 200:
                                zip_path = os.path.join(SAVE_PATH, f"{file_name}.zip")
                                with open(zip_path, 'wb') as f:
                                    f.write(zip_response.content)
                                print(f"结果已保存: {zip_path}")
                            else:
                                print(f"下载失败: {file_name}")
                            
                            results.append({
                                "file_name": file_name,
                                "state": state,
                                "zip_url": zip_url
                            })
                        elif state == "failed":
                            error_msg = item.get("err_msg", "未知错误")
                            print(f"文件处理失败: {file_name} - {error_msg}")
                            results.append({
                                "file_name": file_name,
                                "state": state,
                                "error": error_msg
                            })
                    
                    if all_completed:
                        print(f"批次 {batch_id} 处理完成")
                        return results
                
                print(f"批次 {batch_id} 处理超时")
                return []
            else:
                print('申请上传URL失败:', result.get('msg', '未知错误'))
        else:
            print('API响应失败:', response.status_code, response.text)
    except Exception as err:
        print("处理过程中出错:", str(err))
    
    return []

def process_all_pdfs(folder_path: str):
    """处理文件夹中的所有PDF文件"""
    pdf_files = get_pdf_files(folder_path)
    total_files = len(pdf_files)
    
    if total_files == 0:
        print("未找到PDF文件")
        return
    
    print(f"找到 {total_files} 个PDF文件，分 {((total_files-1)//BATCH_SIZE)+1} 批处理")
    
    # 分批处理
    all_results = []
    for i in range(0, total_files, BATCH_SIZE):
        batch_files = pdf_files[i:i+BATCH_SIZE]
        print(f"\n处理批次 #{i//BATCH_SIZE+1}: {len(batch_files)} 个文件")
        
        try:
            results = process_batch(batch_files)
            all_results.extend(results)
            print(f"批次完成，获取 {len(results)} 条结果")
                    
        except Exception as e:
            print(f"批次处理失败: {str(e)}")
    
    # 保存所有结果
    with open(os.path.join(SAVE_PATH, "all_results.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    
    return all_results

if __name__ == "__main__":
    # 创建保存目录
    os.makedirs(SAVE_PATH, exist_ok=True)
    
    # 配置文件夹路径
    PDF_FOLDER = r"D:\pyproject\Spider\PubMed\WHO_CN"
    
    # 开始处理
    final_results = process_all_pdfs(PDF_FOLDER)
    
    print("\n处理完成! 结果已保存到:", os.path.join(SAVE_PATH, "all_results.json"))