import os
import uuid
import pandas as pd

def process_md_files(root_dir, output_csv):
    # 创建空列表存储所有记录
    records = []
    
    # 遍历一级子文件夹
    for source in os.listdir(root_dir):
        source_path = os.path.join(root_dir, source)
        if not os.path.isdir(source_path):
            continue
        
        # 遍历子文件夹中的md文件
        for filename in os.listdir(source_path):
            if filename.endswith('.md'):
                filepath = os.path.join(source_path, filename)
                
                # 读取文件内容
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                except UnicodeDecodeError:
                    with open(filepath, 'r', encoding='latin-1') as f:
                        content = f.read()
                
                # 获取文件名（不含扩展名）
                base_name = os.path.splitext(filename)[0]
                
                # 生成记录 - 直接使用文件名作为title，无论是否为纯数字
                record = {
                    'id': uuid.uuid4().hex,
                    'source': source.replace('_', '/'),
                    'title': base_name,  # 直接使用文件名
                    'clean_text': '',
                    'raw_text': content,
                    'url': 'None',
                    'overview': 'None'
                }
                records.append(record)
                print(f"已处理文件: {filename}")
    
    # 创建DataFrame并保存为CSV
    if records:
        df = pd.DataFrame(records)
        # 使用管道符作为分隔符，并确保正确转义特殊字符
        df.to_csv(output_csv, sep='|', index=False, encoding='utf-8')
        return len(records)
    else:
        return 0

if __name__ == "__main__":
    # 配置参数
    root_directory = r""  # 修改为您的目标文件夹路径
    output_filename = r"output.csv"                  # 输出CSV文件名
    
    print("开始处理Markdown文件...")
    processed_count = process_md_files(root_directory, output_filename)
    
    if processed_count > 0:
        print(f"\n成功处理 {processed_count} 个文件")
        print(f"CSV文件已生成: {output_filename}")
    else:
        print("\n未找到任何Markdown文件，请检查路径设置")