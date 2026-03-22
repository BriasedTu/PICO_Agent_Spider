import sqlite3
import os

def create_database(db_name='text_data.db'):
    """
    创建SQLite数据库和表结构
    
    参数:
        db_name: 数据库文件名，默认为'text_data.db'
    """
    # 连接数据库（如果不存在会自动创建）
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # 创建表 - 修改为符合要求的表结构
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,  -- 改为TEXT类型以存储32位随机ID
        source TEXT NOT NULL,
        title TEXT,           -- 允许为NULL
        clean_text TEXT,      -- 允许为NULL
        raw_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建更新触发器，用于自动更新updated_at字段
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_articles_timestamp
    AFTER UPDATE ON articles
    FOR EACH ROW
    BEGIN
        UPDATE articles SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
    END
    ''')
    
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    
    print(f"数据库 '{db_name}' 创建成功，表 'articles' 已建立")
    return True

def display_data(db_name='text_data.db'):
    """
    显示数据库中的数据
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM articles')
    rows = cursor.fetchall()
    
    print("\n数据库内容:")
    print("-" * 100)
    for row in rows:
        print(f"ID: {row[0]}, Source: {row[1]}, Title: {row[2]}")
        print(f"Clean Text: {row[3][:50]}..." if row[3] and len(row[3]) > 50 else f"Clean Text: {row[3]}")
        print(f"Raw Text: {row[4][:50]}..." if row[4] and len(row[4]) > 50 else f"Raw Text: {row[4]}")
        print(f"Created: {row[5]}, Updated: {row[6]}")
        print("-" * 100)
    
    conn.close()

if __name__ == "__main__":
    # 创建数据库和表
    create_database()
    
    # 显示数据
    display_data()