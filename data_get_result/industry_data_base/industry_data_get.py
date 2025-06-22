import akshare as ak
import pandas as pd
import os
from datetime import datetime

# 获取申万一级、二级和三级行业分类数据
print("=== 开始获取申万行业分类数据 ===")

try:
    # 获取一级行业分类
    print("\n正在获取申万一级行业信息...")
    first_classification = ak.sw_index_first_info()
    print(f"一级行业数据形状: {first_classification.shape}")
    
    # 获取二级行业分类
    print("\n正在获取申万二级行业信息...")
    second_classification = ak.sw_index_second_info()
    print(f"二级行业数据形状: {second_classification.shape}")
    
    # 获取三级行业分类
    print("\n正在获取申万三级行业信息...")
    third_classification = ak.sw_index_third_info()
    print(f"三级行业数据形状: {third_classification.shape}")
    
    print("\n=== 所有数据获取成功 ===")
    
    # 获取当前文件所在目录（industry_data_base）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"\n保存目录: {current_dir}")
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存一级行业分类
    first_filename = f"sw_index_first_info_{timestamp}.csv"
    first_filepath = os.path.join(current_dir, first_filename)
    first_classification.to_csv(first_filepath, index=False, encoding='utf-8-sig')
    print(f"\n一级行业数据已保存到: {first_filepath}")
    print(f"文件大小: {os.path.getsize(first_filepath)} 字节")
    print(f"数据行数: {len(first_classification)}")
    
    # 保存二级行业分类
    second_filename = f"sw_index_second_info_{timestamp}.csv"
    second_filepath = os.path.join(current_dir, second_filename)
    second_classification.to_csv(second_filepath, index=False, encoding='utf-8-sig')
    print(f"\n二级行业数据已保存到: {second_filepath}")
    print(f"文件大小: {os.path.getsize(second_filepath)} 字节")
    print(f"数据行数: {len(second_classification)}")
    
    # 保存三级行业分类
    third_filename = f"sw_index_third_info_{timestamp}.csv"
    third_filepath = os.path.join(current_dir, third_filename)
    third_classification.to_csv(third_filepath, index=False, encoding='utf-8-sig')
    print(f"\n三级行业数据已保存到: {third_filepath}")
    print(f"文件大小: {os.path.getsize(third_filepath)} 字节")
    print(f"数据行数: {len(third_classification)}")
    
    print("\n=== 所有数据保存完成 ===")
    print(f"总共保存了 3 个文件，时间戳: {timestamp}")
    
    
except Exception as e:
    print(f"\n=== 获取数据失败 ===")
    print(f"错误信息: {str(e)}")
    print("\n可能的原因:")
    print("1. 网络连接问题")
    print("2. akshare库版本问题")
    print("3. 数据源暂时不可用")
    print("4. 权限问题（无法创建文件夹或写入文件）")