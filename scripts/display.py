#!/usr/bin/env python3
"""
展示Garmin数据
查询和展示MongoDB中的健康数据
"""

import sys
import os
import logging
from datetime import datetime, timedelta, date
import argparse

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GarminConfigManager
from db import MongoDBClient


def setup_logging(config):
    """设置日志 [[memory:2908108]]"""
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'display.log'
    )
    
    logging.basicConfig(
        level=logging.WARNING,  # 显示脚本使用较少的日志
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
        ]
    )


def display_stats(db_client):
    """显示数据库统计信息"""
    print("\n" + "=" * 60)
    print("数据库统计")
    print("=" * 60)
    
    stats = db_client.get_stats()
    
    print("\n记录数量:")
    print(f"  每日汇总: {stats['daily_summary_count']}")
    print(f"  监控数据: {stats['monitoring_count']}")
    print(f"  睡眠记录: {stats['sleep_count']}")
    print(f"  体重记录: {stats['weight_count']}")
    print(f"  静息心率: {stats['rhr_count']}")
    print(f"  活动记录: {stats['activities_count']}")
    
    print("\n数据时间范围:")
    ranges = db_client.get_date_ranges()
    for key, value in ranges.items():
        if 'start' in value and 'end' in value:
            print(f"  {key}:")
            print(f"    开始: {value['start']}")
            print(f"    结束: {value['end']}")


def display_recent_activities(db_client, days=7, activity_type=None):
    """显示最近的活动"""
    print("\n" + "=" * 60)
    if activity_type:
        print(f"最近 {days} 天的{activity_type}活动")
    else:
        print(f"最近 {days} 天的活动")
    print("=" * 60)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    if activity_type:
        activities = db_client.query_activities_by_type(activity_type, limit=20)
    else:
        activities = db_client.query_activities_by_date_range(
            start_date.isoformat(),
            end_date.isoformat()
        )
    
    if not activities:
        print("  没有找到活动记录")
        return
    
    print(f"\n找到 {len(activities)} 个活动:\n")
    
    for i, activity in enumerate(activities, 1):
        activity_id = activity.get('activityId', 'N/A')
        activity_name = activity.get('activityName', '未命名')
        activity_type = activity.get('activityType', 'unknown')
        start_time = activity.get('startTimeGMT', '')
        
        # 解析时间
        if start_time:
            if isinstance(start_time, str):
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
        
        duration = activity.get('duration', 0)
        distance = activity.get('distance', 0)
        calories = activity.get('calories', 0)
        avg_hr = activity.get('averageHR', 0)
        
        # 格式化时长
        duration_str = f"{duration // 60:.0f}分{duration % 60:.0f}秒" if duration else "N/A"
        
        # 格式化距离（米转公里）
        distance_str = f"{distance / 1000:.2f}公里" if distance else "N/A"
        
        print(f"{i}. {activity_name} ({activity_type})")
        print(f"   ID: {activity_id}")
        print(f"   时间: {start_time}")
        print(f"   时长: {duration_str}")
        print(f"   距离: {distance_str}")
        print(f"   卡路里: {calories}")
        if avg_hr:
            print(f"   平均心率: {avg_hr} bpm")
        print()


def display_daily_summary(db_client, days=7):
    """显示每日汇总"""
    print("\n" + "=" * 60)
    print(f"最近 {days} 天的每日汇总")
    print("=" * 60)
    
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()
    
    summaries = db_client.query_daily_summaries(start_date, end_date)
    
    if not summaries:
        print("  没有找到每日汇总数据")
        return
    
    print(f"\n找到 {len(summaries)} 天的汇总:\n")
    print(f"{'日期':<12} {'步数':<8} {'距离(km)':<10} {'卡路里':<8} {'睡眠(h)':<8} {'心率':<10}")
    print("-" * 70)
    
    for summary in summaries:
        cal_date = summary.get('calendarDate', '')
        steps = summary.get('totalSteps', 0)
        distance = summary.get('totalDistance', 0) / 1000  # 米转公里
        calories = summary.get('totalCalories', 0)
        sleep_seconds = summary.get('sleepTimeSeconds', 0)
        sleep_hours = sleep_seconds / 3600 if sleep_seconds else 0
        rhr = summary.get('restingHeartRate', 0)
        
        rhr_str = f"{rhr}" if rhr else "N/A"
        
        print(f"{cal_date:<12} {steps:<8} {distance:<10.2f} {calories:<8} {sleep_hours:<8.1f} {rhr_str:<10}")


def display_sleep_summary(db_client, days=7):
    """显示睡眠汇总"""
    print("\n" + "=" * 60)
    print(f"最近 {days} 天的睡眠记录")
    print("=" * 60)
    
    # 查询最近的睡眠记录
    sleep_records = list(db_client.db.sleep.find().sort('calendarDate', -1).limit(days))
    
    if not sleep_records:
        print("  没有找到睡眠记录")
        return
    
    print(f"\n找到 {len(sleep_records)} 条睡眠记录:\n")
    print(f"{'日期':<12} {'总时长':<10} {'深睡':<8} {'浅睡':<8} {'REM':<8} {'清醒':<8}")
    print("-" * 70)
    
    for record in reversed(sleep_records):
        cal_date = record.get('calendarDate', '')
        total_sleep = record.get('sleepTimeSeconds', 0) / 3600
        deep_sleep = record.get('deepSleepSeconds', 0) / 3600
        light_sleep = record.get('lightSleepSeconds', 0) / 3600
        rem_sleep = record.get('remSleepSeconds', 0) / 3600
        awake = record.get('awakeSleepSeconds', 0) / 3600
        
        print(f"{cal_date:<12} {total_sleep:<10.2f} {deep_sleep:<8.2f} {light_sleep:<8.2f} {rem_sleep:<8.2f} {awake:<8.2f}")


def display_weight_records(db_client, limit=10):
    """显示体重记录"""
    print("\n" + "=" * 60)
    print(f"最近 {limit} 条体重记录")
    print("=" * 60)
    
    # 查询最近的体重记录
    weight_records = list(db_client.db.weight.find().sort('date', -1).limit(limit))
    
    if not weight_records:
        print("  没有找到体重记录")
        return
    
    print(f"\n找到 {len(weight_records)} 条体重记录:\n")
    print(f"{'日期':<12} {'体重(kg)':<10} {'BMI':<8} {'体脂率(%)':<10}")
    print("-" * 50)
    
    for record in reversed(weight_records):
        # 处理日期
        record_date = record.get('date') or record.get('calendarDate', '')
        if isinstance(record_date, int):
            record_date = datetime.fromtimestamp(record_date / 1000).strftime('%Y-%m-%d')
        
        weight = record.get('weight', 0)
        # 体重可能是克，需要转换为公斤
        if weight > 1000:
            weight = weight / 1000
        
        bmi = record.get('bmi', 0)
        body_fat = record.get('bodyFat', 0)
        
        body_fat_str = f"{body_fat:.1f}" if body_fat else "N/A"
        bmi_str = f"{bmi:.1f}" if bmi else "N/A"
        
        print(f"{record_date:<12} {weight:<10.2f} {bmi_str:<8} {body_fat_str:<10}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='查询和展示Garmin健康数据')
    parser.add_argument('--stats', action='store_true', help='显示数据库统计信息')
    parser.add_argument('--activities', action='store_true', help='显示最近的活动')
    parser.add_argument('--activity-type', type=str, help='按类型筛选活动')
    parser.add_argument('--daily', action='store_true', help='显示每日汇总')
    parser.add_argument('--sleep', action='store_true', help='显示睡眠记录')
    parser.add_argument('--weight', action='store_true', help='显示体重记录')
    parser.add_argument('--days', type=int, default=7, help='查询天数（默认7天）')
    parser.add_argument('--all', action='store_true', help='显示所有信息')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Garmin数据展示工具")
    print("=" * 60)
    
    db_client = None
    
    try:
        # 加载配置
        config = GarminConfigManager()
        setup_logging(config)
        
        # 连接MongoDB
        db_client = MongoDBClient(config)
        
        # 如果没有指定任何选项，或指定了--all，显示所有信息
        show_all = args.all or not (args.stats or args.activities or args.daily or args.sleep or args.weight)
        
        if args.stats or show_all:
            display_stats(db_client)
        
        if args.activities or show_all:
            display_recent_activities(db_client, args.days, args.activity_type)
        
        if args.daily or show_all:
            display_daily_summary(db_client, args.days)
        
        if args.sleep or show_all:
            display_sleep_summary(db_client, args.days)
        
        if args.weight or show_all:
            display_weight_records(db_client, limit=10)
        
        print("\n" + "=" * 60)
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        sys.exit(1)
    finally:
        if db_client:
            db_client.close()


if __name__ == '__main__':
    main()

