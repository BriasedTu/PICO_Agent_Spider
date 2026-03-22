import os
import re

def process_md_files(input_dir, output_dir):
    """
    处理文件夹中的所有md文件，根据第一个和第二个|符号之间的内容重命名
    如果结果是纯数字，则使用第二个|符号到第一个换行符之间的内容
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 获取所有md文件
    md_files = [f for f in os.listdir(input_dir) if f.endswith('.md')]
    
    print(f"找到 {len(md_files)} 个Markdown文件")
    
    for i, file in enumerate(md_files):
        input_path = os.path.join(input_dir, file)
        
        try:
            # 读取文件内容
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找第一个和第二个|符号的位置
            first_bar_index = content.find('|')
            
            if first_bar_index == -1:
                # 如果没有找到|符号，使用默认文件名
                filename = f"document_{i+1}"
            else:
                # 查找第二个|符号
                second_bar_index = content.find('|', first_bar_index + 1)
                
                if second_bar_index == -1:
                    # 如果只有一个|符号，取|后的内容
                    extracted_text = content[first_bar_index + 1:].strip()
                else:
                    # 提取两个|符号之间的内容
                    extracted_text = content[first_bar_index + 1:second_bar_index].strip()
                
                # 清理文本作为文件名
                filename = clean_text_for_filename(extracted_text)
                
                # 检查是否是纯数字
                if filename.isdigit():
                    # 如果是纯数字，使用第二个|到第一个换行符之间的内容
                    if second_bar_index != -1:
                        # 查找第二个|后的第一个换行符
                        next_newline = content.find('\n', second_bar_index)
                        if next_newline != -1:
                            # 提取第二个|到换行符之间的内容
                            alt_text = content[second_bar_index + 1:next_newline].strip()
                            alt_filename = clean_text_for_filename(alt_text)
                            
                            # 如果替代文件名不是纯数字且不为空，使用它
                            if alt_filename and not alt_filename.isdigit():
                                filename = alt_filename
                
                # 如果处理后的文件名为空或长度超过25，取前25个字符
                if not filename or len(filename) > 150:
                    short_text = extracted_text[:150] if extracted_text else f"document_{i+1}"
                    filename = clean_text_for_filename(short_text)
            
            # 确保文件名不为空且不是纯数字
            if not filename or filename.isdigit():
                filename = f"document_{i+1}"
            
            # 添加文件扩展名
            output_filename = f"{filename}.md"
            output_path = os.path.join(output_dir, output_filename)
            
            # 处理可能的文件名冲突
            counter = 1
            original_output_path = output_path
            while os.path.exists(output_path):
                name, ext = os.path.splitext(original_output_path)
                output_path = f"{name}_{counter}{ext}"
                counter += 1
            
            # 复制文件到新位置
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"已处理 {i+1}/{len(md_files)}: {file} -> {os.path.basename(output_path)}")
            
        except Exception as e:
            print(f"处理文件 {file} 时出错: {str(e)}")
    
    print("处理完成!")

def clean_text_for_filename(text):
    """
    清理文本，使其适合作为文件名
    """
    # 去除特殊符号，只保留字母、数字、空格和中文
    cleaned = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    # 转换为大写
    cleaned = cleaned.upper()
    # 去除多余空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # 将空格替换为下划线
    cleaned = cleaned.replace(' ', '_')
    
    return cleaned

if __name__ == "__main__":
    input_dir = r"E:\Python Project\Spider\PICO_Agent\md"
    output_dir = r"E:\Python Project\Spider\PICO_Agent\md2"
    
    # 检查输入文件夹是否存在
    if not os.path.exists(input_dir):
        print(f"错误: 输入文件夹 '{input_dir}' 不存在!")
        exit(1)
    
    process_md_files(input_dir, output_dir)