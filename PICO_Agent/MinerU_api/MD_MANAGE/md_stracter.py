import os
import shutil
from pathlib import Path

def collect_and_rename_md_files(root_dir, output_dir):
    """
    遍历根目录下的一级子文件夹，找到每个子文件夹中的full.md文件，
    将其复制到输出目录并重命名为子文件夹名称
    
    :param root_dir: 根目录路径
    :param output_dir: 输出目录路径
    """
    # 确保输出目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 计数器
    files_copied = 0
    files_skipped = 0
    
    print(f"开始处理根目录: {root_dir}")
    print(f"输出目录: {output_dir}")
    
    # 遍历根目录下的一级子文件夹
    for entry in os.scandir(root_dir):
        if entry.is_dir():
            subdir_name = entry.name
            md_file_path = os.path.join(entry.path, "full.md")
            
            if os.path.exists(md_file_path):
                # 创建新文件名：子文件夹名称 + .md
                new_filename = f"{subdir_name}.md"
                output_path = os.path.join(output_dir, new_filename)
                
                # 复制并重命名文件
                shutil.copy2(md_file_path, output_path)
                print(f"已复制: '{md_file_path}' -> '{output_path}'")
                files_copied += 1
            else:
                print(f"未找到: '{md_file_path}' (跳过)")
                files_skipped += 1
    
    # 打印摘要
    print("\n处理完成!")
    print(f"总子文件夹数: {files_copied + files_skipped}")
    print(f"成功复制文件数: {files_copied}")
    print(f"跳过文件夹数: {files_skipped}")
    print(f"所有文件已保存到: {output_dir}")

if __name__ == "__main__":
    # 配置路径
    ROOT_DIRECTORY = r""  # 替换为你的根目录路径
    OUTPUT_DIRECTORY = r""  # 替换为输出目录路径
    
    # 执行操作
    collect_and_rename_md_files(ROOT_DIRECTORY, OUTPUT_DIRECTORY)