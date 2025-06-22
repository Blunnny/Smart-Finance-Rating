# 智财评分系统 (Smart Finance Score)

> **AI 驱动的智能财务分析与评分系统**  
> _基于人工智能和 AKShare 的财务指标自动分析工具_

## 📋 项目简介

这是一个基于人工智能和 AKSHARE 开源项目的智能财务分析系统，能够自动从 PDF 财务报表中提取财务数据，并与同行业公司进行对比，从盈利能力、成长性、偿债能力和营运能力方面进行评价打分，生成财务分析报告。

### 🎥 演示视频

[![演示视频](https://img.shields.io/badge/演示视频-点击观看-blue?style=for-the-badge&logo=video)](演示视频.mp4)

> 💡 **提示**: 点击上方按钮观看完整演示视频，了解项目的详细使用流程和功能展示。

## 🎯 核心功能

### 1. PDF 文档智能解析

- 使用 **MinerU** 技术自动提取 PDF 财务报表内容
- 支持表格、文字、公式等多种格式的识别
- 将 PDF 转换为结构化的 Markdown 格式

### 2. 财务数据智能分析

- 基于 **DeepSeek AI** 进行财务指标自动计算
- 提取关键财务指标：
  - **盈利能力**：净利润、销售净利率、销售毛利率、净资产收益率
  - **成长性**：净利润同比增长率、营业总收入同比增长率
  - **偿债能力**：流动比率、速动比率、资产负债率
  - **营运能力**：存货周转天数、应收账款周转天数

### 3. 行业数据获取

- 基于 **AKShare** 获取实时行业数据
- 支持申万一级、二级、三级行业分类
- 自动获取同行业公司财务数据进行对比

### 4. 智能评分与报告生成

- 多维度财务指标评分系统
- 行业排名百分位分析
- 自动生成专业的 Markdown 格式分析报告

## 🏗️ 项目架构

```
finance-analysis/
├── main_analyzer.py                    # 主分析器，整合所有功能
├── PDFdata_to_json/                    # PDF数据处理模块
│   ├── financial_analyzer.py          # 财务数据分析器
│   ├── config.py                      # 配置文件
│   └── batch_analyzer.py              # 批量分析器
├── data_get_result/                    # 数据获取模块
│   ├── industry_financial_analyzer.py # 行业财务分析器
│   ├── company_data/                  # 公司数据
│   ├── industry_company_data/         # 行业公司数据
│   └── industry_data_base/            # 行业基础数据
├── analysis_and_scoring/               # 分析与评分模块
│   └── financial_comparison_analyzer.py # 财务对比分析器
├── MinerU/                            # MinerU文档解析工具
├── PDF/                               # PDF文件目录
├── results/                           # 结果输出目录
└── myenv/                             # Python虚拟环境
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- CUDA 支持的 GPU（推荐）
- 至少 8GB 内存

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd finance-analysis
```

2. **激活虚拟环境**

```bash
# Windows
myenv\Scripts\activate.bat

# Linux/macOS
source myenv/bin/activate
```

3. **配置 API 密钥**
   编辑 `PDFdata_to_json/config.py` 文件：

```python
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"  # 替换为实际的DeepSeek API密钥
```

4. **运行分析**

```bash
python main_analyzer.py <PDF文件路径> <行业名称> <年份> [公司名称]
PDF路径若为文件夹，则其中所有的PDF都将被单独分析识别，推荐将PDF文件夹作为PDF文件路径
```

### 使用示例

```bash
# 分析农产品加工行业的2020年财务数据
python main_analyzer.py PDF/test_short.pdf 农产品加工 2020 测试公司
```

## 📊 分析流程

### 步骤 1: PDF 内容提取

- 使用 MinerU 工具解析 PDF 文档
- 提取表格、文字、公式等结构化数据
- 转换为 Markdown 格式便于后续处理

### 步骤 2: 财务数据分析

- 调用 DeepSeek AI API 进行智能分析
- 自动计算关键财务指标
- 生成标准化的 JSON 格式数据

### 步骤 3: 行业数据获取

- 通过 AKShare 获取同行业公司数据
- 支持申万行业分类体系
- 获取对比样本的财务指标

### 步骤 4: 对比分析与报告生成

- 计算各指标在行业中的排名
- 基于权重进行综合评分
- 生成专业的分析报告

## 📈 评分体系

### 指标权重分配

- **盈利能力** (40%): 销售毛利率(12%)、销售净利率(12%)、净资产收益率(16%)
- **成长性** (30%): 营业总收入同比增长率(15%)、净利润同比增长率(15%)
- **偿债能力** (20%): 资产负债率(10%)、流动比率(6%)、速动比率(4%)
- **营运能力** (10%): 存货周转天数(5%)、应收账款周转天数(5%)

### 评分标准

- **100 分**: 行业前 10%（优秀水平）
- **80 分**: 行业前 10%-30%（良好水平）
- **60 分**: 行业前 30%-60%（中等水平）
- **40 分**: 行业前 60%-80%（一般水平）
- **20 分**: 行业后 20%（较差水平）

### 综合评级

- **90-100 分**: 优秀（行业标杆）
- **80-89 分**: 良好（优于多数同行）
- **70-79 分**: 中等（行业平均水平）
- **60-69 分**: 一般（存在短板）
- **<60 分**: 较差（需警惕风险）

## 🔧 配置说明

### MinerU 配置

项目集成了 MinerU 文档解析工具，支持以下参数：

```bash
mineru -p <input_path> -o <output_path> [options]

参数说明：
-p, --path PATH         输入文件路径或目录（必填）
-o, --output PATH       输出目录（必填）
-m, --method [auto|txt|ocr] 解析方法：auto（默认）、txt、ocr
-b, --backend [pipeline|vlm-transformers|vlm-sglang-engine|vlm-sglang-client] 解析后端
-l, --lang [ch|ch_server|...] 指定文档语言
-d, --device TEXT       推理设备（cpu/cuda/cuda:0/npu/mps）
-f, --formula BOOLEAN   是否启用公式解析（默认开启）
-t, --table BOOLEAN     是否启用表格解析（默认开启）
```

### API 配置

- **DeepSeek API**: 用于财务数据智能分析
- **AKShare**: 用于获取行业和公司财务数据

## 📁 输出文件

### 分析报告

生成的报告包含：

- 公司基本信息
- 财务指标详情表格
- 各维度表现分析
- 行业排名和评分
- 投资建议

### 文件命名规则

```
财务分析报告_{公司名称}_{行业名称}_{年份}_{时间戳}.md
```

## 🛠️ 开发说明

### 模块扩展

- **PDFdata_to_json**: 可扩展支持更多文档格式
- **data_get_result**: 可集成更多数据源
- **analysis_and_scoring**: 可自定义评分算法

### 自定义配置

- 修改 `config.py` 中的财务指标模板
- 调整 `financial_comparison_analyzer.py` 中的权重配置
- 自定义报告模板和格式

## 📝 注意事项

1. **API 密钥安全**: 请妥善保管 DeepSeek API 密钥，不要提交到版本控制系统
2. **数据准确性**: 系统分析结果仅供参考，重要决策请结合专业判断
3. **网络连接**: 需要稳定的网络连接以获取实时行业数据
4. **资源消耗**: GPU 加速需要足够的显存，建议使用 8GB 以上显存的显卡

## 📄 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**免责声明**: 本工具生成的分析结果仅供参考，不构成投资建议。投资有风险，决策需谨慎。
