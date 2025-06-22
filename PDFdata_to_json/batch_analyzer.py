from financial_analyzer import FinancialAnalyzer
from config import DEEPSEEK_API_KEY
import os
from pathlib import Path

def batch_analyze_markdown_files(markdown_dir="../results"):
    """
    批量分析markdown文件夹中的所有markdown文件
    :param markdown_dir: 包含markdown文件的目录
    """
    if DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        print("请先在config.py中配置DeepSeek API密钥")
        return
    
    analyzer = FinancialAnalyzer(DEEPSEEK_API_KEY)
    markdown_path = Path(markdown_dir)
    
    if not markdown_path.exists():
        print(f"Markdown目录不存在: {markdown_path}")
        return
    
    # 递归查找所有markdown文件
    markdown_files = list(markdown_path.rglob("*.md"))
    
    if not markdown_files:
        print("目录中没有找到markdown文件")
        return
    
    print(f"找到 {len(markdown_files)} 个markdown文件，开始批量分析...")
    
    success_count = 0
    failed_files = []
    
    for i, markdown_file in enumerate(markdown_files, 1):
        print(f"\n进度: {i}/{len(markdown_files)}")
        print(f"正在处理: {markdown_file.name}")
        
        # 生成输出文件名
        output_filename = f"financial_analysis_{markdown_file.stem}_{i:03d}.json"
        
        result = analyzer.analyze_markdown_file(str(markdown_file), output_filename)
        
        if result:
            success_count += 1
            print(f"✓ {markdown_file.name} 分析成功")
        else:
            failed_files.append(markdown_file.name)
            print(f"✗ {markdown_file.name} 分析失败")
    
    print(f"\n=== 批量分析完成 ===")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {len(failed_files)} 个文件")
    
    if failed_files:
        print("\n失败的文件:")
        for file in failed_files:
            print(f"  - {file}")

def analyze_single_markdown(markdown_file_path):
    """
    分析单个markdown文件
    :param markdown_file_path: markdown文件路径
    """
    if DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        print("请先在config.py中配置DeepSeek API密钥")
        return
    
    analyzer = FinancialAnalyzer(DEEPSEEK_API_KEY)
    result = analyzer.analyze_markdown_file(markdown_file_path)
    
    if result:
        print(f"分析成功，结果保存在: {result}")
    else:
        print("分析失败")

if __name__ == "__main__":
    # 可以选择批量分析或单个文件分析
    import sys
    
    if len(sys.argv) > 1:
        # 分析指定的markdown文件
        markdown_file = sys.argv[1]
        analyze_single_markdown(markdown_file)
    else:
        # 批量分析results目录下的所有markdown文件
        batch_analyze_markdown_files()