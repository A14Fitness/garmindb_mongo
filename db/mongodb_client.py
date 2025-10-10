#!/usr/bin/env python3
"""
MongoDB客户端
管理MongoDB连接和基本操作
"""

import logging
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError

logger = logging.getLogger(__name__)


class MongoDBClient:
    """MongoDB客户端类"""

    def __init__(self, config_manager):
        """
        初始化MongoDB客户端
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.uri = config_manager.get_mongodb_uri()
        self.db_name = config_manager.get_database_name()
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """连接到MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # 测试连接
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            logger.info(f"成功连接到MongoDB数据库: {self.db_name}")
            self._setup_indexes()
        except ConnectionFailure as e:
            logger.error(f"无法连接到MongoDB: {e}")
            raise
    
    def _setup_indexes(self):
        """设置数据库索引"""
        # 监控数据索引
        self.db.monitoring.create_index([('timestamp', DESCENDING)])
        self.db.monitoring.create_index([('date', DESCENDING)])
        
        # 睡眠数据索引
        self.db.sleep.create_index([('calendarDate', DESCENDING)])
        self.db.sleep.create_index([('sleepStartTimestampGMT', DESCENDING)])
        
        # 体重数据索引
        self.db.weight.create_index([('date', DESCENDING)])
        
        # 静息心率数据索引
        self.db.resting_heart_rate.create_index([('calendarDate', DESCENDING)])
        
        # 活动数据索引
        self.db.activities.create_index([('activityId', ASCENDING)], unique=True)
        self.db.activities.create_index([('startTimeGMT', DESCENDING)])
        self.db.activities.create_index([('activityType', ASCENDING)])
        
        # 每日汇总数据索引
        self.db.daily_summary.create_index([('calendarDate', DESCENDING)], unique=True)
        
        logger.info("数据库索引设置完成")
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")
    
    # 监控数据操作
    def insert_monitoring_data(self, data):
        """插入监控数据"""
        try:
            result = self.db.monitoring.insert_many(data)
            logger.info(f"插入了 {len(result.inserted_ids)} 条监控数据")
            return result.inserted_ids
        except Exception as e:
            logger.error(f"插入监控数据失败: {e}")
            return []
    
    def get_latest_monitoring_timestamp(self):
        """获取最新的监控数据时间戳"""
        result = self.db.monitoring.find_one(
            sort=[('timestamp', DESCENDING)]
        )
        return result['timestamp'] if result else None
    
    # 睡眠数据操作
    def insert_sleep_data(self, data):
        """插入睡眠数据"""
        try:
            if isinstance(data, list):
                result = self.db.sleep.insert_many(data)
                logger.info(f"插入了 {len(result.inserted_ids)} 条睡眠数据")
                return result.inserted_ids
            else:
                result = self.db.sleep.insert_one(data)
                logger.info(f"插入了1条睡眠数据")
                return [result.inserted_id]
        except Exception as e:
            logger.error(f"插入睡眠数据失败: {e}")
            return []
    
    def get_latest_sleep_date(self):
        """获取最新的睡眠数据日期"""
        result = self.db.sleep.find_one(
            sort=[('calendarDate', DESCENDING)]
        )
        return result['calendarDate'] if result else None
    
    # 体重数据操作
    def insert_weight_data(self, data):
        """插入体重数据"""
        try:
            if isinstance(data, list):
                result = self.db.weight.insert_many(data)
                logger.info(f"插入了 {len(result.inserted_ids)} 条体重数据")
                return result.inserted_ids
            else:
                result = self.db.weight.insert_one(data)
                logger.info(f"插入了1条体重数据")
                return [result.inserted_id]
        except Exception as e:
            logger.error(f"插入体重数据失败: {e}")
            return []
    
    def get_latest_weight_date(self):
        """获取最新的体重数据日期"""
        result = self.db.weight.find_one(
            sort=[('date', DESCENDING)]
        )
        return result['date'] if result else None
    
    # 静息心率数据操作
    def insert_rhr_data(self, data):
        """插入静息心率数据"""
        try:
            if isinstance(data, list):
                result = self.db.resting_heart_rate.insert_many(data)
                logger.info(f"插入了 {len(result.inserted_ids)} 条静息心率数据")
                return result.inserted_ids
            else:
                result = self.db.resting_heart_rate.insert_one(data)
                logger.info(f"插入了1条静息心率数据")
                return [result.inserted_id]
        except Exception as e:
            logger.error(f"插入静息心率数据失败: {e}")
            return []
    
    def get_latest_rhr_date(self):
        """获取最新的静息心率数据日期"""
        result = self.db.resting_heart_rate.find_one(
            sort=[('calendarDate', DESCENDING)]
        )
        return result['calendarDate'] if result else None
    
    # 活动数据操作
    def insert_activity_data(self, data):
        """插入活动数据"""
        try:
            result = self.db.activities.update_one(
                {'activityId': data['activityId']},
                {'$set': data},
                upsert=True
            )
            if result.upserted_id:
                logger.info(f"插入新活动: {data['activityId']}")
            else:
                logger.info(f"更新活动: {data['activityId']}")
            return result.upserted_id or result.modified_count
        except Exception as e:
            logger.error(f"插入活动数据失败: {e}")
            return None
    
    def insert_activities_batch(self, activities):
        """批量插入活动数据"""
        count = 0
        for activity in activities:
            if self.insert_activity_data(activity):
                count += 1
        logger.info(f"批量插入了 {count} 条活动数据")
        return count
    
    def get_latest_activity_date(self):
        """获取最新的活动日期"""
        result = self.db.activities.find_one(
            sort=[('startTimeGMT', DESCENDING)]
        )
        return result['startTimeGMT'] if result else None
    
    def get_activity_by_id(self, activity_id):
        """根据ID获取活动"""
        return self.db.activities.find_one({'activityId': activity_id})
    
    # 每日汇总数据操作
    def insert_daily_summary(self, data):
        """插入每日汇总数据"""
        try:
            result = self.db.daily_summary.update_one(
                {'calendarDate': data['calendarDate']},
                {'$set': data},
                upsert=True
            )
            if result.upserted_id:
                logger.info(f"插入新每日汇总: {data['calendarDate']}")
            else:
                logger.info(f"更新每日汇总: {data['calendarDate']}")
            return result.upserted_id or result.modified_count
        except Exception as e:
            logger.error(f"插入每日汇总数据失败: {e}")
            return None
    
    def get_latest_daily_summary_date(self):
        """获取最新的每日汇总日期"""
        result = self.db.daily_summary.find_one(
            sort=[('calendarDate', DESCENDING)]
        )
        return result['calendarDate'] if result else None
    
    # 查询操作
    def query_monitoring_by_date_range(self, start_date, end_date):
        """查询日期范围内的监控数据"""
        return list(self.db.monitoring.find({
            'date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('timestamp', ASCENDING))
    
    def query_activities_by_date_range(self, start_date, end_date):
        """查询日期范围内的活动数据"""
        return list(self.db.activities.find({
            'startTimeGMT': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('startTimeGMT', DESCENDING))
    
    def query_activities_by_type(self, activity_type, limit=10):
        """查询特定类型的活动"""
        return list(self.db.activities.find({
            'activityType': activity_type
        }).sort('startTimeGMT', DESCENDING).limit(limit))
    
    def query_daily_summaries(self, start_date, end_date):
        """查询日期范围内的每日汇总"""
        return list(self.db.daily_summary.find({
            'calendarDate': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('calendarDate', ASCENDING))
    
    # 统计操作
    def get_stats(self):
        """获取数据库统计信息"""
        stats = {
            'monitoring_count': self.db.monitoring.count_documents({}),
            'sleep_count': self.db.sleep.count_documents({}),
            'weight_count': self.db.weight.count_documents({}),
            'rhr_count': self.db.resting_heart_rate.count_documents({}),
            'activities_count': self.db.activities.count_documents({}),
            'daily_summary_count': self.db.daily_summary.count_documents({})
        }
        return stats
    
    def get_date_ranges(self):
        """获取各类数据的日期范围"""
        ranges = {}
        
        # 监控数据范围
        first_monitoring = self.db.monitoring.find_one(sort=[('timestamp', ASCENDING)])
        last_monitoring = self.db.monitoring.find_one(sort=[('timestamp', DESCENDING)])
        if first_monitoring and last_monitoring:
            ranges['monitoring'] = {
                'start': first_monitoring['timestamp'],
                'end': last_monitoring['timestamp']
            }
        
        # 活动数据范围
        first_activity = self.db.activities.find_one(sort=[('startTimeGMT', ASCENDING)])
        last_activity = self.db.activities.find_one(sort=[('startTimeGMT', DESCENDING)])
        if first_activity and last_activity:
            ranges['activities'] = {
                'start': first_activity['startTimeGMT'],
                'end': last_activity['startTimeGMT']
            }
        
        return ranges


if __name__ == '__main__':
    # 测试MongoDB客户端
    from ..config import GarminConfigManager
    
    config = GarminConfigManager()
    client = MongoDBClient(config)
    
    print("数据库统计:")
    stats = client.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    client.close()

