import pandas as pd
import os
from datetime import datetime

# 合并得到的申万一级、二级和三级行业数据，只保留行业代码、行业名称和公司个数
try:
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 读取三个CSV文件
    first_df = pd.read_csv(os.path.join(current_dir, 'sw_index_first_info_20250621_120041.csv'))
    second_df = pd.read_csv(os.path.join(current_dir, 'sw_index_second_info_20250621_120041.csv'))
    third_df = pd.read_csv(os.path.join(current_dir, 'sw_index_third_info_20250621_120041.csv'))
    
    # 获取列名（假设第一列是行业代码，第二列是行业名称，第三列是成份个数或上级行业）
    first_columns = first_df.columns.tolist()
    second_columns = second_df.columns.tolist()
    third_columns = third_df.columns.tolist()
    
    # 提取需要的列并重命名
    # 一级行业：行业代码、行业名称、成份个数
    first_selected = first_df.iloc[:, [0, 1, 2]].copy()
    first_selected.columns = ['一级行业代码', '一级行业名称', '一级成份个数']
    first_selected['级别'] = '一级'
    
    # 二级行业：行业代码、行业名称、上级行业、成份个数
    second_selected = second_df.iloc[:, [0, 1, 2, 3]].copy()
    second_selected.columns = ['二级行业代码', '二级行业名称', '上级行业名称', '二级成份个数']
    second_selected['级别'] = '二级'
    
    # 三级行业：行业代码、行业名称、上级行业、成份个数
    third_selected = third_df.iloc[:, [0, 1, 2, 3]].copy()
    third_selected.columns = ['三级行业代码', '三级行业名称', '上级行业名称', '三级成份个数']
    third_selected['级别'] = '三级'
    
    # 第一步：将二级行业与一级行业合并
    # 通过二级行业的"上级行业名称"与一级行业的"一级行业名称"进行匹配
    second_with_first = pd.merge(
        second_selected, 
        first_selected[['一级行业代码', '一级行业名称', '一级成份个数']], 
        left_on='上级行业名称', 
        right_on='一级行业名称', 
        how='left'
    )
    
    # 第二步：将三级行业与二级行业合并
    # 通过三级行业的"上级行业名称"与二级行业的"二级行业名称"进行匹配
    third_with_second = pd.merge(
        third_selected, 
        second_with_first[['二级行业代码', '二级行业名称', '二级成份个数', '一级行业代码', '一级行业名称', '一级成份个数']], 
        left_on='上级行业名称', 
        right_on='二级行业名称', 
        how='left'
    )
    
    # 整理最终的合并结果
    merged_result = third_with_second[[
        '一级行业代码', '一级行业名称', '一级成份个数',
        '二级行业代码', '二级行业名称', '二级成份个数', 
        '三级行业代码', '三级行业名称', '三级成份个数'
    ]].copy()
    
    # 添加只有一级和二级的数据（没有对应三级的二级行业）
    second_only = second_with_first[~second_with_first['二级行业名称'].isin(third_selected['上级行业名称'])].copy()
    second_only_result = second_only[[
        '一级行业代码', '一级行业名称', '一级成份个数',
        '二级行业代码', '二级行业名称', '二级成份个数'
    ]].copy()
    second_only_result['三级行业代码'] = ''
    second_only_result['三级行业名称'] = ''
    second_only_result['三级成份个数'] = ''
    
    # 添加只有一级的数据（没有对应二级的一级行业）
    first_only = first_selected[~first_selected['一级行业名称'].isin(second_selected['上级行业名称'])].copy()
    first_only_result = first_only[['一级行业代码', '一级行业名称', '一级成份个数']].copy()
    first_only_result['二级行业代码'] = ''
    first_only_result['二级行业名称'] = ''
    first_only_result['二级成份个数'] = ''
    first_only_result['三级行业代码'] = ''
    first_only_result['三级行业名称'] = ''
    first_only_result['三级成份个数'] = ''
    
    # 合并所有结果
    final_result = pd.concat([merged_result, second_only_result, first_only_result], ignore_index=True)
    
    # 按一级、二级、三级行业代码排序
    final_result = final_result.sort_values(['一级行业代码', '二级行业代码', '三级行业代码']).reset_index(drop=True)

    # 生成输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"merged_sw_industry_info_{timestamp}.csv"
    output_filepath = os.path.join(current_dir, output_filename)
    
    # 保存合并结果
    final_result.to_csv(output_filepath, index=False, encoding='utf-8-sig')
    
    # 显示前几行数据预览
    print("\n=== 数据预览 ===")
    print(final_result.head(10))
    
    # 显示列信息
    print("\n=== 最终列名 ===")
    for i, col in enumerate(final_result.columns, 1):
        print(f"{i:2d}. {col}")
        
except Exception as e:
    print(f"\n=== 合并失败 ===")
    print(f"错误信息: {str(e)}")
    print("\n可能的原因:")
    print("1. CSV文件不存在或路径错误")
    print("2. 文件格式问题")
    print("3. 列名不匹配")
    print("4. 权限问题（无法写入文件）")