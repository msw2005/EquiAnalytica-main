import akshare as ak
from typing import Dict, Any
from datetime import datetime


def get_last_quarter():
    now = datetime.now()
    year = now.year
    quarter = (now.month - 1) // 3
    
    if quarter == 0:
        year -= 1
        quarter = 4
    
    return f"{year}{quarter}"



def fetch_stock_individual_fund_flow(stock: str, market: str) -> Dict[str, Dict[str, str]] | Dict[str, Any]:
    """
    获取指定市场和股票的近 100 个交易日的资金流向数据。

    数据来源：东方财富网 - 数据中心 - 个股资金流向

    Args:
        stock (str): 股票代码，例如 "000425"。
        market (str): 交易市场，取值包括：
                      - "sh"：上海证券交易所
                      - "sz"：深证证券交易所
                      - "bj"：北京证券交易所

    Returns:
        Dict[str, Dict[str, str]]: 嵌套字典，最外层以“日期”字段为键，对应值是该交易日的资金流向各项数据。
                                  所有值均转换为字符串格式，示例结构如下：
        {
            "2025-05-30": {
                "收盘价": "12.34",
                "涨跌幅": "−0.56",                  # 单位：%
                "主力净流入-净额": "1.23E+07",
                "主力净流入-净占比": "5.12",        # 单位：%
                "超大单净流入-净额": "4.56E+06",
                "超大单净流入-净占比": "1.89",      # 单位：%
                "大单净流入-净额": "3.00E+06",
                "大单净流入-净占比": "1.24",        # 单位：%
                "中单净流入-净额": "2.00E+06",
                "中单净流入-净占比": "0.83",        # 单位：%
                "小单净流入-净额": "1.23E+06",
                "小单净流入-净占比": "0.51"         # 单位：%
            },
            "2025-05-29": {
                ...
            },
            ...
        }

    Example:
        >>> result = fetch_stock_individual_fund_flow(stock="000425", market="sh")
        >>> # result 是一个以日期为键的字典
        >>> data_20250530 = result.get("2025-05-30")
    """
    try:
        # 从 AkShare 获取 DataFrame
        df = ak.stock_individual_fund_flow(stock=stock, market=market)
        if df is None or df.empty:
            return {}

        # 将所有列转换为字符串类型，确保数值和百分比都按文本处理
        df = df.astype(str)

        # 构建嵌套字典：外层 key = 日期，内层为该行其他字段的字典
        nested: Dict[str, Dict[str, str]] = {}
        for record in df.to_dict(orient='records'):
            date_key = record.get("日期")
            # 去除 “日期” 字段，仅保留其他列
            inner: Dict[str, str] = {k: v for k, v in record.items() if k != "日期"}
            nested[date_key] = inner

        return nested

    except Exception as e:
        return {"status": "error", "message": str(e)}



import akshare as ak
from typing import Dict, Any


def fetch_stock_chip_distribution(symbol: str, adjust: str = "") -> Dict[str, Dict[str, str]] | Dict[str, Any]:
    """
    获取指定股票的近 90 个交易日筹码分布数据。

    数据来源：东方财富网 - 概念板 - 日K - 筹码分布

    Args:
        symbol (str): 股票代码，例如 "000001"。
        adjust (str): 复权类型，可选值：
                      - "qfq"：前复权
                      - "hfq"：后复权
                      - ""：不复权

    Returns:
        Dict[str, Dict[str, str]]: 嵌套字典，最外层以“日期”字段为键，对应值是该交易日的筹码分布各项数据。
                                  所有数值均转换为字符串格式，示例结构如下：
        {
            "2025-05-30": {
                "获利比例": "0.1234",
                "平均成本": "12.34",
                "90成本-低": "11.00",
                "90成本-高": "13.50",
                "90集中度": "0.5678",
                "70成本-低": "11.50",
                "70成本-高": "13.00",
                "70集中度": "0.4567"
            },
            "2025-05-29": {
                ...
            },
            ...
        }

    Example:
        >>> result = fetch_stock_chip_distribution(symbol="000001", adjust="qfq")
        >>> # result 是一个以日期为键的字典
        >>> data_20250530 = result.get("2025-05-30")
    """
    try:
        # 从 AkShare 获取 DataFrame
        df = ak.stock_cyq_em(symbol=symbol, adjust=adjust)
        if df is None or df.empty:
            return {}

        # 将所有列转换为字符串类型
        df = df.astype(str)

        # 构建嵌套字典：外层 key = 日期，内层为该行其他字段的字典
        nested: Dict[str, Dict[str, str]] = {}
        for record in df.to_dict(orient="records"):
            date_key = record.get("日期")
            inner: Dict[str, str] = {k: v for k, v in record.items() if k != "日期"}
            nested[date_key] = inner

        return nested

    except Exception as e:
        return {"status": "error", "message": str(e)}




import akshare as ak
from typing import Dict


def fetch_stock_institute_hold_detail(stock: str, quarter: str) -> Dict[str, Dict[str, str]] | Dict[str, Any]:
    """
    获取指定股票在某季度的机构持股详情。

    数据来源：新浪财经 - 机构持股 - 机构持股详情

    Args:
        stock (str): 股票代码，例如 "300003"。
        quarter (str): 报告期，格式为 "YYYYQ"，其中 Q ∈ {1,2,3,4}，例如：
                       - "20201": 2020 年一季报
                       - "20193": 2019 年三季报

    Returns:
        Dict[str, Dict[str, str]]: 嵌套字典，最外层以“持股机构代码”字段为键，对应值是该机构当期的持股详情各项数据。
                                  所有数值均转换为字符串格式，示例结构如下：
        {
            "00001234": {
                "持股机构类型": "公募基金",
                "持股机构简称": "华夏成长混合",
                "持股机构全称": "华夏基金管理有限公司-华夏成长混合型证券投资基金",
                "持股数": "1234.56",              # 单位：万股
                "最新持股数": "1250.00",          # 单位：万股
                "持股比例": "2.34",               # 单位：%
                "最新持股比例": "2.38",           # 单位：%
                "占流通股比例": "1.20",           # 单位：%
                "最新占流通股比例": "1.22",       # 单位：%
                "持股比例增幅": "0.04",           # 单位：%
                "占流通股比例增幅": "0.02"        # 单位：%
            },
            "00005678": {
                ...
            },
            ...
        }

    Example:
        >>> result = fetch_stock_institute_hold_detail(stock="300003", quarter="20201")
        >>> # result 是一个以持股机构代码为键的字典
        >>> data_for_institution = result.get("00001234")
    """
    try:
        # 从 AkShare 获取 DataFrame
        df = ak.stock_institute_hold_detail(stock=stock, quarter=quarter)
        if df is None or df.empty:
            return {}

        # 将所有列转换为字符串类型
        df = df.astype(str)

        # 构建嵌套字典：外层 key = 持股机构代码，内层为该行其他字段的字典
        nested: Dict[str, Dict[str, str]] = {}
        for record in df.to_dict(orient='records'):
            inst_code = record.get("持股机构代码")
            # 排除“持股机构代码”字段，保留其余项
            inner = {k: v for k, v in record.items() if k != "持股机构代码"}
            nested[inst_code] = inner

        return nested

    except Exception as e:
        return {"status": "error", "message": str(e)}



import akshare as ak
from typing import Dict


def fetch_stock_hsgt_individual_detail(symbol: str, start_date: str, end_date: str) -> Dict[str, Dict[str, str]] | Dict[str, Any]:
    """
    获取指定股票在沪深港通持股期间（最近 90 个交易日内）的个股持股详情数据。

    数据来源：东方财富网 - 数据中心 - 沪深港通 - 沪深港通持股 - 个股详情

    Args:
        symbol (str): 股票代码，例如 "002008"。
        start_date (str): 开始日期，格式 "YYYYMMDD"，只能查询最近 90 个交易日范围内的数据。
        end_date (str): 结束日期，格式 "YYYYMMDD"，只能查询最近 90 个交易日范围内的数据。

    Returns:
        Dict[str, Dict[str, str]]: 嵌套字典，最外层以“持股日期”字段为键，对应值是该日期的持股详情各项数据。
                                  所有数值均转换为字符串格式，示例结构如下：
        {
            "2021-09-01": {
                "当日收盘价": "12.34",                   # 单位：元
                "当日涨跌幅": "−0.56",                    # 单位：%
                "机构名称": "南方基金管理有限公司",       
                "持股数量": "1234567",                    # 单位：股
                "持股市值": "12345678.90",                # 单位：元
                "持股数量占A股百分比": "1.23",            # 单位：%
                "持股市值变化-1日": "12345.67",           # 单位：元
                "持股市值变化-5日": "23456.78",           # 单位：元
                "持股市值变化-10日": "34567.89"           # 单位：元
            },
            "2021-08-31": {
                ...
            },
            ...
        }

    Example:
        >>> result = fetch_stock_hsgt_individual_detail(symbol="002008", start_date="20210830", end_date="20211026")
        >>> # result 是一个以日期为键的字典
        >>> data_20210901 = result.get("2021-09-01")
    """
    try:
        # 从 AkShare 获取 DataFrame
        df = ak.stock_hsgt_individual_detail_em(symbol=symbol, start_date=start_date, end_date=end_date)
        if df is None or df.empty:
            return {}

        # 将所有列转换为字符串类型
        df = df.astype(str)

        # 构建嵌套字典：外层 key = 持股日期，内层为该行其他字段的字典
        nested: Dict[str, Dict[str, str]] = {}
        for record in df.to_dict(orient='records'):
            date_key = record.get("持股日期")
            inner = {k: v for k, v in record.items() if k != "持股日期"}
            nested[date_key] = inner

        return nested

    except Exception as e:
        return {"status": "error", "message": str(e)}


