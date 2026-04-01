import re


def reg_search(text, regex_list):
    """
    实现自定义正则匹配函数

    Args:
        text: 需要正则匹配的文本内容
        regex_list: 正则表达式列表，每个元素是一个字典，键为目标字段名，值为对应的正则模式

    Returns:
        匹配到的结果列表
    """
    results = []

    for regex_dict in regex_list:
        result_dict = {}

        for field_name, pattern in regex_dict.items():
            if pattern == '*自定义*':
                # 根据具体需求自定义正则表达式
                if field_name == '标的证券':
                    # 匹配股票代码，如 600900.SH
                    match = re.search(r'(\d{6}\.[A-Z]{2})', text)
                    if match:
                        result_dict[field_name] = match.group(1)
                    else:
                        result_dict[field_name] = None
                elif field_name == '换股期限':
                    # 匹配日期范围，如 2023 年 6 月 2 日至 2027 年 6 月 1 日
                    # 先找所有日期格式
                    date_pattern = r'(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)'
                    matches = re.findall(date_pattern, text)

                    if len(matches) >= 2:
                        # 提取前两个日期并转换格式
                        dates = []
                        for date_str in matches[:2]:
                            # 提取年月日
                            year_match = re.search(r'(\d{4})\s*年', date_str)
                            month_match = re.search(r'(\d{1,2})\s*月', date_str)
                            day_match = re.search(r'(\d{1,2})\s*日', date_str)

                            if year_match and month_match and day_match:
                                year = year_match.group(1)
                                month = month_match.group(1).zfill(2)  # 补零
                                day = day_match.group(1).zfill(2)  # 补零
                                dates.append(f"{year}-{month}-{day}")

                        result_dict[field_name] = dates
                    else:
                        # 尝试另一种匹配方式，直接匹配"至"字前后的时间
                        range_pattern = r'(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)\s*至\s*(\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日)'
                        range_match = re.search(range_pattern, text)

                        if range_match:
                            dates = []
                            for i in range(1, 3):
                                date_part = range_match.group(i)
                                year_match = re.search(r'(\d{4})\s*年', date_part)
                                month_match = re.search(r'(\d{1,2})\s*月', date_part)
                                day_match = re.search(r'(\d{1,2})\s*日', date_part)

                                if year_match and month_match and day_match:
                                    year = year_match.group(1)
                                    month = month_match.group(1).zfill(2)
                                    day = day_match.group(1).zfill(2)
                                    dates.append(f"{year}-{month}-{day}")

                            result_dict[field_name] = dates
                        else:
                            result_dict[field_name] = []
                else:
                    # 默认处理方式
                    result_dict[field_name] = None
            else:
                # 使用提供的正则表达式进行匹配
                matches = re.findall(pattern, text)
                if matches:
                    result_dict[field_name] = matches[0] if len(matches) == 1 else matches
                else:
                    result_dict[field_name] = None

        results.append(result_dict)

    return results


# 测试用例
text = '''
标的证券：本期发行的证券为可交换为发行人所持中国长江电力股份
有限公司股票（股票代码：600900.SH，股票简称：长江电力）的可交换公司债
券。
换股期限：本期可交换公司债券换股期限自可交换公司债券发行结束
之日满 12 个月后的第一个交易日起至可交换债券到期日止，即 2023 年 6 月 2
日至 2027 年 6 月 1 日止。
'''

regex_list = [{
    '标的证券': '*自定义*',
    '换股期限': '*自定义*'
}]

result = reg_search(text, regex_list)
print(result)