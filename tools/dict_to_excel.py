import pandas as pd
from io import BytesIO


def dict_to_excel(data: dict) -> bytes:
    """
    将分析结果字典转换为 Excel 二进制流
    """
    # 准备数据
    rows = []

    # 提取核心字段
    company = data.get('company', '无')
    industry = data.get('industry', '无')
    score = data.get('score', '无')
    analysis = data.get('analysis', '无')
    recommendation = data.get('recommendation', '无')

    # 构造表格行
    rows.append([company, industry, score, analysis[:100] + '...' if len(analysis) > 100 else analysis, recommendation])

    # 创建 DataFrame
    df = pd.DataFrame(rows, columns=['公司名称', '所属行业', '评分', '分析结果', '合作建议'])

    # 写入 Excel 到内存
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='销售分析报告')

    # 获取二进制数据
    output.seek(0)
    return output.read()