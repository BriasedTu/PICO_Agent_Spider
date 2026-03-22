import os
import re
from pathlib import Path

def remove_duplicate_content(content):
    """
    移除MD文件中的重复内容
    策略：将内容分成两半，如果后半部分与前半部分高度相似，则只保留前半部分
    """
    lines = content.split('\n')
    half_len = len(lines) // 2
    
    # 如果文件太小，不需要处理重复
    if half_len < 50:
        return content
        
    first_half = '\n'.join(lines[:half_len])
    second_half = '\n'.join(lines[half_len:])
    
    # 简单检查两部分是否相似（通过检查开头和结尾）
    if first_half[:200] == second_half[:200] and first_half[-200:] == second_half[-200:]:
        return first_half
    
    return content

def clean_md_content(content):
    """
    清洗MD文件内容
    """
    # 移除重复内容
    content = remove_duplicate_content(content)
    
    # 修复常见的转换错误
    # 1. 修复被错误转换的数学符号和特殊字符
    content = re.sub(r'\\mathbf\s*\{\s*\\cdot\s*\\_\s*\{\s*\\beta\s*\}\s*\}', 'PKC-β', content)
    content = re.sub(r'\\mathbf\s*\{\s*\\cdot\s*\\_\s*\{\s*\\beta\s*\}\s*\}', 'PKC-β', content)
    content = re.sub(r'\\mathbf\s*\{\s*\\cdot\s*\\mathbf\s*\{\s*\\_\s*\{\s*\\beta\s*\}\s*\}\s*\}', 'PKC-β', content)
    content = re.sub(r'\\mathbf\s*\{\s*\\beta\s*\\cdot\s*\\beta\s*\\cdot\s*\\beta\s*\}', 'PKC-β', content)
    content = re.sub(r'\\boldsymbol\s*\{\s*\\cdot\s*\\boldsymbol\s*\{\s*\\beta\s*\}\s*\}', 'PKC-β', content)
    
    # 2. 修复表格中的格式问题
    content = re.sub(r'(\n\s*)([A-Z]+\s*[A-Z]*\s*:\s*)', r'\n## \2', content)  # 将全大写的标题转换为二级标题
    content = re.sub(r'\s*(\d+)\s*(\d+)\s*(\d+)\s*', r' \1.\2.\3 ', content)  # 修复日期格式
    
    # 3. 修复参考文献格式
    content = re.sub(r'(\d+)\s*\.\s*(\s+)', r'\1. ', content)  # 修复参考文献编号后的空格
    
    # 4. 移除多余的空行（保留最多两个连续空行）
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    # 5. 修复列表格式
    content = re.sub(r'(\n)\s*([•▪♦])\s*', r'\1- ', content)  # 统一列表符号
    content = re.sub(r'(\n)\s*(\d+)\.\s+', r'\1\2. ', content)  # 修复编号列表
    
    # 6. 修复标题格式
    content = re.sub(r'(#+)([^#\n])', r'\1 \2', content)  # 确保标题符号后有空格
    
    return content

def process_md_files():
    """
    处理输入目录中的所有MD文件，并将结果保存到输出目录
    """
    # 固定输入和输出目录
    input_dir = "E:\Python Project\Spider\PICO_Agent\md3"
    output_dir = "E:\Python Project\Spider\PICO_Agent\md4"
    
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
        
        # 清洗内容
        cleaned_content = clean_md_content(content)
        
        # 保存处理后的文件
        output_file = output_path / md_file.name
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            print(f"已保存: {output_file}")
        except Exception as e:
            print(f"保存文件 {output_file} 时出错: {e}")

def main():
    process_md_files()
    print("处理完成!")

if __name__ == '__main__':
    main()