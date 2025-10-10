# 使用示例

## 基本使用流程

### 示例1：首次完整下载

```bash
# 1. 设置配置
python scripts/setup.py

# 2. 下载所有历史数据
python scripts/download_all.py

# 3. 导入到MongoDB
python scripts/import_data.py

# 4. 查看数据
python scripts/display.py
```

### 示例2：日常增量更新

```bash
# 一键完成下载和导入
python scripts/update.py
```

### 示例3：查看不同维度的数据

```bash
# 查看最近7天的所有数据
python scripts/display.py --days 7

# 查看最近30天的活动
python scripts/display.py --activities --days 30

# 查看所有跑步活动
python scripts/display.py --activities --activity-type running

# 查看最近14天的睡眠情况
python scripts/display.py --sleep --days 14

# 查看体重变化
python scripts/display.py --weight
```

## Python代码示例

### 示例1：直接使用工具类

```python
from config import GarminConfigManager
from db import MongoDBClient
from utils import GarminDownloader, DataImporter

# 初始化配置
config = GarminConfigManager()

# 下载数据
downloader = GarminDownloader(config)
downloader.login()
downloader.download_all_data(latest=True)

# 导入数据
db_client = MongoDBClient(config)
importer = DataImporter(config, db_client)
importer.import_all_data()

# 查询数据
stats = db_client.get_stats()
print(stats)

db_client.close()
```

### 示例2：查询特定时间段的活动

```python
from datetime import datetime, timedelta
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 查询最近7天的活动
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

activities = db_client.query_activities_by_date_range(
    start_date.isoformat(),
    end_date.isoformat()
)

for activity in activities:
    print(f"{activity['activityName']}: {activity['distance']/1000:.2f}km")

db_client.close()
```

### 示例3：分析睡眠数据

```python
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 查询最近30天的睡眠数据
sleep_records = list(
    db_client.db.sleep.find().sort('calendarDate', -1).limit(30)
)

# 计算平均睡眠时间
total_sleep = sum(r.get('sleepTimeSeconds', 0) for r in sleep_records)
avg_sleep_hours = (total_sleep / len(sleep_records) / 3600) if sleep_records else 0

print(f"最近30天平均睡眠时间: {avg_sleep_hours:.2f} 小时")

# 计算平均深睡时间
total_deep = sum(r.get('deepSleepSeconds', 0) for r in sleep_records)
avg_deep_hours = (total_deep / len(sleep_records) / 3600) if sleep_records else 0

print(f"最近30天平均深睡时间: {avg_deep_hours:.2f} 小时")

db_client.close()
```

### 示例4：统计运动数据

```python
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 统计各类运动的次数和总距离
pipeline = [
    {
        '$group': {
            '_id': '$activityType',
            'count': {'$sum': 1},
            'total_distance': {'$sum': '$distance'},
            'total_calories': {'$sum': '$calories'}
        }
    },
    {'$sort': {'count': -1}}
]

results = list(db_client.db.activities.aggregate(pipeline))

print("运动统计:")
for result in results:
    activity_type = result['_id']
    count = result['count']
    distance = result['total_distance'] / 1000  # 转换为公里
    calories = result['total_calories']
    
    print(f"{activity_type}:")
    print(f"  次数: {count}")
    print(f"  总距离: {distance:.2f} km")
    print(f"  总卡路里: {calories}")

db_client.close()
```

### 示例5：每日数据趋势分析

```python
from datetime import date, timedelta
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 查询最近30天的每日汇总
end_date = date.today().isoformat()
start_date = (date.today() - timedelta(days=30)).isoformat()

summaries = db_client.query_daily_summaries(start_date, end_date)

# 分析步数趋势
steps_list = [s.get('totalSteps', 0) for s in summaries if s.get('totalSteps')]
if steps_list:
    avg_steps = sum(steps_list) / len(steps_list)
    max_steps = max(steps_list)
    min_steps = min(steps_list)
    
    print("最近30天步数统计:")
    print(f"  平均步数: {avg_steps:.0f}")
    print(f"  最高步数: {max_steps}")
    print(f"  最低步数: {min_steps}")

db_client.close()
```

## MongoDB查询示例

直接使用MongoDB shell或工具查询：

```javascript
// 连接到数据库
use garmin_health

// 查询最近10个活动
db.activities.find().sort({startTimeGMT: -1}).limit(10)

// 查询所有跑步活动
db.activities.find({activityType: "running"})

// 统计总活动数
db.activities.count()

// 查询特定日期的每日汇总
db.daily_summary.findOne({calendarDate: "2024-01-01"})

// 查询步数超过10000的日期
db.daily_summary.find({totalSteps: {$gt: 10000}})

// 查询睡眠时间少于7小时的记录
db.sleep.find({sleepTimeSeconds: {$lt: 25200}})

// 统计平均静息心率
db.resting_heart_rate.aggregate([
    {$group: {
        _id: null,
        avgRHR: {$avg: "$restingHeartRate"}
    }}
])
```

## 数据导出示例

### 导出为JSON

```python
import json
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 导出所有活动
activities = list(db_client.db.activities.find())

# 转换ObjectId为字符串
for activity in activities:
    activity['_id'] = str(activity['_id'])

# 保存为JSON
with open('activities_export.json', 'w', encoding='utf-8') as f:
    json.dump(activities, f, ensure_ascii=False, indent=2, default=str)

print(f"已导出 {len(activities)} 个活动")

db_client.close()
```

### 导出为CSV

```python
import csv
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 查询活动
activities = list(db_client.db.activities.find())

# 导出为CSV
with open('activities_export.csv', 'w', encoding='utf-8', newline='') as f:
    if activities:
        # 定义要导出的字段
        fields = ['activityId', 'activityName', 'activityType', 'startTimeGMT', 
                  'duration', 'distance', 'calories', 'averageHR']
        
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for activity in activities:
            row = {field: activity.get(field, '') for field in fields}
            writer.writerow(row)

print(f"已导出 {len(activities)} 个活动到CSV")

db_client.close()
```

## 高级用例

### 创建自定义数据分析脚本

```python
#!/usr/bin/env python3
"""
自定义分析脚本示例：分析运动强度和恢复
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import GarminConfigManager
from db import MongoDBClient

def analyze_training_load():
    """分析训练负荷"""
    config = GarminConfigManager()
    db_client = MongoDBClient(config)
    
    # 查询最近7天的活动
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    activities = db_client.query_activities_by_date_range(
        start_date.isoformat(),
        end_date.isoformat()
    )
    
    # 统计训练负荷
    total_duration = sum(a.get('duration', 0) for a in activities)
    total_distance = sum(a.get('distance', 0) for a in activities)
    total_calories = sum(a.get('calories', 0) for a in activities)
    
    print("最近7天训练统计:")
    print(f"  活动次数: {len(activities)}")
    print(f"  总时长: {total_duration / 60:.1f} 分钟")
    print(f"  总距离: {total_distance / 1000:.2f} 公里")
    print(f"  总卡路里: {total_calories}")
    
    # 查询静息心率趋势（恢复指标）
    rhr_records = list(
        db_client.db.resting_heart_rate.find().sort('calendarDate', -1).limit(7)
    )
    
    if rhr_records:
        avg_rhr = sum(r.get('restingHeartRate', 0) for r in rhr_records) / len(rhr_records)
        print(f"\n平均静息心率: {avg_rhr:.1f} bpm")
    
    db_client.close()

if __name__ == '__main__':
    analyze_training_load()
```

## 数据可视化示例

使用matplotlib进行简单的数据可视化：

```python
import matplotlib.pyplot as plt
from datetime import date, timedelta
from config import GarminConfigManager
from db import MongoDBClient

config = GarminConfigManager()
db_client = MongoDBClient(config)

# 查询最近30天的每日汇总
end_date = date.today().isoformat()
start_date = (date.today() - timedelta(days=30)).isoformat()

summaries = db_client.query_daily_summaries(start_date, end_date)

# 提取数据
dates = [s['calendarDate'] for s in summaries]
steps = [s.get('totalSteps', 0) for s in summaries]

# 绘图
plt.figure(figsize=(12, 6))
plt.plot(dates, steps, marker='o')
plt.xticks(rotation=45)
plt.xlabel('日期')
plt.ylabel('步数')
plt.title('最近30天步数趋势')
plt.grid(True)
plt.tight_layout()
plt.savefig('steps_trend.png')
plt.show()

db_client.close()
```

这些示例展示了工具的各种使用方式，您可以根据自己的需求进行修改和扩展！

