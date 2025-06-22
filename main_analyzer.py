# 在文件开头添加akshare导入
import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile
import akshare as ak


# 导入各模块
sys.path.append('PDFdata_to_json')
sys.path.append('data_get_result')
sys.path.append('analysis_and_scoring')

from PDFdata_to_json.financial_analyzer import FinancialAnalyzer
from PDFdata_to_json.config import DEEPSEEK_API_KEY
from data_get_result.industry_financial_analyzer import IndustryFinancialAnalyzer
from analysis_and_scoring.financial_comparison_analyzer import FinancialComparisonAnalyzer

class IntegratedFinancialAnalyzer:
    def __init__(self):
        self.temp_dir = None
        self.cleanup_files = []
        
    def setup_temp_directory(self):
        """创建临时工作目录"""
        self.temp_dir = tempfile.mkdtemp(prefix='finance_analysis_')
        print(f"创建临时工作目录: {self.temp_dir}")
        
    def cleanup_temp_files(self):
        """清理所有临时文件和目录"""
        try:
            # 清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                print(f"已清理临时目录: {self.temp_dir}")
            
            # 清理其他中间文件
            for file_path in self.cleanup_files:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    print(f"已清理文件: {file_path}")
                    
        except Exception as e:
            print(f"清理文件时出错: {e}")
    
    def extract_pdf_content(self, pdf_path):
        """使用MinerU提取PDF内容"""
        print("步骤1: 提取PDF内容...")
        
        # 创建输出目录
        output_dir = os.path.join(self.temp_dir, "pdf_output")
        os.makedirs(output_dir, exist_ok=True)
        
        # 激活虚拟环境并运行mineru
        if os.name == 'nt':  # Windows
            activate_cmd = r"myenv\Scripts\activate.bat"
            cmd = f"{activate_cmd} && mineru -p \"{pdf_path}\" -o \"{output_dir}\" -d cuda"
        else:  # Linux/macOS
            activate_cmd = "source myenv/bin/activate"
            cmd = f"{activate_cmd} && mineru -p '{pdf_path}' -o '{output_dir}' -d cuda"
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                raise Exception(f"MinerU执行失败: {result.stderr}")
            
            # 查找生成的markdown文件
            markdown_files = list(Path(output_dir).rglob("*.md"))
            if not markdown_files:
                raise Exception("未找到生成的markdown文件")
            
            markdown_path = str(markdown_files[0])
            self.cleanup_files.append(output_dir)
            print(f"PDF内容提取完成: {markdown_path}")
            return markdown_path
            
        except Exception as e:
            print(f"PDF提取失败: {e}")
            return None
    
    def analyze_financial_data(self, markdown_path):
        """分析财务数据"""
        print("步骤2: 分析财务数据...")
        
        if DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            raise Exception("请先在config.py中配置DeepSeek API密钥")
        
        analyzer = FinancialAnalyzer(DEEPSEEK_API_KEY)
        
        # 读取markdown内容
        content = analyzer.read_markdown_content(markdown_path)
        if not content:
            raise Exception("读取markdown文件失败")
        
        # 分析财务数据
        analysis_result = analyzer.analyze_financial_data(content)
        if not analysis_result:
            raise Exception("财务数据分析失败")
        
        # 保存分析结果到临时文件
        json_path = os.path.join(self.temp_dir, "financial_analysis.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(analysis_result)
        
        self.cleanup_files.append(json_path)
        print("财务数据分析完成")
        return json_path
    
    def get_industry_data(self, industry_name, year):
        """获取行业数据"""
        print(f"步骤3: 获取{industry_name}行业{year}年数据...")
        
        industry_analyzer = IndustryFinancialAnalyzer()
        
        # 分析行业财务数据
        csv_path = industry_analyzer.analyze_industry_financials(industry_name, year)
        if not csv_path or not os.path.exists(csv_path):
            raise Exception(f"获取{industry_name}行业数据失败")
        
        self.cleanup_files.append(csv_path)
        print(f"行业数据获取完成: {csv_path}")
        return csv_path
    
    def generate_comparison_report(self, company_json_path, industry_csv_path, company_name, industry_name, year):
        """生成对比分析报告"""
        print("步骤4: 生成对比分析报告...")
        
        comparison_analyzer = FinancialComparisonAnalyzer()
        
        # 加载公司数据
        company_data = comparison_analyzer.load_target_company_data(company_json_path)
        
        # 加载行业数据
        industry_data = comparison_analyzer.load_industry_data(industry_csv_path)
        
        # 生成报告
        report_content = comparison_analyzer.generate_comparison_report(
            company_data, industry_data, company_name, industry_name, year
        )
        
        # 保存最终报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"财务分析报告_{company_name}_{industry_name}_{year}_{timestamp}.md"
        report_path = os.path.join(os.getcwd(), report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"分析报告生成完成: {report_path}")
        return report_path
    
    def run_complete_analysis(self, pdf_path, industry_name, year, company_name=None):
        """运行完整的分析流程"""
        try:
            print("=== 开始财务分析流程 ===")
            print(f"PDF文件: {pdf_path}")
            print(f"对比行业: {industry_name}")
            print(f"分析年份: {year}")
            
            # 设置临时目录
            self.setup_temp_directory()
            
            # 如果没有提供公司名称，从PDF文件名提取
            if not company_name:
                company_name = Path(pdf_path).stem
            
            # 步骤1: 提取PDF内容
            markdown_path = self.extract_pdf_content(pdf_path)
            if not markdown_path:
                raise Exception("PDF内容提取失败")
            
            # 步骤2: 分析财务数据
            json_path = self.analyze_financial_data(markdown_path)
            
            # 步骤3: 获取行业数据
            csv_path = self.get_industry_data(industry_name, year)
            
            # 步骤4: 生成对比报告
            report_path = self.generate_comparison_report(
                json_path, csv_path, company_name, industry_name, year
            )
            
            print("=== 分析流程完成 ===")
            print(f"最终报告: {report_path}")
            
            return report_path
            
        except Exception as e:
            print(f"分析过程中出错: {e}")
            return None
        
        finally:
            # 清理所有临时文件
            print("\n=== 清理临时文件 ===")
            self.cleanup_temp_files()
            print("清理完成")

def main():
    """主函数 - 命令行接口"""
    if len(sys.argv) < 4:
        print("使用方法: python main_analyzer.py <PDF文件路径> <行业名称> <年份> [公司名称]")
        print("示例: python main_analyzer.py PDF/test_short.pdf 农产品加工 2020 测试公司")
        return
    
    pdf_path = sys.argv[1]
    industry_name = sys.argv[2]
    year = int(sys.argv[3])
    company_name = sys.argv[4] if len(sys.argv) > 4 else None
    
    # 检查PDF文件是否存在
    if not os.path.exists(pdf_path):
        print(f"错误: PDF文件不存在 - {pdf_path}")
        return
    
    # 运行分析
    analyzer = IntegratedFinancialAnalyzer()
    result = analyzer.run_complete_analysis(pdf_path, industry_name, year, company_name)
    
    if result:
        print(f"\n✅ 分析成功完成!")
        print(f"📄 报告文件: {result}")
    else:
        print("\n❌ 分析失败")

if __name__ == "__main__":
    main()