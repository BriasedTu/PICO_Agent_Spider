import sqlite3
import pandas as pd

def display_top_five_rows(db_name='text_data.db'):
    """
    使用Pandas读取数据库并显示前五行数据
    
    参数:
        db_name: 数据库文件名，默认为'text_data.db'
    """
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_name)
        
        # 使用Pandas读取整个表
        df = pd.read_sql_query("SELECT * FROM articles", conn)
        
        # 关闭连接
        conn.close()
        
        # 检查是否有数据
        if df.empty:
            print("数据库中没有数据")
            return
        
        # 显示前五行
        print("数据库中的前五行数据:")
        print("=" * 100)
        print(df.head())
        
        # 显示数据的基本信息
        print("\n数据基本信息:")
        print("=" * 100)
        print(f"总行数: {len(df)}")
        print(f"列名: {list(df.columns)}")
        print(f"每列的非空值数量:")
        print(df.count())
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    display_top_five_rows()