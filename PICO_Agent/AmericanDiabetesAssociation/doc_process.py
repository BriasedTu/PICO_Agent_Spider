import os
import re

# 设置要处理的文件夹路径
folder_path = r""

if not os.path.exists(folder_path):
    print(f"文件夹不存在: {folder_path}")
    exit()

print(f"正在处理文件夹: {folder_path}\n")

kept = 0
deleted = 0

# 正则表达式匹配以 _1.扩展名 结尾的文件名
pattern = re.compile(r"^(.*?)_1(\.[^.]+)?$")

for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    
    if not os.path.isfile(file_path):
        continue
    
    # 检查是否是副本文件 (_1)
    match = pattern.match(filename)
    if match:
        # 构建原始文件名
        base_name = match.group(1) + (match.group(2) if match.group(2) else "")
        base_path = os.path.join(folder_path, base_name)
        
        # 检查原始文件是否存在
        if os.path.exists(base_path):
            try:
                os.remove(file_path)
                deleted += 1
                print(f"删除副本: '{filename}' (原始文件 '{base_name}' 存在)")
            except Exception as e:
                print(f"无法删除 '{filename}': {e}")
        else:
            kept += 1
            print(f"保留副本: '{filename}' (原始文件不存在)")
    else:
        kept += 1
        print(f"保留: '{filename}'")

print(f"\n处理完成:")
print(f"保留的文件数: {kept}")
print(f"删除的副本文件数: {deleted}")