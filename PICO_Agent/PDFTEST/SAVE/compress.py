import os
import zipfile
import shutil

def extract_and_rename_md(root_folder: str, output_folder: str = None):
    """
    遍历根文件夹下的每个子文件夹，解压其中的ZIP压缩文件，
    找到解压后的.md文件，并重命名为子文件夹的名字。
    
    :param root_folder: 根文件夹路径（包含多个子文件夹）
    :param output_folder: 可选，输出重命名.md文件的目录（默认使用根文件夹）
    """
    if output_folder is None:
        output_folder = root_folder
    
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历根文件夹下的直接子文件夹
    for subdir in os.listdir(root_folder):
        subdir_path = os.path.join(root_folder, subdir)
        
        # 只处理文件夹
        if not os.path.isdir(subdir_path):
            continue
        
        print(f"处理子文件夹: {subdir}")
        
        # 在子文件夹中查找ZIP文件（假设每个子文件夹有至少一个ZIP）
        zip_files = [f for f in os.listdir(subdir_path) if f.lower().endswith('.zip')]
        
        if not zip_files:
            print(f"  未找到ZIP文件，跳过: {subdir}")
            continue
        
        # 对于每个ZIP文件进行解压（如果有多个，逐个处理）
        for zip_file in zip_files:
            zip_path = os.path.join(subdir_path, zip_file)
            extract_dir = os.path.join(subdir_path, f"extracted_{os.path.splitext(zip_file)[0]}")
            
            # 创建解压目录
            os.makedirs(extract_dir, exist_ok=True)
            
            # 解压ZIP
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                print(f"  解压成功: {zip_file} 到 {extract_dir}")
            except Exception as e:
                print(f"  解压失败: {zip_file} - {str(e)}")
                continue
            
            # 在解压目录中递归查找.md文件（假设至多一个）
            md_files = []
            for root, _, files in os.walk(extract_dir):
                for file in files:
                    if file.lower().endswith('.md'):
                        md_files.append(os.path.join(root, file))
            
            if not md_files:
                print(f"  未找到.md文件在解压目录: {extract_dir}")
                # 可选：清理解压目录
                shutil.rmtree(extract_dir)
                continue
            
            if len(md_files) > 1:
                print(f"  警告: 找到多个.md文件 ({len(md_files)}) 在 {extract_dir}，只处理第一个")
            
            # 处理第一个.md文件
            md_path = md_files[0]
            new_md_name = f"{subdir}.md"  # 重命名为子文件夹名字 + .md
            new_md_path = os.path.join(output_folder, new_md_name)
            
            # 重命名并移动到输出目录
            try:
                os.rename(md_path, new_md_path)
                print(f"  重命名成功: {os.path.basename(md_path)} -> {new_md_name} (移动到 {output_folder})")
            except Exception as e:
                print(f"  重命名失败: {str(e)}")
            
            # 可选：清理解压目录和原ZIP（根据需要 uncomment）
            # shutil.rmtree(extract_dir)
            # os.remove(zip_path)
    
    print("\n处理完成！所有.md文件已重命名并保存到输出目录。")

if __name__ == "__main__":
    # 配置根文件夹路径（替换为实际路径）
    ROOT_FOLDER = r""  # 示例路径，您可以修改
    OUTPUT_FOLDER = r""  # 可选输出目录，设为None则用根文件夹
    
    extract_and_rename_md(ROOT_FOLDER, OUTPUT_FOLDER)