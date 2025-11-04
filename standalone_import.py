#!/usr/bin/env python3
"""
独立导入脚本 - 不依赖其他模块
直接读取JSON文件并插入MongoDB
"""

import os
import json
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from tqdm import tqdm

print("=" * 60)
print("独立导入脚本")
print("=" * 60)

# 1. 连接MongoDB
print("\n1. 连接MongoDB...")
client = MongoClient('mongodb://localhost:27999/')
db = client['garmin_health']
print("  ✓ 连接成功")

# 2. 清空旧数据
print("\n2. 清空旧数据...")
result = db.activities.delete_many({})
print(f"  已删除 {result.deleted_count} 条")

# 3. 创建索引
print("\n3. 创建索引...")
db.activities.create_index([('activityId', ASCENDING)], unique=True)
db.activities.create_index([('startTimeGMT', DESCENDING)])
db.activities.create_index([('activityType', ASCENDING)])
print("  ✓ 索引创建完成")

# 4. 读取并导入活动文件
print("\n4. 导入活动数据...")
activities_dir = '/home/wangyuanchun/myCoach/data/garmin/mydata/activities'

# 获取所有JSON文件
json_files = []
for file in os.listdir(activities_dir):
    if file.endswith('.json'):
        json_files.append(os.path.join(activities_dir, file))

print(f"  找到 {len(json_files)} 个JSON文件")

# 按activityId去重（优先详情文件）
activity_files = {}
for filepath in json_files:
    filename = os.path.basename(filepath)
    if '_summary.json' in filename:
        activity_id = filename.replace('_summary.json', '')
        if activity_id not in activity_files:
            activity_files[activity_id] = filepath
    elif '_details.json' in filename:
        activity_id = filename.replace('_details.json', '')
        activity_files[activity_id] = filepath  # 详情文件覆盖摘要

print(f"  去重后 {len(activity_files)} 个活动")

# 导入每个活动
count = 0
debug_first = True
for activity_id, filepath in tqdm(activity_files.items(), desc="导入活动"):
    try:
        # 读取JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 调试第一个文件
        if debug_first and str(activity_id) == '360757114':
            print(f"\n调试文件: {filepath}")
            print(f"  JSON中的activityId: {data.get('activityId')}")
            print(f"  JSON中的startTimeGMT: {data.get('startTimeGMT')}")
            print(f"  JSON中的distance: {data.get('distance')}")
            print(f"  JSON类型: {type(data)}")
            print(f"  JSON键数量: {len(data)}")
            debug_first = False
        
        # 判断是summary还是details文件
        is_details = 'summaryDTO' in data
        
        if is_details:
            # details文件：数据在summaryDTO中
            summary = data.get('summaryDTO', {})
            activity_type_obj = data.get('activityTypeDTO', {})
        else:
            # summary文件：数据在根级别
            summary = data
            activity_type_obj = data.get('activityType', {})
        
        # 提取activityType
        if isinstance(activity_type_obj, dict):
            activity_type = activity_type_obj.get('typeKey')
        else:
            activity_type = activity_type_obj
        
        # 构建活动文档
        activity = {
            'activityId': data.get('activityId'),
            'activityName': data.get('activityName'),
            'activityType': activity_type,
            'activityTypeDisplay': activity_type,
            'startTimeGMT': summary.get('startTimeGMT'),
            'startTimeLocal': summary.get('startTimeLocal'),
            'duration': summary.get('duration'),
            'distance': summary.get('distance'),
            'averageSpeed': summary.get('averageSpeed'),
            'maxSpeed': summary.get('maxSpeed'),
            'calories': summary.get('calories'),
            'averageHR': summary.get('averageHR'),
            'maxHR': summary.get('maxHR'),
            'elevationGain': summary.get('elevationGain'),
            'elevationLoss': summary.get('elevationLoss'),
            'averageTemperature': summary.get('averageTemperature'),
            'steps': summary.get('steps'),
            'averageCadence': summary.get('averageRunningCadenceInStepsPerMinute') or summary.get('averageSwimCadence'),
            'maxCadence': summary.get('maxRunningCadenceInStepsPerMinute'),
            'strideLength': summary.get('strideLength'),
            'vO2Max': summary.get('vO2MaxValue'),
            'trainingEffect': summary.get('trainingEffect') or summary.get('aerobicTrainingEffect'),
            'anaerobicTrainingEffect': summary.get('anaerobicTrainingEffect'),
            'locationName': data.get('locationName'),
            'startLatitude': data.get('startLatitude'),
            'startLongitude': data.get('startLongitude'),
            'endLatitude': data.get('endLatitude'),
            'endLongitude': data.get('endLongitude'),
            'deviceName': data.get('deviceName'),
            'raw_data': data,
            'created_at': datetime.utcnow()
        }
        
        # 插入MongoDB
        db.activities.update_one(
            {'activityId': activity['activityId']},
            {'$set': activity},
            upsert=True
        )
        count += 1
        
    except Exception as e:
        print(f"\n  ✗ 导入 {activity_id} 失败: {e}")

print(f"\n✓ 成功导入 {count} 个活动")

# 5. 验证数据
print("\n5. 验证数据...")
sample = db.activities.find_one({'activityId': 360757114})
if sample:
    print(f"  示例活动 360757114:")
    print(f"    activityName: {sample.get('activityName')}")
    print(f"    activityType: {sample.get('activityType')}")
    print(f"    startTimeGMT: {sample.get('startTimeGMT')}")
    print(f"    distance: {sample.get('distance')}")
    print(f"    calories: {sample.get('calories')}")
    
    if sample.get('startTimeGMT'):
        print("\n  ✓ 数据正确！")
    else:
        print("\n  ✗ 数据还是null！")
else:
    print("  未找到数据")

# 6. 统计
print("\n6. 数据库统计:")
total = db.activities.count_documents({})
print(f"  总活动数: {total}")

# 查看最新5个活动
print("\n7. 最新5个活动:")
for act in db.activities.find().sort('startTimeGMT', -1).limit(5):
    print(f"  {act.get('activityName')}: {act.get('startTimeGMT')} ({act.get('activityType')})")

client.close()

print("\n" + "=" * 60)
print("导入完成！")
print("=" * 60)

