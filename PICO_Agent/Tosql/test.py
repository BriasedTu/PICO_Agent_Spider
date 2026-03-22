import os
import sqlite3
import random
import string

def generate_random_id(length=32):
    """生成指定长度的随机字母数字ID"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def process_md_files(folder_path, db_name='text_data.db'):
    """
    处理指定文件夹中的所有MD文件，并将内容插入数据库
    
    参数:
        folder_path: 包含MD文件的文件夹路径
        db_name: 数据库文件名，默认为'text_data.db'
    """
    # 连接到数据库
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 获取文件夹中所有的MD文件
    md_files = [f for f in os.listdir(folder_path) if f.endswith('.md')]
    
    if not md_files:
        print(f"在文件夹 '{folder_path}' 中没有找到MD文件")
        return
    
    print(f"找到 {len(md_files)} 个MD文件，开始处理...")
    
    # 处理每个MD文件
    for i, filename in enumerate(md_files, 1):
        file_path = os.path.join(folder_path, filename)
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 分割内容：第一个|之前的部分作为source，之后的部分作为raw_text
            if '|' in content:
                source, raw_text = content.split('|', 1)
                source = source.strip()
                raw_text = raw_text.strip()
            else:
                # 如果没有|，则将整个内容作为raw_text，source设为文件名
                source = os.path.splitext(filename)[0]
                raw_text = content.strip()
            
            # 生成随机ID
            random_id = generate_random_id()
            
            # 插入数据库
            cursor.execute(
                "INSERT INTO articles (id, source, title, clean_text, raw_text) VALUES (?, ?, ?, ?, ?)",
                (random_id, source, None, None, raw_text)
            )
            
            print(f"处理进度: {i}/{len(md_files)} - {filename}")
            
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {str(e)}")
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    
    print(f"\n处理完成! 成功导入 {len(md_files)} 个文件到数据库")

def display_database_stats(db_name='text_data.db'):
    """显示数据库统计信息"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 获取记录总数
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    
    # 获取示例记录
    cursor.execute("SELECT * FROM articles LIMIT 3")
    sample_records = cursor.fetchall()
    
    conn.close()
    
    print(f"\n数据库统计:")
    print(f"总记录数: {count}")
    print("\n示例记录:")
    for record in sample_records:
        print(f"ID: {record[0]}")
        print(f"Source: {record[1]}")
        print(f"Raw Text (前100字符): {record[4][:100]}..." if len(record[4]) > 100 else f"Raw Text: {record[4]}")
        print("-" * 50)

if __name__ == "__main__":
    # 指定包含MD文件的文件夹路径
    folder_path = "E:\Python Project\Spider\PICO_Agent\md"
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
    else:
        # 处理MD文件
        process_md_files(folder_path)
        
        # 显示数据库统计信息
        display_database_stats()