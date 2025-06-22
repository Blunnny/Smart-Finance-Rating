import pandas as pd
import os
from datetime import datetime
import time

# 添加akshare导入
try:
    import akshare as ak
except ImportError:
    print("错误: 请先安装akshare库: pip install akshare")
    raise

# 合并申万一级、二级和三级行业分类
class IndustryFinancialAnalyzer:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.industry_mapping_file = os.path.join(
            self.current_dir, 
            'industry_data_base', 
            'merged_sw_industry_info_20250621_145757.csv'
        )
        
    def load_industry_mapping(self):
        """加载行业映射数据"""
        try:
            return pd.read_csv(self.industry_mapping_file, encoding='utf-8-sig')
        except Exception as e:
            print(f"加载行业映射文件失败: {e}")
            return None
    
    def find_third_level_industries(self, industry_name):
        """根据行业名称查找对应的三级行业代码"""
        mapping_df = self.load_industry_mapping()
        if mapping_df is None:
            return []
        
        third_level_codes = []
        
        # 检查是否为一级行业
        first_level_match = mapping_df[mapping_df['一级行业名称'] == industry_name]
        if not first_level_match.empty:
            # 获取该一级行业下所有有三级行业代码的记录
            third_level_codes = first_level_match[first_level_match['三级行业代码'] != '']['三级行业代码'].unique().tolist()
            print(f"找到一级行业 '{industry_name}' 下的 {len(third_level_codes)} 个三级行业")
            return third_level_codes
        
        # 检查是否为二级行业
        second_level_match = mapping_df[mapping_df['二级行业名称'] == industry_name]
        if not second_level_match.empty:
            third_level_codes = second_level_match[second_level_match['三级行业代码'] != '']['三级行业代码'].unique().tolist()
            print(f"找到二级行业 '{industry_name}' 下的 {len(third_level_codes)} 个三级行业")
            return third_level_codes
        
        # 检查是否为三级行业
        third_level_match = mapping_df[mapping_df['三级行业名称'] == industry_name]
        if not third_level_match.empty:
            third_level_codes = third_level_match['三级行业代码'].unique().tolist()
            print(f"找到三级行业 '{industry_name}' 的行业代码")
            return third_level_codes
        
        print(f"未找到行业名称 '{industry_name}' 对应的数据")
        return []
    
    def get_industry_constituents(self, industry_code):
        """获取指定三级行业的成分股数据"""
        try:
            constituents_df = ak.sw_index_third_cons(symbol=industry_code)
            return constituents_df
        except Exception as e:
            print(f"获取行业 {industry_code} 成分股数据失败: {e}")
            return pd.DataFrame()
    
    def extract_stock_codes(self, constituents_df):
        """从成分股数据中提取6位股票代码"""
        if constituents_df.empty:
            return []
        
        # 假设股票代码在第二列（索引1），格式如 "002741.SZ"
        stock_codes = []
        for code in constituents_df.iloc[:, 1]:  # 第二列是股票代码
            # 提取6位数字代码
            if isinstance(code, str) and '.' in code:
                six_digit_code = code.split('.')[0]
                stock_codes.append(six_digit_code)
        
        return stock_codes
    
    def get_stock_financial_data(self, stock_code, year, period="按年度"):
        """获取单个股票的财务数据"""
        try:
            financial_df = ak.stock_financial_abstract_ths(symbol=stock_code, indicator=period)
            
            # 筛选指定年份的数据
            if '报告期' in financial_df.columns:
                financial_df['报告期_str'] = financial_df['报告期'].astype(str)
                year_str = str(year)
                filtered_df = financial_df[financial_df['报告期_str'].str.contains(year_str, na=False)]
                
                if not filtered_df.empty:
                    filtered_df = filtered_df.drop('报告期_str', axis=1)
                    # 添加股票代码列
                    filtered_df['股票代码'] = stock_code
                    return filtered_df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"获取股票 {stock_code} 财务数据失败: {e}")
            return pd.DataFrame()
    
    def analyze_industry_financials(self, industry_name, year):
        """主函数：分析指定行业的财务数据"""
        print(f"\n=== 开始分析行业 '{industry_name}' 的 {year} 年财务数据 ===")
        
        # 1. 查找三级行业代码
        third_level_codes = self.find_third_level_industries(industry_name)
        if not third_level_codes:
            print("未找到对应的行业数据")
            return None
        
        # 2. 获取所有成分股
        all_stock_codes = []
        for code in third_level_codes:
            constituents_df = self.get_industry_constituents(code)
            stock_codes = self.extract_stock_codes(constituents_df)
            all_stock_codes.extend(stock_codes)
            time.sleep(1)  # 避免请求过于频繁
        
        # 去重
        all_stock_codes = list(set(all_stock_codes))
        print(f"\n总共找到 {len(all_stock_codes)} 只成分股")
        
        # 3. 批量获取财务数据
        all_financial_data = []
        success_count = 0
        
        for i, stock_code in enumerate(all_stock_codes, 1):
            print(f"\n进度: {i}/{len(all_stock_codes)}")
            financial_df = self.get_stock_financial_data(stock_code, year)
            
            if not financial_df.empty:
                all_financial_data.append(financial_df)
                success_count += 1
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        print(f"\n成功获取 {success_count} 只股票的财务数据")
        
        # 4. 合并所有财务数据
        if all_financial_data:
            combined_df = pd.concat(all_financial_data, ignore_index=True)
            
            # 5. 保存到CSV文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"industry_financial_analysis_{industry_name}_{year}_{timestamp}.csv"
            filepath = os.path.join(self.current_dir, filename)
            
            combined_df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"\n=== 分析完成 ===")
            print(f"总共包含 {len(combined_df)} 条财务记录")
            
            return filepath
        else:
            print("\n未获取到任何财务数据")
            return None