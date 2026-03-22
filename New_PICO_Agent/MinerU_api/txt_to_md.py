import os

def convert_txt_to_md(folder_path):
    """
    将指定文件夹中的所有txt文件转换为md文件
    :param folder_path: 要处理的文件夹路径
    """
    # 计数器
    converted_count = 0
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        # 检查文件是否为txt文件
        if filename.endswith('.txt'):
            # 构建完整的文件路径
            txt_path = os.path.join(folder_path, filename)
            
            # 构建新的md文件名
            md_filename = filename[:-4] + '.md'  # 去掉.txt后缀，加上.md
            md_path = os.path.join(folder_path, md_filename)
            
            # 重命名文件
            os.rename(txt_path, md_path)
            print(f"已将文件重命名: {filename} → {md_filename}")
            converted_count += 1
    
    print(f"\n转换完成! 共转换了 {converted_count} 个文件")

if __name__ == "__main__":
    # 输入要处理的文件夹路径
    target_folder = r""
    
    # 验证路径是否存在
    if not os.path.isdir(target_folder):
        print(f"错误: 路径 '{target_folder}' 不存在或不是文件夹")
    else:
        convert_txt_to_md(target_folder)