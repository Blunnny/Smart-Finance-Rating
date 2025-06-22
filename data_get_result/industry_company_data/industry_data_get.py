import akshare as ak
import pandas as pd
import os
from datetime import datetime

# 获取指定申万三级行业成分股数据
industry_code = "850861.SI"

try:
    sw_index_third_cons_df = ak.sw_index_third_cons(symbol=industry_code)
    
    # 获取当前文件所在目录（industry_company_data）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成带时间戳的文件名：行业编号+时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    industry_code = "850861"
    filename = f"{industry_code}_{timestamp}.csv"
    full_path = os.path.join(current_dir, filename)
    
    # 保存数据到CSV文件
    sw_index_third_cons_df.to_csv(full_path, index=False, encoding='utf-8-sig')
    
        
except Exception as e:
    print(f"\n=== 获取数据失败 ===")
