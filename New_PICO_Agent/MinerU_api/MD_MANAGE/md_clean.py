import os
import re

# ================== 配置区域 ================== #
# 在此设置要处理的Markdown文件夹路径
TARGET_DIRECTORY = r""  # 替换为你的实际路径
# ============================================= #

def remove_urls(text):
    """移除文本中的所有URL"""
    return re.sub(
        r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%|\-)*\b', '', 
        text, flags=re.MULTILINE)

def remove_references(text):
    """移除参考文献标记和链接"""
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\[\d+\]', '', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)
    return text

def normalize_sections(text, max_hashes=3):
    """规范化标题层级（1-3级）"""
    if '\n#' not in text: 
        return text
    min_hashes = min([len(x)-1 for x in re.findall(r'\n#+', text)])
    text = re.sub(r'\n' + '#' * min_hashes, '\n#', text)
    text = re.sub(r'\n#{%d,}' % (max_hashes), '\n' + '#' * max_hashes, text)
    return text

def normalize_lists(text): 
    """统一列表符号为破折号"""
    text = re.sub(r'\n\* ', '\n- ', text)
    text = re.sub(r'\n•', '\n-', text)
    text = re.sub(r'\no', '\n-', text)
    text = re.sub(r'\n', '\n-', text)
    text = re.sub(r'\n\+ ', '\n- ', text)
    text = text.replace('• ', '- ')
    text = re.sub(r'\* ', '- ', text)
    return text

def remove_weird_chars(text):
    """移除特殊字符和符号"""
    text = re.sub(r'◆', '', text)
    text = re.sub(r'•', '', text)
    text = re.sub(r'', '', text)
    text = re.sub(r'▪', '', text)
    text = re.sub(r'■', '', text)
    text = re.sub(r'□', '', text)
    text = re.sub(r'\*-', '', text)
    text = re.sub(r'\n>', '\n', text)
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'�', '', text)
    return text

def normalize_newlines(text):
    """规范化换行符和空行"""
    new_text = ''
    for line in text.split('\n'):
        line_an = re.sub(r'[^a-zA-Z ]', '', line).strip()
        if line_an == '':
            continue
        else: 
            new_text += line + '\n' 
    text = new_text
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    text = re.sub(r'\n#', '\n\n#', text)
    return text

def clean_markdown(text): 
    """
    完整的Markdown清洗流程：
    1. 移除URL
    2. 移除参考文献标记
    3. 统一列表格式
    4. 移除特殊字符
    5. 规范化标题层级
    6. 规范化换行符
    """
    text = remove_urls(text)
    text = remove_references(text)
    text = normalize_lists(text)
    text = remove_weird_chars(text)
    text = normalize_sections(text)
    text = normalize_newlines(text)
    return text.strip()

def process_directory(directory_path):
    """处理目录中的所有Markdown文件"""
    processed_count = 0
    error_count = 0
    
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith('.md'):
                filepath = os.path.join(root, filename)
                try:
                    # 读取原始内容
                    with open(filepath, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    # 应用清洗流程
                    cleaned_content = clean_markdown(original_content)
                    
                    # 写回清洗后的内容
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                    
                    print(f"✅ 成功处理: {filepath}")
                    processed_count += 1
                
                except Exception as e:
                    print(f"❌ 处理失败 {filepath}: {str(e)}")
                    error_count += 1
    
    return processed_count, error_count

def main():
    """主程序入口"""
    # 验证目录存在
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"错误：目录不存在 - {TARGET_DIRECTORY}")
        print("请修改程序中的 TARGET_DIRECTORY 变量为有效路径")
        return
    
    print("=" * 50)
    print(f"Markdown文件清洗工具")
    print(f"目标目录: {TARGET_DIRECTORY}")
    print("=" * 50)
    print("开始处理文件...\n")
    
    # 处理目录中的所有Markdown文件
    processed, errors = process_directory(TARGET_DIRECTORY)
    
    print("\n" + "=" * 50)
    print(f"处理完成!")
    print(f"成功处理文件: {processed} 个")
    print(f"处理失败文件: {errors} 个")
    print("=" * 50)

if __name__ == "__main__":
    main()