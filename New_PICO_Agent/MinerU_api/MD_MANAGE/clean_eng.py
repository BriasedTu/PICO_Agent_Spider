import os
from langdetect import detect

# ================== 配置区域 ================== #
# 在此设置要处理的Markdown文件夹路径
TARGET_DIRECTORY = r""  # 替换为你的实际路径
# ============================================= #

def detect_lang(text, sample_size=10000):
    """检测文本语言"""
    if not text.strip():
        return 'empty'
    
    # 采样部分文本进行检测（提高效率）
    sample = text if len(text) < sample_size else text[:sample_size]
    
    try:
        language = detect(sample)
    except:
        language = 'unknown'
    return language

def process_directory(directory_path):
    """处理目录中的所有Markdown文件，删除非英语文件"""
    stats = {
        'total': 0,
        'english': 0,
        'non_english': 0,
        'empty': 0,
        'errors': 0
    }
    
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if not filename.lower().endswith('.md'):
                continue
                
            filepath = os.path.join(root, filename)
            stats['total'] += 1
            
            try:
                # 读取文件内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测语言
                lang = detect_lang(content)
                
                # 处理非英文文档
                if lang != 'en':
                    os.remove(filepath)
                    print(f"🗑️ 删除非英文文件: {filepath} (检测语言: {lang})")
                    stats['non_english'] += 1
                    continue
                
                # 处理空文档
                if not content.strip():
                    os.remove(filepath)
                    print(f"🗑️ 删除空文件: {filepath}")
                    stats['empty'] += 1
                    continue
                
                print(f"✅ 保留英文文件: {filepath}")
                stats['english'] += 1
                
            except Exception as e:
                print(f"❌ 处理失败 {filepath}: {str(e)}")
                stats['errors'] += 1
    
    return stats

def main():
    """主程序入口"""
    # 验证目录存在
    if not os.path.isdir(TARGET_DIRECTORY):
        print(f"错误：目录不存在 - {TARGET_DIRECTORY}")
        print("请修改程序中的 TARGET_DIRECTORY 变量为有效路径")
        return
    
    print("=" * 60)
    print(f"Markdown文件语言检测工具")
    print(f"目标目录: {TARGET_DIRECTORY}")
    print("=" * 60)
    print("开始处理文件...\n")
    
    # 处理目录中的所有Markdown文件
    stats = process_directory(TARGET_DIRECTORY)
    
    print("\n" + "=" * 60)
    print("处理完成! 统计结果:")
    print(f"扫描文件总数: {stats['total']}")
    print(f"保留英文文件: {stats['english']}")
    print(f"删除非英文文件: {stats['non_english']}")
    print(f"删除空文件: {stats['empty']}")
    print(f"处理失败文件: {stats['errors']}")
    print("=" * 60)

if __name__ == "__main__":
    # 确保已安装langdetect库
    try:
        import langdetect
    except ImportError:
        print("错误: 需要安装langdetect库，请运行: pip install langdetect")
        exit(1)
    
    main()