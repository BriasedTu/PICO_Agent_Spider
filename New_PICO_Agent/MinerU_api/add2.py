import pandas as pd

def fill_empty_clean_text(csv_path):
    """
    填充CSV文件中空的clean_text列
    :param csv_path: CSV文件路径
    """
    # 读取CSV文件
    df = pd.read_csv(csv_path, sep='|')
    
    # 计数器
    filled_count = 0
    
    # 查找clean_text为空的记录
    empty_mask = df['clean_text'].isna() | (df['clean_text'] == '')
    
    # 填充空的clean_text
    df.loc[empty_mask, 'clean_text'] = df.loc[empty_mask, 'raw_text']
    
    # 统计填充数量
    filled_count = empty_mask.sum()
    
    # 保存更新后的CSV
    df.to_csv(csv_path, sep='|', index=False)
    return filled_count

if __name__ == "__main__":
    # 配置参数
    csv_file_path = r"output.csv"  # CSV文件路径
    
    print("开始检查并填充空的clean_text列...")
    filled_count = fill_empty_clean_text(csv_file_path)
    
    if filled_count > 0:
        print(f"\n成功填充 {filled_count} 个空的clean_text记录")
        print(f"CSV文件已更新: {csv_file_path}")
    else:
        print("\n未找到任何空的clean_text记录")