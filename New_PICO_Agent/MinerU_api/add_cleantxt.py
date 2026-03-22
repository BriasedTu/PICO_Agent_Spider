import os
import pandas as pd
import re

def update_clean_text(csv_path, clean_md_root_dir):
    """
    更新CSV文件中的clean_text列
    :param csv_path: CSV文件路径
    :param clean_md_root_dir: 清洗后的MD文件根目录
    """
    # 读取CSV文件
    df = pd.read_csv(csv_path, sep='|')
    
    # 创建映射字典：{(source, title): index}
    mapping = {}
    for idx, row in df.iterrows():
        key = (row['source'], row['title'])
        mapping[key] = idx
    
    # 计数器
    updated_count = 0
    skipped_count = 0
    
    # 遍历清洗后的MD文件根目录
    for source_folder in os.listdir(clean_md_root_dir):
        source_path = os.path.join(clean_md_root_dir, source_folder)
        if not os.path.isdir(source_path):
            continue
        
        # 转换source格式（下划线转斜杠）
        csv_source = source_folder.replace('_', '/')
        
        # 遍历MD文件
        for md_file in os.listdir(source_path):
            if not md_file.endswith('.md'):
                continue
            
            # 获取文件名（不含扩展名）
            base_name = os.path.splitext(md_file)[0]
            
            # 尝试在映射中查找对应的记录
            key = (csv_source, base_name)
            if key not in mapping:
                print(f"⚠️ 未找到匹配记录: source={csv_source}, title={base_name}")
                skipped_count += 1
                continue
            
            # 读取清洗后的MD文件内容
            file_path = os.path.join(source_path, md_file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 更新DataFrame中的clean_text
                idx = mapping[key]
                df.at[idx, 'clean_text'] = content
                updated_count += 1
                print(f"✅ 已更新: {source_folder}/{md_file}")
            
            except Exception as e:
                print(f"❌ 读取失败 {file_path}: {str(e)}")
                skipped_count += 1
    
    # 保存更新后的CSV
    df.to_csv(csv_path, sep='|', index=False)
    return updated_count, skipped_count

if __name__ == "__main__":
    # 配置参数
    csv_file_path = "output.csv"          # CSV文件路径
    clean_md_directory = r""  # 清洗后的MD文件根目录
    
    print("开始更新clean_text内容...")
    updated_count, skipped_count = update_clean_text(csv_file_path, clean_md_directory)
    
    if updated_count > 0:
        print(f"\n成功更新 {updated_count} 个文件的clean_text内容")
        print(f"跳过 {skipped_count} 个文件（未找到匹配记录或读取失败）")
        print(f"CSV文件已更新: {csv_file_path}")
    else:
        print("\n未找到任何匹配的MD文件")