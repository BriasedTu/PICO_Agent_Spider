import re
from pathlib import Path

def process_md_file(content):
    """
    处理MD文件内容，删除重复标题及其之后的内容
    """
    # 找到第一个标题（以#开头，后跟空格和字母）
    title_pattern = r'^(#+)\s+([A-Za-z].*?)(?=\n|$)'
    match = re.search(title_pattern, content, re.MULTILINE)
    
    if not match:
        return content  # 如果没有找到标题，返回原内容
    
    first_title = match.group(0)  # 完整的标题行
    title_level = match.group(1)  # 标题级别（#的数量）
    title_text = match.group(2).strip()  # 标题文本
    
    print(f"找到第一个标题: {first_title}")
    
    # 分割内容为两部分：第一个标题之前和之后
    content_parts = content.split(first_title, 1)
    if len(content_parts) < 2:
        return content  # 如果没有分割成功，返回原内容
    
    before_first_title = content_parts[0]
    after_first_title = first_title + content_parts[1]  # 重新添加第一个标题
    
    # 构建正则表达式模式来匹配相同级别的相同标题
    # 注意：这里我们匹配相同级别和相同文本的标题
    duplicate_pattern = rf'^{title_level}\s+{re.escape(title_text)}(?=\n|$)'
    
    # 查找所有重复的标题
    duplicates = list(re.finditer(duplicate_pattern, after_first_title, re.MULTILINE))
    
    if len(duplicates) <= 1:
        return content  # 如果没有重复标题，返回原内容
    
    # 找到第二个重复标题的位置
    second_duplicate = duplicates[1]
    start_index = second_duplicate.start()
    
    # 保留第一个标题及其之前的内容，删除第二个重复标题及其之后的所有内容
    result = before_first_title + after_first_title[:start_index]
    
    print(f"已删除重复标题及其后的内容")
    return result

def process_all_md_files(input_dir="E:\Python Project\Spider\PICO_Agent\md4", output_dir="E:\Python Project\Spider\PICO_Agent\md5"):
    """
    处理输入目录中的所有MD文件，并将结果保存到输出目录
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # 确保输出目录存在
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 处理所有MD文件
    for md_file in input_path.glob('*.md'):
        print(f"处理文件: {md_file.name}")
        
        # 读取文件内容
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"读取文件 {md_file.name} 时出错: {e}")
            continue
        
        # 处理内容
        processed_content = process_md_file(content)
        
        # 保存处理后的文件
        output_file = output_path / md_file.name
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            print(f"已保存: {output_file}")
        except Exception as e:
            print(f"保存文件 {output_file} 时出错: {e}")

if __name__ == '__main__':
    process_all_md_files()
    print("处理完成!")