#任务一：数据预处理
#1.导入库
import numpy as np #数值计算库
import pandas as pd #数据处理核心库
import matplotlib.pyplot as plt #用于画图

#2.读取数据
df = pd.read_csv("ICData.csv", sep=",") # sep="," 表示数据是用“”分隔
print("=== 数据前5行 ===")#查看前5行，确认数据是否读取正确
print(df.head())
#查看数据基本信息（行数、列数、每列类型）
print("\n=== 数据基本信息 ===")
print(df.info())

#3.时间解析（核心步骤）

df['交易时间'] = pd.to_datetime(df['交易时间']) # 将“交易时间”从字符串转换为 datetime 类型
#从时间中提取“小时”（0~23）新建一列hour
df['hour'] = df['交易时间'].dt.hour
#时间输出
print("\n=== 时间解析后 ===")
print(df[['交易时间', 'hour']].head())

#4.构造衍生字段：搭乘站点数
#ride_stops=|下车站点-车站点|
df['ride_stops'] = (df['下车站点'] - df['上车站点']).abs()

#站点数输出
print("\n=== 搭乘站点数示例 ===")
print(df[['上车站点', '下车站点', 'ride_stops']].head())

#异常处理
#5.删除异常数据（ride_stops =0）
#记录删除前的数据量
before_rows = len(df)
#删除ride_stops等于0的记录
df = df[df['ride_stops'] != 0]
#删除后数据量
after_rows = len(df)
#删除行
print("\n删除异常数据(ride_stops=0):", before_rows - after_rows, "条")

# 6.检查缺失值
print("\n=== 各列缺失值数量 ===")
print(df.isnull().sum())
# 7.删除缺失值
df = df.dropna()
print("\n缺失值处理完成(已删除包含缺失值的行)")




#任务2
#统计两个时间段人数
#24小时柱状图
#(a)使用numpy统计
df_up=df[df['刷卡类型'] == 0]#统计“上车刷卡”（刷卡类型=0）
hours=df_up['hour'].values#转成numpy数组
morning_count =np.sum(hours<7)#统计早上7点前（hour<7）

#统计晚上22点后（hour>=22）
night_count = np.sum(hours>=22)
#计算全天总刷卡量
total_count = len(hours)
#计算百分比
morning_percent = morning_count / total_count * 100
night_percent = night_count / total_count * 100

#输出结果
print("=== 时间段统计结果 ===")
print(f"早7点前刷卡量:{morning_count} 次，占比：{morning_percent:.2f}%")
print(f"晚22点后刷卡量:{night_count} 次，占比：{night_percent:.2f}%")
