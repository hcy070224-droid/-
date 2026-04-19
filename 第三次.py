#任务一：数据预处理
#1. 导入库
import numpy as np #数值计算库
import pandas as pd #数据处理核心库
import matplotlib.pyplot as plt #用于画图

# 2. 读取数据
df = pd.read_csv("ICData.csv", sep=",") # sep="," 表示数据是用“”分隔
print("=== 数据前5行 ===")# 查看前5行，确认数据是否读取正确
print(df.head())
# 查看数据基本信息（行数、列数、每列类型）
print("\n=== 数据基本信息 ===")
print(df.info())

# 3. 时间解析（核心步骤）

df['交易时间'] = pd.to_datetime(df['交易时间']) # 将“交易时间”从字符串转换为 datetime 类型
# 从时间中提取“小时”（0~23），新建一列 hour
df['hour'] = df['交易时间'].dt.hour
#时间输出
print("\n=== 时间解析后 ===")
print(df[['交易时间', 'hour']].head())

# 4. 构造衍生字段：搭乘站点数
# ride_stops = |下车站点 - 上车站点|
df['ride_stops'] = (df['下车站点'] - df['上车站点']).abs()

#站点数输出
print("\n=== 搭乘站点数示例 ===")
print(df[['上车站点', '下车站点', 'ride_stops']].head())



