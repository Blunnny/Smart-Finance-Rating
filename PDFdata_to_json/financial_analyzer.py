import os
import json
import subprocess
from pathlib import Path
from openai import OpenAI
from datetime import datetime
import re

class FinancialAnalyzer:
    def __init__(self, deepseek_api_key):
        """
        初始化财务分析器
        :param deepseek_api_key: DeepSeek API密钥
        """
        self.client = OpenAI(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com"
        )
        self.current_dir = Path(__file__).parent
    
    def read_markdown_content(self, markdown_path):
        """
        读取markdown文件内容
        :param markdown_path: markdown文件路径
        :return: 文件内容字符串
        """
        try:
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"读取markdown文件失败: {e}")
            return None
    
    def analyze_financial_data(self, markdown_content):
        """
        使用DeepSeek API分析财务数据
        :param markdown_content: markdown格式的财务报表内容
        :return: 分析结果JSON字符串
        """
        try:
            # 构建分析提示词
            system_prompt = """
你是一个专业的财务分析师。请根据提供的财务报表markdown内容，计算并提取以下财务指标，并以JSON格式返回结果：

{
   "盈利能力指标": {
     "净利润": "数值（元）",
     "销售净利率": "数值（%）", 
     "销售毛利率": "数值（%）",
     "净资产收益率": "数值（%）"
   },
   "成长性指标": {
     "净利润同比增长率": "数值（%）",
     "营业总收入同比增长率": "数值（%）"
   },
   "偿债能力指标": {
     "流动比率": "数值",
     "速动比率": "数值",
     "资产负债率": "数值（%）"
   },
   "营运能力指标": {
     "存货周转天数": "数值（天）",
     "应收账款周转天数": "数值（天）"
   }
}

**重要计算说明：**
1. 销售净利率 = 净利润 ÷ 营业收入 × 100%
2. 销售毛利率 = (营业收入 - 营业成本) ÷ 营业收入 × 100%
3. 净资产收益率 = 净利润 ÷ 平均净资产 × 100%
4. 流动比率 = 流动资产 ÷ 流动负债
5. 速动比率 = (流动资产 - 存货) ÷ 流动负债
6. 资产负债率 = 总负债 ÷ 总资产 × 100%
7. **存货周转天数 = 365 ÷ (营业成本 ÷ 平均存货)**
   - 平均存货 = (期初存货 + 期末存货) ÷ 2
8. **应收账款周转天数 = 365 ÷ (营业收入 ÷ 平均应收账款)**
   - 平均应收账款 = (期初应收账款 + 期末应收账款) ÷ 2

**数据提取注意事项：**
- 仔细查找资产负债表中的"应收账款"和"存货"的期初、期末数据
- 仔细查找利润表中的"营业收入"和"营业成本"数据
- 忽略数字中的空格、逗号等格式化字符
- 如果数据存在但格式复杂，请尝试提取数值进行计算
- 只有在确实找不到必要数据时才填写"数据不足"

请仔细分析财务报表数据，优先从合并报表中提取数据。只返回JSON格式的结果，不要包含其他解释文字。
"""
            
            user_prompt = f"请分析以下财务报表数据，特别注意提取存货、应收账款、营业收入、营业成本等关键数据：\n\n{markdown_content}"
            
            print("正在调用DeepSeek API进行财务分析...")
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False,
                temperature=0.1  # 降低随机性，提高准确性
            )
            
            result = response.choices[0].message.content
            print("DeepSeek API调用成功")
            
            # 尝试解析JSON以验证格式
            try:
                json.loads(result)
                return result
            except json.JSONDecodeError:
                print("API返回的不是有效的JSON格式，尝试提取JSON部分")
                # 尝试从响应中提取JSON部分
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result, re.DOTALL)
                if json_match:
                    return json_match.group(0)
                else:
                    print("无法从响应中提取有效的JSON")
                    return None
                    
        except Exception as e:
            print(f"调用DeepSeek API时发生错误: {e}")
            return None
    
    def save_analysis_result(self, result_json, output_filename=None):
        """
        保存分析结果到JSON文件
        :param result_json: 分析结果JSON字符串
        :param output_filename: 输出文件名（可选）
        :return: 保存的文件路径
        """
        try:
            # 生成输出文件名
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"financial_analysis_{timestamp}.json"
            
            output_path = self.current_dir / output_filename
            
            # 格式化JSON并保存
            parsed_json = json.loads(result_json)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=2)
            
            print(f"分析结果已保存到: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"保存分析结果时发生错误: {e}")
            return None
    
    def analyze_markdown_file(self, markdown_file_path, output_filename=None):
        """
        分析markdown格式的财务报表文件
        :param markdown_file_path: markdown文件路径
        :param output_filename: 输出文件名（可选）
        :return: 分析结果文件路径或None
        """
        print(f"开始分析财务报表: {markdown_file_path}")
        
        # 读取markdown内容
        markdown_content = self.read_markdown_content(markdown_file_path)
        if not markdown_content:
            print("无法读取markdown文件内容")
            return None
        
        # 分析财务数据
        analysis_result = self.analyze_financial_data(markdown_content)
        if not analysis_result:
            print("财务数据分析失败")
            return None
        
        # 保存分析结果
        result_path = self.save_analysis_result(analysis_result, output_filename)
        if result_path:
            print(f"财务分析完成，结果已保存到: {result_path}")
            return result_path
        else:
            print("保存分析结果失败")
            return None

