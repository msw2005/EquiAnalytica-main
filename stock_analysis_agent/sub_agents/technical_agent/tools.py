import pandas as pd
import numpy as np
import akshare as ak



def calculate_technical_indicators(provided_ticker: str) -> dict[str, dict] | dict[str, str]:
    """
    Fetch historical daily data for the specified stock from six months before today up to today,
    where "today" is determined in the China (Asia/Shanghai) timezone, then calculate the following:
      1. Volatility: 20-day rolling standard deviation of log returns, annualized
      2. RSI (Relative Strength Index): 14-day period
      3. MACD (Moving Average Convergence Divergence): using 12, 26, and 9-day settings
      4. Bollinger Bands: 20-day moving average ± 2 × standard deviation
      5. KDJ: 9-day RSV, with initial values for K and D set to 50 (starting once RSV is available)
      6. Volume Amplification: current volume divided by 20-day average volume
      7. Technical events:
         - Monthly High/Low: Closing price is highest/lowest in last 20 trading days
         - 6-Month High/Low: Closing price is highest/lowest in last 126 trading days
         - Yearly High/Low: Closing price is highest/lowest in last 252 trading days 
         - All-Time High/Low: Closing price is highest/lowest historically
         - Consecutive Up Days (%): Number of consecutive up days and cumulative percentage gain
         - Consecutive Down Days (%): Number of consecutive down days and cumulative percentage loss
         - Consecutive Volume Up Days: Number of consecutive days with increasing volume
         - Consecutive Volume Down Days: Number of consecutive days with decreasing volume
         - Breakout Above:
             * 5-day, 10-day, 20-day, 30-day, 60-day, 120-day, 250-day moving averages
             * Upper Bollinger Band
         - Breakdown Below:
             * 5-day, 10-day, 20-day, 30-day, 60-day, 120-day, 250-day moving averages 
             * Lower Bollinger Band
         - Price-Volume Up Days (%): Days with both price & volume up, cumulative gain %, turnover %
         - Price-Volume Down Days (%): Days with both price & volume down, cumulative loss %, turnover %

    Parameters:
      provided_ticker (str): Stock code, e.g., "600519"

    Returns (dict[str, dict]):
        A nested dictionary where:
        - Outer keys are dates in "YYYY-MM-DD" format
        - Inner values are dictionaries containing all indicators for that date
        Example:
        {
            "2022-01-03": {
                "open": 12.34,
                "close": 12.56,
                // ...other indicators...
            },
            "2022-01-04": {
                // ...next day's indicators...
            }
        }

    Details:
      - "today" is computed using the Asia/Shanghai timezone.
      - end_date is set to "today" in China timezone.
      - start_date is computed as six months before end_date.
      - Use ak.stock_zh_a_hist with adjust="qfq" to fetch daily data from start_date to end_date (inclusive).
      - Technical events are derived solely from columns in the fetched DataFrame.
      - If fetching fails, return status="error" with error_message.
      - On success, return status="success" and convert the DataFrame to a list of dicts.
    """
    try:
        # 计算今天的日期（使用中国时区 Asia/Shanghai）
        tz_sh = "Asia/Shanghai"
        today_sh = pd.Timestamp.now(tz=tz_sh).normalize()
        end_date = today_sh.strftime("%Y%m%d")
        # start_dt = today_sh - pd.DateOffset(years=1)
        # start_date = start_dt.strftime("%Y%m%d")
        start_date = "19910101"

        # 1. 拉取历史日线数据 (固定前复权)
        df = ak.stock_zh_a_hist(
            symbol=provided_ticker,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )

        if df is None or df.empty:
            return {
                "status": "error",
                "error_message": f"未能获取 {provided_ticker} 在 {start_date} 到 {end_date} 之间的历史数据。"
            }

        df = df.sort_values("日期").reset_index(drop=True)

        # 2. 计算对数收益
        df["log_return"] = np.log(df["收盘"] / df["收盘"].shift(1))

        # 3. 波动率：20 日滚动对数收益率标准差并年化
        window_vol = 20
        df["volatility"] = (df["log_return"].rolling(window=window_vol).std() * np.sqrt(252)).round(2)

        # 4. RSI：14 日
        window_rsi = 14
        delta = df["收盘"].diff(1)
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(window=window_rsi).mean()
        avg_loss = loss.rolling(window=window_rsi).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = (100 - (100 / (1 + rs))).shift(1).round(2)

        # 5. MACD：12 日 EMA - 26 日 EMA，信号线 9 日 EMA
        ema_short = df["收盘"].ewm(span=12, adjust=False).mean()
        ema_long = df["收盘"].ewm(span=26, adjust=False).mean()
        df["MACD_diff"] = (ema_short - ema_long)
        df["MACD_signal"] = df["MACD_diff"].ewm(span=9, adjust=False).mean()
        df["MACD_hist"] = (df["MACD_diff"] - df["MACD_signal"]).round(2)
        df["MACD_diff"] = df["MACD_diff"].round(2)
        df["MACD_signal"] = df["MACD_signal"].round(2)
        

        # 6. 布林带：20 日均线 ± 2*标准差
        window_bb = 20
        df["BB_mid"] = df["收盘"].rolling(window=window_bb).mean()
        df["BB_std"] = df["收盘"].rolling(window=window_bb).std()
        df["BB_upper"] = (df["BB_mid"] + 2 * df["BB_std"]).round(2)
        df["BB_lower"] = (df["BB_mid"] - 2 * df["BB_std"]).round(2)
        

        # 7. KDJ：9 日 RSV，初始化 K/D 当 RSV 首次可用
        low_min = df["最低"].rolling(window=9).min()
        high_max = df["最高"].rolling(window=9).max()
        df["RSV"] = (df["收盘"] - low_min) / (high_max - low_min) * 100
        df["K"] = np.nan
        df["D"] = np.nan
        first_valid_idx = df["RSV"].first_valid_index()
        if first_valid_idx is not None:
            df.loc[first_valid_idx, "K"] = 50.0
            df.loc[first_valid_idx, "D"] = 50.0
            for i in range(first_valid_idx + 1, len(df)):
                if not np.isnan(df.loc[i, "RSV"]):
                    prev_k = df.loc[i - 1, "K"]
                    prev_d = df.loc[i - 1, "D"]
                    df.loc[i, "K"] = 2/3 * prev_k + 1/3 * df.loc[i, "RSV"]
                    df.loc[i, "D"] = 2/3 * prev_d + 1/3 * df.loc[i, "K"]
                else:
                    df.loc[i, "K"] = df.loc[i - 1, "K"]
                    df.loc[i, "D"] = df.loc[i - 1, "D"]
            df["J"] = 3 * df["K"] - 2 * df["D"]
        else:
            df["J"] = np.nan
        df["K"] = df["K"].round(2)
        df["D"] = df["D"].round(2)
        df["J"] = df["J"].round(2)
        

        # 8. 成交量放大倍数：成交量 ÷ 20 日均量
        window_vol_amp = 20
        df["vol_ma20"] = df["成交量"].rolling(window=window_vol_amp).mean()
        df["volume_amplification"] = (df["成交量"] / df["vol_ma20"]).round(2)
        

        # 9. Technical Events with refined Chinese descriptions
        # Precompute moving averages for breakout checks
        df["MA5"] = df["收盘"].rolling(window=5).mean()
        df["MA10"] = df["收盘"].rolling(window=10).mean()
        df["MA20"] = df["收盘"].rolling(window=20).mean()
        df["MA30"] = df["收盘"].rolling(window=30).mean()
        df["MA60"] = df["收盘"].rolling(window=60).mean()
        df["MA120"] = df["收盘"].rolling(window=120).mean()
        df["MA250"] = df["收盘"].rolling(window=250).mean()
        

        # 9.1 新高 / 新低: month, half-year, year, all-time
        df["max20_close"] = df["收盘"].rolling(window=20).max()
        df["min20_close"] = df["收盘"].rolling(window=20).min()
        df["max126_close"] = df["收盘"].rolling(window=126).max()
        df["min126_close"] = df["收盘"].rolling(window=126).min()
        df["max252_close"] = df["收盘"].rolling(window=252).max()
        df["min252_close"] = df["收盘"].rolling(window=252).min()
        df["cum_max_close"] = df["收盘"].cummax()
        df["cum_min_close"] = df["收盘"].cummin()

        def high_low_flags(row):
            return pd.Series({
                "创月新高": (not np.isnan(row["max20_close"]) and row["收盘"] >= row["max20_close"]),
                "创月新低": (not np.isnan(row["min20_close"]) and row["收盘"] <= row["min20_close"]),
                "半年新高": (not np.isnan(row["max126_close"]) and row["收盘"] >= row["max126_close"]),
                "半年新低": (not np.isnan(row["min126_close"]) and row["收盘"] <= row["min126_close"]),
                "一年新高": (not np.isnan(row["max252_close"]) and row["收盘"] >= row["max252_close"]),
                "一年新低": (not np.isnan(row["min252_close"]) and row["收盘"] <= row["min252_close"]),
                "历史新高": (row["收盘"] >= row["cum_max_close"]),
                "历史新低": (row["收盘"] <= row["cum_min_close"]) 
            })

        hl_flags = df.apply(high_low_flags, axis=1)
        df = pd.concat([df, hl_flags], axis=1)
        

        # 9.2 连续上涨 / 连续下跌: count days and pct change
        df["连续上涨天数"] = 0
        df["连续上涨涨幅"] = "0.00%"
        df["连续下跌天数"] = 0
        df["连续下跌跌幅"] = "0.00%"

        up_streak = 0
        up_start_idx = None
        down_streak = 0
        down_start_idx = None
        for i in range(1, len(df)):
            # 上涨逻辑
            if df.loc[i, "收盘"] > df.loc[i-1, "收盘"]:
                if up_streak == 0:
                    up_streak = 1
                    up_start_idx = i-1
                else:
                    up_streak += 1
                df.loc[i, "连续上涨天数"] = up_streak
                if up_start_idx is not None and up_streak > 0:
                    df.loc[i, "连续上涨涨幅"] = f"{(df.loc[i, '收盘'] / df.loc[up_start_idx, '收盘'] * 100 - 100):.2f}%"
            else:
                up_streak = 0
                up_start_idx = None
                df.loc[i, "连续上涨天数"] = 0

            # 下跌逻辑
            if df.loc[i, "收盘"] < df.loc[i-1, "收盘"]:
                if down_streak == 0:
                    down_streak = 1
                    down_start_idx = i-1
                else:
                    down_streak += 1
                df.loc[i, "连续下跌天数"] = down_streak
                if down_start_idx is not None and down_streak > 0:
                    df.loc[i, "连续下跌跌幅"] = f"{(1 - df.loc[i, '收盘'] / df.loc[down_start_idx, '收盘']) * 100:.2f}%"
            else:
                down_streak = 0
                down_start_idx = None
                df.loc[i, "连续下跌天数"] = 0
        

        # 9.3 持续放量 / 持续缩量: count days
        df["持续放量天数"] = 0
        df["持续缩量天数"] = 0
        vol_up_streak = 0
        vol_down_streak = 0
        for i in range(1, len(df)):
            if df.loc[i, "成交量"] > df.loc[i-1, "成交量"]:
                vol_up_streak += 1
                df.loc[i, "持续放量天数"] = vol_up_streak
            else:
                vol_up_streak = 0
            if df.loc[i, "成交量"] < df.loc[i-1, "成交量"]:
                vol_down_streak += 1
                df.loc[i, "持续缩量天数"] = vol_down_streak
            else:
                vol_down_streak = 0
        

        # 9.4 量价齐升 / 量价齐跌: count consecutive days, pct change, cum turnover
        df["量价齐升天数"] = 0
        df["量价齐升期间涨幅"] = "0.00%"
        df["量价齐升期间换手率"] = "0.00%"
        df["量价齐跌天数"] = 0
        df["量价齐跌期间跌幅"] = "0.00%"
        df["量价齐跌期间换手率"] = "0.00%"

        price_vol_rise_streak = 0
        price_vol_fall_streak = 0
        for i in range(1, len(df)):
            if df.loc[i, "收盘"] > df.loc[i-1, "收盘"] and df.loc[i, "成交量"] > df.loc[i-1, "成交量"]:
                price_vol_rise_streak += 1
                df.loc[i, "量价齐升天数"] = price_vol_rise_streak
                start_idx = i - price_vol_rise_streak
                df.loc[i, "量价齐升期间涨幅"] = f"{(df.loc[i, '收盘'] / df.loc[start_idx, '收盘'] * 100 - 100):.2f}%"
                df.loc[i, "量价齐升期间换手率"] = f"{df.loc[start_idx:i, '换手率'].sum():.2f}%"
            else:
                price_vol_rise_streak = 0
            if df.loc[i, "收盘"] < df.loc[i-1, "收盘"] and df.loc[i, "成交量"] < df.loc[i-1, "成交量"]:
                price_vol_fall_streak += 1
                df.loc[i, "量价齐跌天数"] = price_vol_fall_streak
                start_idx_fall = i - price_vol_fall_streak
                df.loc[i, "量价齐跌期间跌幅"] = f"{(1 - df.loc[i, '收盘'] / df.loc[start_idx_fall, '收盘']) * 100:.2f}%"
                df.loc[i, "量价齐跌期间换手率"] = f"{df.loc[start_idx_fall:i, '换手率'].sum():.2f}%"
            else:
                price_vol_fall_streak = 0


        # 9.5 保留过去一月收盘价序列
        price_hist = df["收盘"].tail(20).tolist()


        # 9.6 向上突破 / 向下突破: 赋值对应均线名称列表与布林带标志
        df = df.tail(20)
        df.reset_index(drop=True, inplace=True)

        # 突破均线：前一日收盘低于均线且当日收盘大于等于均线
        def breakout_ma(row):
            result = []
            idx = row.name
            for ma in ["MA5", "MA10", "MA20", "MA30", "MA60", "MA120", "MA250"]:
                if idx == 0 or np.isnan(row[ma]) or np.isnan(df.loc[idx-1, ma]):
                    continue
                if df.loc[idx-1, "收盘"] < df.loc[idx-1, ma] and row["收盘"] >= row[ma]:
                    result.append(ma.replace("MA", "") + "日均线")
            return result
        df["突破均线"] = df.apply(breakout_ma, axis=1)

        # 跌破均线：前一日收盘高于均线且当日收盘小于等于均线
        def breakdown_ma(row):
            result = []
            idx = row.name
            for ma in ["MA5", "MA10", "MA20", "MA30", "MA60", "MA120", "MA250"]:
                if idx == 0 or np.isnan(row[ma]) or np.isnan(df.loc[idx-1, ma]):
                    continue
                if df.loc[idx-1, "收盘"] > df.loc[idx-1, ma] and row["收盘"] <= row[ma]:
                    result.append(ma.replace("MA", "") + "日均线")
            return result
        df["跌破均线"] = df.apply(breakdown_ma, axis=1)

        # 突破布林带上轨：前一日收盘低于上轨且当日收盘大于等于上轨
        def breakout_bb_upper(row):
            idx = row.name
            if idx == 0 or np.isnan(row["BB_upper"]) or np.isnan(df.loc[idx-1, "BB_upper"]):
                return False
            if df.loc[idx-1, "收盘"] < df.loc[idx-1, "BB_upper"] and row["收盘"] >= row["BB_upper"]:
                return True
            return False
        df["突破布林带上轨"] = df.apply(breakout_bb_upper, axis=1)

        # 跌破布林带下轨：前一日收盘高于下轨且当日收盘小于等于下轨
        def breakdown_bb_lower(row):
            idx = row.name
            if idx == 0 or np.isnan(row["BB_lower"]) or np.isnan(df.loc[idx-1, "BB_lower"]):
                return False
            if df.loc[idx-1, "收盘"] > df.loc[idx-1, "BB_lower"] and row["收盘"] <= row["BB_lower"]:
                return True
            return False
        df["跌破布林带下轨"] = df.apply(breakdown_bb_lower, axis=1)
        

        # 10 删除中间计算列
        # df = df.drop(columns=[
        #     "log_return", "RSV", "vol_ma20", "cum_max_close", "cum_min_close",
        #     "max20_close", "min20_close", "max126_close", "min126_close", "max252_close", "min252_close",
        #     "pct_change", "MA5", "MA10", "MA20", "MA30", "MA60", "MA120", "MA250",
        #     "BB_mid", "BB_std", "BB_upper", "BB_lower"
        # ], errors="ignore")

        df = df.drop(columns=[
            "log_return", "RSV", "vol_ma20", "cum_max_close", "cum_min_close",
            "max20_close", "min20_close", "max126_close", "min126_close", "max252_close", "min252_close",
            "pct_change"
        ], errors="ignore")
        
        df['日期'] = df['日期'].astype(str)

        # Transform dataframe into nested dict with dates as keys
        indicators_list = df.to_dict(orient="records")
        last_10_days = indicators_list[-10:-1]
        
        # Convert list of dicts to nested dict by date
        result = {}
        for day_data in last_10_days:
            date = day_data.pop('日期')  # Remove date from inner dict and use as key
            result[date] = day_data
        
        # Add price history to the last day's data
        last_date = list(result.keys())[-1]
        result[last_date]["price_hist_over_past_month"] = price_hist

        return result

    except Exception as e:
        return {
            "error": f"An exception occurred during calculation: {str(e)}"
        }