import pandas as pd
import numpy as np
import json
from pathlib import Path
from datetime import datetime

# 分析得到的财务指标并输出markdown格式的报告
class FinancialComparisonAnalyzer:
    def __init__(self):
        # 指标权重配置
        self.weights = {
            '销售毛利率': 0.12,
            '销售净利率': 0.12, 
            '净资产收益率': 0.16,
            '营业总收入同比增长率': 0.15,
            '净利润同比增长率': 0.15,
            '资产负债率': 0.10,
            '流动比率': 0.06,
            '速动比率': 0.04,
            '存货周转天数': 0.05,
            '应收账款周转天数': 0.05
        }
    
    def load_target_company_data(self, json_file_path):
        """加载待分析公司的财务数据"""
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取关键指标
        target_metrics = {
            '销售毛利率': float(data['盈利能力指标']['销售毛利率']),
            '销售净利率': float(data['盈利能力指标']['销售净利率']),
            '净资产收益率': float(data['盈利能力指标']['净资产收益率']),
            '营业总收入同比增长率': float(data['成长性指标']['营业总收入同比增长率']),
            '净利润同比增长率': float(data['成长性指标']['净利润同比增长率']),
            '资产负债率': float(data['偿债能力指标']['资产负债率']),
            '流动比率': float(data['偿债能力指标']['流动比率']),
            '速动比率': float(data['偿债能力指标']['速动比率']),
            '存货周转天数': float(data['营运能力指标']['存货周转天数']),
            '应收账款周转天数': float(data['营运能力指标']['应收账款周转天数'])
        }
        
        return target_metrics
    
    def load_industry_data(self, csv_file_path):
        """加载同行业公司数据"""
        df = pd.read_csv(csv_file_path, encoding='utf-8')
        
        # 清理数据，移除包含异常值的行
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # 处理百分比字符串和其他数据类型问题
        percentage_cols = ['净利润同比增长率', '营业总收入同比增长率', '销售净利率', '销售毛利率', '净资产收益率', '资产负债率']
        for col in percentage_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('%', '').replace('False', np.nan)
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 处理数值列
        numeric_cols = ['流动比率', '速动比率', '存货周转天数', '应收账款周转天数']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 移除包含NaN的行
        required_cols = ['销售毛利率', '销售净利率', '净资产收益率', '营业总收入同比增长率', 
                        '净利润同比增长率', '资产负债率', '流动比率', '速动比率', 
                        '存货周转天数', '应收账款周转天数']
        
        df_clean = df.dropna(subset=required_cols)
        
        return df_clean
    
    def calculate_percentile_score(self, target_value, industry_values, metric_name):
        """计算单个指标的百分位排名得分"""
        # 移除异常值并确保数据类型一致
        industry_values = pd.to_numeric(industry_values, errors='coerce').dropna()
        target_value = float(target_value)
        
        if len(industry_values) == 0:
            return 60  # 默认中等分数
        
        # 对于负向指标（越小越好），需要反向计算
        reverse_metrics = ['资产负债率', '存货周转天数', '应收账款周转天数']
        
        if metric_name in reverse_metrics:
            # 对于负向指标，值越小排名越高
            percentile = (industry_values > target_value).sum() / len(industry_values) * 100
        else:
            # 对于正向指标，值越大排名越高
            percentile = (industry_values < target_value).sum() / len(industry_values) * 100
        
        # 根据百分位排名分配分数
        if percentile >= 90:
            return 100
        elif percentile >= 70:
            return 80
        elif percentile >= 40:
            return 60
        elif percentile >= 20:
            return 40
        else:
            return 20
    
    def generate_comparison_report(self, target_metrics, industry_df, company_name, industry_name, year):
        """生成对比分析报告"""
        # 计算各指标得分
        scores = {}
        weighted_scores = {}
        
        for metric, target_value in target_metrics.items():
            if metric in industry_df.columns:
                industry_values = industry_df[metric]
                score = self.calculate_percentile_score(target_value, industry_values, metric)
                scores[metric] = score
                weighted_scores[metric] = score * self.weights[metric]
        
        # 计算总分
        total_score = sum(weighted_scores.values())
        
        # 评级
        if total_score >= 90:
            rating = "优秀（行业标杆）"
        elif total_score >= 80:
            rating = "良好（优于多数同行）"
        elif total_score >= 70:
            rating = "中等（行业平均水平）"
        elif total_score >= 60:
            rating = "一般（存在短板）"
        else:
            rating = "较差（需警惕风险）"
        
        # 生成markdown报告内容
        timestamp = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        markdown_content = f"""# {company_name} 财务指标分析报告

**分析对象**: {company_name}
**对比行业**: {industry_name}
**分析年份**: {year}年
**生成时间**: {timestamp}

## 📊 分析摘要

- **综合评分**: {total_score:.1f}分
- **评级等级**: {rating}
- **对比样本**: {len(industry_df)}家同行业公司

## 🎯 财务指标详情

| 指标类别 | 指标名称 | 公司数值 | 行业排名得分 | 权重 | 加权得分 |
|---------|---------|----------|-------------|------|----------|
"""
        
        # 按类别组织指标
        categories = {
            '盈利能力': ['销售毛利率', '销售净利率', '净资产收益率'],
            '成长性': ['营业总收入同比增长率', '净利润同比增长率'],
            '偿债能力': ['资产负债率', '流动比率', '速动比率'],
            '营运能力': ['存货周转天数', '应收账款周转天数']
        }
        
        for category, metrics in categories.items():
            for metric in metrics:
                if metric in target_metrics:
                    target_value = target_metrics[metric]
                    score = scores.get(metric, 0)
                    weight = self.weights[metric] * 100
                    weighted_score = weighted_scores.get(metric, 0)
                    markdown_content += f"| {category} | {metric} | {target_value} | {score}分 | {weight}% | {weighted_score:.2f}分 |\n"
        
        # 计算各维度得分
        profitability_score = sum(weighted_scores.get(m, 0) for m in categories['盈利能力']) / 0.4
        growth_score = sum(weighted_scores.get(m, 0) for m in categories['成长性']) / 0.3
        solvency_score = sum(weighted_scores.get(m, 0) for m in categories['偿债能力']) / 0.2
        operation_score = sum(weighted_scores.get(m, 0) for m in categories['营运能力']) / 0.1
        
        markdown_content += f"""

## 🏆 各维度表现分析

### 盈利能力 (权重40%)
- **维度得分**: {profitability_score:.1f}分
- **表现评价**: {'优秀' if profitability_score >= 80 else '良好' if profitability_score >= 60 else '一般' if profitability_score >= 40 else '较差'}

### 成长性 (权重30%)
- **维度得分**: {growth_score:.1f}分
- **表现评价**: {'优秀' if growth_score >= 80 else '良好' if growth_score >= 60 else '一般' if growth_score >= 40 else '较差'}

### 偿债能力 (权重20%)
- **维度得分**: {solvency_score:.1f}分
- **表现评价**: {'优秀' if solvency_score >= 80 else '良好' if solvency_score >= 60 else '一般' if solvency_score >= 40 else '较差'}

### 营运能力 (权重10%)
- **维度得分**: {operation_score:.1f}分
- **表现评价**: {'优秀' if operation_score >= 80 else '良好' if operation_score >= 60 else '一般' if operation_score >= 40 else '较差'}

## 📋 评分标准说明

### 单指标评分规则
- **100分**: 行业前10%（优秀水平）
- **80分**: 行业前10%-30%（良好水平）
- **60分**: 行业前30%-60%（中等水平）
- **40分**: 行业前60%-80%（一般水平）
- **20分**: 行业后20%（较差水平）

### 综合评级标准
- **90-100分**: 优秀（行业标杆）
- **80-89分**: 良好（优于多数同行）
- **70-79分**: 中等（行业平均水平）
- **60-69分**: 一般（存在短板）
- **<60分**: 较差（需警惕风险）

## 💡 投资建议

基于当前评分结果：

1. **优势指标**: 继续保持和强化表现优秀的指标
2. **改进空间**: 重点关注得分较低的指标，制定针对性改进措施
3. **行业对比**: 定期与同行业公司进行对比分析，及时调整经营策略
4. **风险防控**: 特别关注偿债能力相关指标，确保财务安全

---
*本报告基于同行业{len(industry_df)}家公司的财务数据进行对比分析，仅供参考。*
"""
        
        return markdown_content

if __name__ == "__main__":
    # 简化的测试代码
    analyzer = FinancialComparisonAnalyzer()
    print("FinancialComparisonAnalyzer 初始化完成")