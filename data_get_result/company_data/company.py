import akshare as ak
import pandas as pd
import os
from datetime import datetime

# 参数设置
stock_code = "002538" # 目标股票代码
period = "按年度" # "按报告期", "按年度", "按单季度" 之一
year = 2024

try:
    # 获取股票财务摘要数据
    stock_financial_abstract_ths_df = ak.stock_financial_abstract_ths(symbol=stock_code, indicator=period)
    
    # 检查报告期列的格式
    if '报告期' in stock_financial_abstract_ths_df.columns:
        # 尝试转换为字符串然后筛选包含指定年份的数据
        stock_financial_abstract_ths_df['报告期_str'] = stock_financial_abstract_ths_df['报告期'].astype(str)
        
        # 筛选包含指定年份的数据（更宽松的条件）
        year_str = str(year)
        filtered_df = stock_financial_abstract_ths_df[stock_financial_abstract_ths_df['报告期_str'].str.contains(year_str, na=False)]
        
        if len(filtered_df) > 0:
            # 删除临时列
            filtered_df = filtered_df.drop('报告期_str', axis=1)
            stock_financial_abstract_ths_df = filtered_df
        else:
            unique_periods = stock_financial_abstract_ths_df['报告期'].unique()[:10]
            for period_val in unique_periods:
                print(f"  - {period_val}")
    else:
        for col in stock_financial_abstract_ths_df.columns:
            print(f"  - {col}")
    
    # 获取当前文件所在目录（company_data）
    current_dir = os.path.dirname(os.path.abspath(__file__))

    
    # 生成带时间戳和年份的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stock_financial_abstract_{stock_code}_{year}_{timestamp}.csv"
    filepath = os.path.join(current_dir, filename)
    
    # 保存数据到CSV文件
    stock_financial_abstract_ths_df.to_csv(filepath, index=False, encoding='utf-8-sig')
    
        
except Exception as e:
    print(f"\n=== 获取数据失败 ===")
