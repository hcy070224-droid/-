#任务一：数据预处理
#1.导入库
import numpy as np #数值计算库
import pandas as pd #数据处理核心库
import matplotlib.pyplot as plt #用于画图
import seaborn as sns#补充画图工具
import os# 用来创建文件夹
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

#任务2(b)：24小时分布图
# 解决中文显示问题
plt.rcParams['font.sans-serif']=['SimHei']  #黑体
plt.rcParams['axes.unicode_minus']=False    #解决负号显示为方块的问题
plt.rcParams['font.family']='sans-serif'

#1.统计每个小时的刷卡量
hour_counts = df_up.groupby('hour').size()
#2.补全0~23小时
hour_counts = hour_counts.reindex(range(24), fill_value=0)

colors = []#3.设置颜色（重点：区分时间段）
for h in range(24):
    if h < 7:
        colors.append('blue') #早峰前
    elif h >= 22:
        colors.append('red') #深夜
    else:
        colors.append('gray') #普通时间

plt.figure(figsize=(10, 5))#4.画图
plt.bar(range(24), hour_counts.values, color=colors)
plt.title("24小时刷卡量分布")#5.设置标题和标签
plt.xlabel("小时")
plt.ylabel("刷卡量（次）")
#6.设置x轴刻度（每2小时一个）
plt.xticks(range(0, 24, 2))
#7.添加网格线
plt.grid(axis='y', linestyle='--', alpha=0.7)
#8.添加图例
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='blue', label='早峰前(<7点)'),
    Patch(facecolor='red', label='深夜(>=22点)'),
    Patch(facecolor='gray', label='其他时段')
]
plt.legend(handles=legend_elements)
#9.保存图片
plt.savefig("hour_distribution.png", dpi=150)
#10.显示图像
plt.show()

# 任务3线路站点

#1.定义函数
def analyze_route_stops(df, route_col='线路号', stops_col='ride_stops'):
    """
    计算各线路乘客的平均搭乘站点数及其标准差。
    Parameters
    ----------
    df : pd.DataFrame  预处理后的数据集
    route_col : str    线路号列名
    stops_col : str    搭乘站点数列名
    Returns
    -------
    pd.DataFrame  包含列:线路号、mean_stops、std_stops,按 mean_stops 降序排列
    """
    grouped = df.groupby(route_col)[stops_col]  #按线路号分组，并取出搭乘站点数
    #单独每条线路统计“坐了多少站”
    #计算每条线路的平均搭乘站点数
    mean_stops = grouped.mean()
    #计算每条线路的标准差
    std_stops = grouped.std()

    #将结果整理成一个新的DataFrame
    result = pd.DataFrame({
        route_col: mean_stops.index,   #线路号作为引索
        'mean_stops': mean_stops.values,  #平均值
        'std_stops': std_stops.values     #标准差
    })
    #按平均搭乘站点数从大到小排序#坐得最远的线路排在最前面
    result = result.sort_values(by='mean_stops', ascending=False)
    #返回结果
    return result

#2.调用函数
route_stats = analyze_route_stops(df)
#输出前10条结果
print("=== 各线路平均搭乘站点数(前10)===")
print(route_stats.head(10))

#3.可视化处理
#取平均值最高的前15条线路
top15 = route_stats.head(15)
top15['线路号'] = top15['线路号'].astype(str)
plt.figure(figsize=(10, 6)) #设置图像大小

#使用seaborn画水平条形图
sns.barplot(
    data=top15,
    x='mean_stops',
    y='线路号',
    palette='Blues_d'
)
plt.errorbar(#手动添加误差棒
    x=top15['mean_stops'],
    y=range(len(top15)),
    xerr=top15['std_stops'],
    fmt='none',
    ecolor='black',
    capsize=0.3,
    elinewidth=1
)
#添加标题和坐标轴标签
plt.title("各线路平均搭乘站点数（Top15）")
plt.xlabel("平均搭乘站点数")
plt.ylabel("线路号")
#设置x轴从0开始
plt.xlim(0, None)
plt.savefig("route_stops.png", dpi=150)#保存图片
plt.show()#显示图像


#任务4（高峰小时系数PHF）
#PHF5：
#12×最大5分钟人数/高峰小时总人数
#PHF15：
#4×最大15分钟人数/高峰小时总人数

#只保留“上车刷卡”
df_up = df[df['刷卡类型'] == 0]
#按小时统计刷卡量
hour_counts = df_up.groupby('hour').size()
#找到刷卡量最大的小时（高峰小时）
peak_hour = hour_counts.idxmax()#哪个小时最多
peak_count = hour_counts.max()#这个小时的人数
print(f"高峰小时：{peak_hour:02d}:00 ~ {peak_hour+1:02d}:00，刷卡量：{peak_count} 次")
#取出“高峰小时”的数据
df_peak = df_up[df_up['hour'] == peak_hour]
#设置时间索引
df_peak = df_peak.set_index('交易时间')

#5分钟粒度统计#每5分钟统计一次刷卡量
count_5min=df_peak.resample('5T').size()
#找最大5分钟刷卡量
max_5min = count_5min.max()
#找这个最大值对应的时间段
max_5min_time = count_5min.idxmax()
#计算PHF5
PHF5 = peak_count / (12 * max_5min)

#15分钟粒度统计
count_15min = df_peak.resample('15T').size()
#找最大15分钟刷卡量
max_15min = count_15min.max()
#找这个最大值对应的时间段
max_15min_time = count_15min.idxmax()
#计算PHF15
PHF15 = peak_count / (4 * max_15min)

#输出结果
#计算时间段结束时间
end_5min = max_5min_time + pd.Timedelta(minutes=5)
end_15min = max_15min_time + pd.Timedelta(minutes=15)

print(f"\n最大5分钟刷卡量（{max_5min_time.strftime('%H:%M')}~{end_5min.strftime('%H:%M')}）：{max_5min} 次")
print(f"PHF5  = {peak_count} / (12*{max_5min}) = {PHF5:.4f}")

print(f"\n最大15分钟刷卡量（{max_15min_time.strftime('%H:%M')}~{end_15min.strftime('%H:%M')}）：{max_15min} 次")
print(f"PHF15 ={peak_count}/( 4*{max_15min})={PHF15:.4f}")


#任务5导出线路驾驶员信息
#筛选线路1101-1120
df_filtered = df[(df['线路号'] >= 1101) & (df['线路号'] <= 1120)]#只保留题目要求的20条线路
#创建文件夹
folder_name = "线路驾驶员信息"
os.makedirs(folder_name, exist_ok=True)
#获取所有线路号
routes = df_filtered['线路号'].unique()
for route in routes:#循环每条线路
    #取出当前线路的数据
    df_route=df_filtered[df_filtered['线路号']==route]
    #提取“车辆编号-驾驶员编号”并去重
    pairs=df_route[['车辆编号','驾驶员编号']].drop_duplicates()
    #写入文件
    file_path = os.path.join(folder_name, f"{route}.txt")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"线路号: {route}\n")
        f.write("车辆编号\t驾驶员编号\n")
        for _, row in pairs.iterrows():
            f.write(f"{row['车辆编号']}\t{row['驾驶员编号']}\n")
    #打印路径
    print(f"已生成文件:{file_path}")


#任务6司机排名 + 热力图
top_driver=df['驾驶员编号'].value_counts().head(10)#司机前10
top_route = df['线路号'].value_counts().head(10)#线路前10
top_station = df['上车站点'].value_counts().head(10)#上车站点前10
top_vehicle = df['车辆编号'].value_counts().head(10)#车辆前10
#打印结果
print("=== Top10 司机 ===")
print(top_driver)
print("\n=== Top10 线路 ===")
print(top_route)
print("\n=== Top10 上车站点 ===")
print(top_station)
print("\n=== Top10 车辆 ===")
print(top_vehicle)

#构造热力图数据（4×10）
# 把四个前10拼成一个DataFrame
heatmap_data = pd.DataFrame([
    top_driver.values.tolist(),
    top_route.values.tolist(),
    top_station.values.tolist(),
    top_vehicle.values.tolist()
])
heatmap_data.index = ['司机','线路','上车站点','车辆']#设置行标签
heatmap_data.columns = [f"Top{i}" for i in range(1, 11)]#设置列标签
#画图
plt.figure(figsize=(12, 6))
sns.heatmap(
    heatmap_data,
    annot=True,#每个格子显示数值
    fmt='d',#整数格式
    cmap='YlOrRd'#颜色
)
#标题
plt.title("公交服务绩效Top10热力图\n（颜色越深表示服务人次越多）")
plt.xticks(rotation=0)#x轴标签不旋转
plt.savefig("performance_heatmap.png", dpi=150, bbox_inches='tight')#保存图片
plt.show()#显示
#输出结论
print("\n=== 分析结论 ===")
print("从热力图可以看出，不同维度的服务人次存在明显差异。其中部分线路和司机的服务人次显著高于其他对象，说明客流分布不均衡，可能集中在少数热门线路和高频运行车辆上。同时，上车站点的分布也表现出类似规律，部分站点客流量远高于平均水平，反映出城市出行需求的集中性。这些信息可为公交调度优化和资源配置提供重要参考。")