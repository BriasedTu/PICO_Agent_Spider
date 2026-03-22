import re
import os
from pathlib import Path

def extract_sections_from_csv(csv_file_path, output_folder, min_length=16, min_content_length=5000):
    """
    从 CSV 文件中提取特定模式之间的文本内容并保存为 Markdown 文件
    
    参数:
    csv_file_path (str): CSV 文件的路径
    output_folder (str): 输出文件夹路径
    min_length (int): 标记字符串的最小长度
    min_content_length (int): 内容最小长度阈值
    """
    # 确保输出文件夹存在
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    
    # 读取 CSV 文件内容作为纯文本
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(csv_file_path, 'r', encoding='latin-1') as file:
                content = file.read()
        except Exception as e:
            print(f"无法读取文件: {e}")
            return
    
    # 正则表达式匹配长字符串后跟|符号的模式
    pattern = re.compile(r'\b[a-zA-Z0-9]{%d,}\b\|' % min_length)
    
    # 找到所有匹配的位置
    matches = list(pattern.finditer(content))
    print(f"找到 {len(matches)} 个标记")
    
    # 如果没有足够的标记，直接返回
    if len(matches) < 2:
        print("需要至少两个标记才能提取内容")
        return
    
    file_counter = 0
    
    # 提取每两个标记之间的内容
    for i in range(len(matches) - 1):
        start_pos = matches[i].end()  # 当前标记结束位置
        end_pos = matches[i+1].start()  # 下一个标记开始位置
        
        # 提取两个标记之间的文本
        section_content = content[start_pos:end_pos].strip()
        
        # 如果内容为空或太短，跳过
        if not section_content or len(section_content) < min_content_length:
            continue
        
        # 创建文件名
        filename = f"section_{file_counter}.md"
        file_counter += 1
        
        # 写入 Markdown 文件
        output_file = output_path / filename
        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write(section_content)
        
        print(f"已创建: {filename} (长度: {len(section_content)})")

if __name__ == "__main__":
    # 设置文件路径
    csv_path = ""
    output_dir = ""
    
    # 执行提取
    extract_sections_from_csv(csv_path, output_dir, min_length=32, min_content_length=5000)
    print("处理完成!")