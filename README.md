# 黄晨昱-25348078-第三次人工智能编程作业
## 1. 任务拆解与 AI 协作策略
具体策略如下：
#首先，我将整个任务划分为6个模块：数据预处理、时间分布分析、线路站点分析、高峰小时系数计算、文件批量导出以及服务绩效热力图分析，然后按顺序逐步完成：
#第一步，让AI帮助完成数据读取与预处理（包括时间解析、字段构造和异常值处理）
#第二步，针对时间分布问题，明确要求使用numpy进行条件统计，并使用matplotlib绘图
#第三步，让AI生成符合指定analyze_route_stops函数，并进行结果验证
#第四步，PHF计算较为复杂，我将其拆分为“高峰识别→分钟级计算→带入公式”三步逐步完成
#第五步，文件导出任务找路径与去重，通过多次调试保证文件生成正常
#第六步，最后完成排名统计与热力图画图，并对结果进行总结分析
## 2. 核心 Prompt 迭代记录
#（1）任务3画图代码：
before：
sns.barplot(
    data=top15,
    x='mean_stops',
    y='线路号',
    xerr=top15['std_stops'],
)
after1：
sns.barplot(
    data=top15,
    x='mean_stops',
    y='线路号',
    palette='Blues_d',
    errorbar='sd',
    capsize=0.3
)
after2:
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
    capsize=3
)
#（2）最开始AI预处理中没有进行异常处理，因此添加
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

print("\n=== 各列缺失值数量 ===")#6.检查缺失值
print(df.isnull().sum())
df = df.dropna()#7.删除缺失值
print("\n缺失值处理完成(已删除包含缺失值的行)")

生成的问题：最开始AI生成的代码无法运行，后使用了 seaborn 的默认误差棒（errorbar='sd'），但是发现不是要求中的任务要求因此改成了使用我自己计算的 std_stops
## 3. Debug 记录
在任务3中，使用 sns.barplot 时出现如下错误：
ValueError: 'xerr' shape must match 'x'
原因分析：在 seaborn 新版本中，barplot不再直接支持传入xerr参数，导致误差棒数据维度与柱状图不匹配。
解决过程：
首先确认问题出在xerr参数，后发现seaborn已改变接口，最终采用“seaborn+matplotlib添加误差棒”的方式解决
## 4. 人工代码审查（逐行中文注释）
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
print(f"PHF5  = {peak_count} / (12*{max_5min}) = {PHF5:.4f}")#计算PHF5

print(f"\n最大15分钟刷卡量（{max_15min_time.strftime('%H:%M')}~{end_15min.strftime('%H:%M')}）：{max_15min} 次")
print(f"PHF15 ={peak_count}/( 4*{max_15min})={PHF15:.4f}")#计算PHF15
