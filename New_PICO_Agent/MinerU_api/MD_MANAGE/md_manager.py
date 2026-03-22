import os
import re
import shutil
from pathlib import Path

def clean_md_files(folder_path: str):
    """
    处理指定文件夹中的所有.md文件：
    1. 从文件名中删除第一个出现的".pdf"
    2. 删除文件名末尾带有"_数字"的重复文件
    
    :param folder_path: 要处理的文件夹路径
    """
    # 计数器
    renamed_count = 0
    removed_count = 0
    skipped_count = 0
    
    print(f"开始处理文件夹: {folder_path}")
    print("=" * 50)
    
    # 第一步：重命名文件，删除文件名中的".pdf"
    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            # 检查文件名中是否包含".pdf"
            if ".pdf" in filename:
                # 创建新文件名（只删除第一个出现的".pdf"）
                new_name = filename.replace(".pdf", "", 1)
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_name)
                
                # 避免覆盖现有文件
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    print(f"重命名: '{filename}' -> '{new_name}'")
                    renamed_count += 1
                else:
                    print(f"跳过重命名: '{filename}' -> '{new_name}' (目标文件已存在)")
                    skipped_count += 1
    
    print("\n" + "=" * 50)
    print("开始删除重复文件")
    print("=" * 50)
    
    # 第二步：删除文件名末尾带有"_数字"的重复文件
    # 创建一个字典来跟踪基础文件名
    base_files = {}
    
    # 首先收集所有文件并分类
    for filename in os.listdir(folder_path):
        if filename.endswith('.md'):
            # 匹配文件名末尾的"_数字"模式
            match = re.match(r'^(.*?)(?:_\d+)?\.md$', filename)
            if match:
                base_name = match.group(1) + '.md'
                
                # 检查是否是基础文件（无数字后缀）
                if filename == base_name:
                    base_files[base_name] = filename
                else:
                    # 检查基础文件是否存在
                    if base_name in base_files:
                        # 基础文件存在，删除当前文件
                        file_path = os.path.join(folder_path, filename)
                        os.remove(file_path)
                        print(f"删除重复文件: '{filename}' (基础文件 '{base_name}' 存在)")
                        removed_count += 1
                    else:
                        # 基础文件不存在，保留当前文件
                        print(f"保留文件: '{filename}' (无基础文件)")
                        skipped_count += 1
    
    # 打印摘要
    print("\n" + "=" * 50)
    print("处理完成!")
    print(f"重命名文件数: {renamed_count}")
    print(f"删除重复文件数: {removed_count}")
    print(f"跳过文件数: {skipped_count}")
    print("=" * 50)

if __name__ == "__main__":
    # 配置要处理的文件夹路径
    TARGET_FOLDER = r""  # 替换为您的文件夹路径
    
    # 确保文件夹存在
    if not os.path.exists(TARGET_FOLDER):
        print(f"错误: 文件夹 '{TARGET_FOLDER}' 不存在!")
    
        exit(1)
    
    # 执行处理
    clean_md_files(TARGET_FOLDER)