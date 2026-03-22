import csv
import os
import re

def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    # 移除非法字符（Windows和Unix/Linux中不允许的字符）
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def csv_to_markdown_files(csv_file_path, output_folder):
    """
    从CSV文件中读取数据，将每个raw_text内容保存为Markdown文件
    
    参数:
    csv_file_path (str): CSV文件的路径
    output_folder (str): 输出Markdown文件的文件夹路径
    """
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"创建输出文件夹: {output_folder}")
    
    # 统计处理的文件数量
    count = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # 使用DictReader以便通过列名访问数据
            reader = csv.DictReader(csvfile)
            
            # 检查必要的列是否存在
            if 'title' not in reader.fieldnames or 'clean_text' not in reader.fieldnames:
                print("错误: CSV文件中必须包含'title'和'raw_text'列")
                return
            
            for row in reader:
                # 获取title和raw_text
                title = row['title'].strip()
                raw_text = row['clean_text']
                
                # 如果title为空，跳过此行
                if not title:
                    print("警告: 跳过无标题的行")
                    continue
                
                # 清理文件名
                safe_title = sanitize_filename(title)
                
                # 创建Markdown文件名
                md_filename = f"{safe_title}.md"
                md_filepath = os.path.join(output_folder, md_filename)
                
                # 写入Markdown文件
                try:
                    with open(md_filepath, 'w', encoding='utf-8') as md_file:
                        md_file.write(raw_text)
                    count += 1
                    print(f"已创建: {md_filename}")
                except Exception as e:
                    print(f"错误: 无法写入文件 {md_filename}: {str(e)}")
    
    except FileNotFoundError:
        print(f"错误: 找不到CSV文件 '{csv_file_path}'")
    except Exception as e:
        print(f"错误: 处理CSV文件时发生错误: {str(e)}")
    
    print(f"\n处理完成! 共创建了 {count} 个Markdown文件。")

if __name__ == "__main__":
    # 输入CSV文件路径
    csv_path = "E:\Python Project\Spider\PICO_Agent\MinerU_api\output.csv"
    
    # 输出文件夹路径
    output_dir = "E:\Python Project\Spider\PICO_Agent\md"
    
    # 如果未提供输出文件夹，使用默认值
    if not output_dir:
        output_dir = "markdown_output"
        print(f"使用默认输出文件夹: {output_dir}")
    
    # 执行转换
    csv_to_markdown_files(csv_path, output_dir)



    eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiIxODkwNjk2NCIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2MjQxODcyOSwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiMTk5NDEyMDQ1MzgiLCJvcGVuSWQiOm51bGwsInV1aWQiOiI3ZWJiMTdhNS05OWQwLTQzNGEtOTE4Yi1lNmY5ZThiOTZjMmQiLCJlbWFpbCI6IiIsImV4cCI6MTc2MzYyODMyOX0.oyk0HcNUEr9mtMGGhuo1mdObu67YXYfNpllniAZNFRbOjDb88D3RngmcTqbS--vYEKKdMnSO47_fMZnsBNpkGA