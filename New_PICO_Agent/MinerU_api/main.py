import os
import time
import requests
import json
from typing import List, Dict, Tuple
from DrissionPage import SessionPage

# API配置常量
API_TOKEN = ""  # 替换为实际API令牌
GET_UPLOAD_URL_API = ""
GET_RESULT_API = ""
POLL_INTERVAL = 30  # 秒，轮询间隔
MAX_RETRIES = 10    # 最大轮询次数
BATCH_SIZE = 10    # 每批文件数量
save_path = r''

# 确保保存目录存在
os.makedirs(save_path, exist_ok=True)

def get_pdf_files(folder_path: str) -> List[str]:
    """获取文件夹中所有PDF文件路径"""
    pdf_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith('.pdf'):
            pdf_files.append(os.path.join(folder_path, file))
    return pdf_files

def process_batch(files: List[str], batch_id: str = "") -> Tuple[str, List[Dict]]:
    """
    处理一批文件：获取上传URL -> 上传文件 -> 轮询解析结果
    返回：(batch_id, 结果列表)
    """
    # 过滤掉大于30MB的文件
    filtered_files = []
    for file_path in files:
        file_size = os.path.getsize(file_path)  # 字节
        if file_size > 30 * 1024 * 1024:  # 30MB
            print(f"跳过上传（文件过大）: {file_path} ({file_size / (1024*1024):.1f} MB)")
            continue
        filtered_files.append(file_path)

    if not filtered_files:
        print("当前批次所有文件均大于30MB，跳过处理。")
        return batch_id, []  # 返回空结果

    # 1. 获取上传URL
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_TOKEN}'
    }
    
    # 构建文件元数据
    file_metas = [{
        "name": os.path.basename(f),
        "is_ocr": True,
        "data_id": f"doc_{idx}"  # 生成唯一ID
    } for idx, f in enumerate(filtered_files)]
    
    payload = {
        "model_version": "vlm",
        "files": file_metas,
        
    }
    
    response = requests.post(GET_UPLOAD_URL_API, headers=headers, json=payload)
    
    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.status_code}")
    else:
        print(f"API请求成功: {response.status_code}")
    
    result = response.json()
    
    if result.get("code") != 0:
        raise Exception(f"API错误: {result.get('msg')}")
    
    batch_id = result["data"]["batch_id"]
    upload_urls = result["data"]["file_urls"]
    
    # 2. 上传文件
    for file_path, url in zip(filtered_files, upload_urls):
        try:
            with open(file_path, 'rb') as f:
                res = requests.put(url, data=f)
                if res.status_code != 200:
                    print(f"上传失败: {file_path} - 状态码: {res.status_code}")
                else:
                    print(f"上传成功: {file_path}")
        except Exception as e:
            print(f"上传异常: {file_path} - {str(e)}")
    
    # 3. 轮询解析结果
    for retry in range(MAX_RETRIES):
        time.sleep(POLL_INTERVAL)
        
        # 查询解析状态
        url = f"{GET_RESULT_API}/{batch_id}"
        res = requests.get(url, headers=headers)
        
        if res.status_code != 200:
            print(f"状态查询失败: {res.status_code}")
            continue
            
        status_data = res.json()
        if status_data.get("code") != 0:
            print(f"状态查询错误: {status_data.get('msg')}")
            continue
            
        batch_results = status_data["data"]["extract_result"]
        print(batch_results)
        all_completed = all(item["state"] in ["done", "failed"] for item in batch_results)
        
        if all_completed:
            print(f"批次 {batch_id} 处理完成")
            # 现在构建 results 并下载（避免重复）
            results = []
            for item in batch_results:
                state = item["state"]
                result = {
                    "file_name": item["file_name"],
                    "state": state,
                    "data_id": item.get("data_id", "")
                }
                
                if state == "done":
                    result["zip_url"] = item["full_zip_url"]
                    try:
                        download(result)  # 下载
                    except Exception as e:
                        result["download_error"] = str(e)
                        print(f"下载失败: {result['file_name']} - {str(e)}")
                elif state == "failed":
                    result["error"] = item.get("err_msg", "未知错误")
                
                results.append(result)
            return batch_id, results
    
    raise Exception(f"批次 {batch_id} 处理超时")

def process_all_pdfs(folder_path: str) -> Dict[str, List[Dict]]:
    """处理文件夹中的所有PDF文件"""
    all_results = {}
    pdf_files = get_pdf_files(folder_path)
    total_files = len(pdf_files)
    
    print(f"找到 {total_files} 个PDF文件，分 {((total_files-1)//BATCH_SIZE)+1} 批处理")
    
    # 分批处理
    for i in range(0, total_files, BATCH_SIZE):
        batch_files = pdf_files[i:i+BATCH_SIZE]
        print(f"\n处理批次 #{i//BATCH_SIZE+1}: {len(batch_files)} 个文件")
        
        try:
            batch_id, results = process_batch(batch_files)
            all_results[batch_id] = results
            print(f"批次完成，结果: {len(results)} 条")
            
            # 保存中间结果
            with open(f"batch_{batch_id}.json", "w") as f:
                json.dump(results, f, indent=2)
                
        except Exception as e:
            print(f"批次处理失败: {str(e)}")
    
    return all_results

def download(result):
    zip_url = result["zip_url"]
    file_name = result["file_name"] + ".zip"  # 使用原文件名 + .zip
    full_save_path = os.path.join(save_path, file_name)  # 完整保存路径
    page.download.add(zip_url, full_save_path)  # 传入 URL 和保存路径
    print(f"下载启动: {file_name} -> {full_save_path}")

if __name__ == "__main__":
    # 配置文件夹路径
    PDF_FOLDER = r""  # 替换为实际文件夹路径
    
    # 开始处理
    page = SessionPage()
    final_results = process_all_pdfs(PDF_FOLDER)
    
    # 保存最终结果
    with open("all_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    
    print("\n处理完成! 结果已保存到 all_results.json")