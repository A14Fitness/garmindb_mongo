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
        """设置数据库索引（中国区简化版）"""
        # 活动数据索引（主要功能）
        # myCoach多用户系统：activityId + userId 唯一组合
        self.db.activities.create_index([('activityId', ASCENDING), ('userId', ASCENDING)], unique=True)
        self.db.activities.create_index([('userId', ASCENDING), ('startTimeGMT', DESCENDING)])
        self.db.activities.create_index([('activityType', ASCENDING)])
        
        # 体重数据索引（支持date和calendarDate作为唯一标识）
        self.db.weight.create_index([('date', DESCENDING)])
        self.db.weight.create_index([('calendarDate', DESCENDING)])
        # 尝试创建唯一索引（如果字段存在）
        try:
            self.db.weight.create_index([('date', ASCENDING)], unique=True, sparse=True)
        except:
            pass  # 如果已有重复数据则跳过
        try:
            self.db.weight.create_index([('calendarDate', ASCENDING)], unique=True, sparse=True)
        except:
            pass  # 如果已有重复数据则跳过
        
        # 训练计划数据索引
        self.db.training_plans.create_index([('date', ASCENDING)], unique=True)
        self.db.training_plans.create_index([('created_at', DESCENDING)])
        
        logger.info("数据库索引设置完成")
    
    def close(self):
        """关闭数据库连接"""
        if self.client:
            self.client.close()
            logger.info("MongoDB连接已关闭")
    
    # 以下方法在中国区不可用（API返回403 Forbidden）
    # 保留代码供将来参考或国际版用户使用
    
    # def insert_monitoring_data(self, data):
    #     """插入监控数据（中国区不可用）"""
    #     pass
    
    # def insert_sleep_data(self, data):
    #     """插入睡眠数据（中国区不可用）"""
    #     pass
    
    # def insert_rhr_data(self, data):
    #     """插入静息心率数据（中国区不可用）"""
    #     pass
    
    # def insert_daily_summary(self, data):
    #     """插入每日汇总数据（中国区不可用）"""
    #     pass
    
    # 体重数据操作（部分可用）
    def insert_weight_data(self, data):
        """插入体重数据（增量更新：如果已存在则跳过）"""
        try:
            if isinstance(data, list):
                # 批量插入，过滤已存在的记录
                inserted_count = 0
                skipped_count = 0
                for item in data:
                    date = item.get('date') or item.get('calendarDate')
                    if not date:
                        logger.warning("体重数据缺少日期字段，跳过")
                        continue
                    
                    # 检查是否已存在（基于date或calendarDate + userId）
                    query = {
                        '$or': [
                            {'date': date},
                            {'calendarDate': date}
                        ]
                    }
                    # 如果有userId，添加到查询条件
                    if 'userId' in item:
                        query['userId'] = item['userId']
                    existing = self.db.weight.find_one(query)
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # 插入新记录
                    self.db.weight.insert_one(item)
                    inserted_count += 1
                
                if inserted_count > 0:
                    logger.info(f"插入了 {inserted_count} 条新体重数据，跳过 {skipped_count} 条已存在的数据")
                else:
                    logger.debug(f"所有体重数据已存在，跳过 {skipped_count} 条")
                return inserted_count > 0
            else:
                # 单条插入
                date = data.get('date') or data.get('calendarDate')
                if not date:
                    logger.warning("体重数据缺少日期字段，跳过")
                    return False
                
                # 检查是否已存在（基于date或calendarDate + userId）
                query = {
                    '$or': [
                        {'date': date},
                        {'calendarDate': date}
                    ]
                }
                # 如果有userId，添加到查询条件
                if 'userId' in data:
                    query['userId'] = data['userId']
                existing = self.db.weight.find_one(query)
                if existing:
                    logger.debug(f"日期 {date} 的体重数据已存在（userId: {data.get('userId')}），跳过")
                    return False
                
                # 插入新记录
                result = self.db.weight.insert_one(data)
                logger.debug(f"插入新体重数据: {date}")
                return result.inserted_id is not None
        except Exception as e:
            logger.error(f"插入体重数据失败: {e}")
            return False
    
    def get_latest_weight_date(self):
        """获取最新的体重数据日期"""
        result = self.db.weight.find_one(
            sort=[('date', DESCENDING)]
        )
        return result['date'] if result else None
    
    # 活动数据操作
    def insert_activity_data(self, data):
        """插入活动数据（增量更新：如果已存在则跳过）"""
        try:
            activity_id = data.get('activityId')
            if not activity_id:
                logger.warning("活动数据缺少 activityId，跳过")
                return None
            
            # 构建查询条件：包含 activityId 和可选的 userId
            query = {'activityId': activity_id}
            if 'userId' in data:
                query['userId'] = data['userId']
            
            # 检查是否已存在
            existing = self.db.activities.find_one(query)
            if existing:
                logger.debug(f"活动 {activity_id} 已存在（userId: {data.get('userId')}），跳过")
                return False  # 返回False表示已存在，跳过
            
            # 插入新记录
            result = self.db.activities.insert_one(data)
            logger.debug(f"插入新活动: {activity_id} (userId: {data.get('userId')})")
            return result.inserted_id
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
    
    # 查询操作（活动数据）
    
    def query_activities_by_date_range(self, start_date, end_date):
        """查询日期范围内的活动数据"""
        # 将 datetime 对象转换为 ISO 格式字符串
        if isinstance(start_date, datetime):
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-5]  # 去掉多余的微秒位
        else:
            start_str = start_date
        
        if isinstance(end_date, datetime):
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-5]
        else:
            end_str = end_date
        
        return list(self.db.activities.find({
            'startTimeGMT': {
                '$gte': start_str,
                '$lte': end_str
            }
        }).sort('startTimeGMT', DESCENDING))
    
    def query_activities_by_type(self, activity_type, limit=10):
        """查询特定类型的活动"""
        return list(self.db.activities.find({
            'activityType': activity_type
        }).sort('startTimeGMT', DESCENDING).limit(limit))
    
    # 统计操作
    def get_stats(self):
        """获取数据库统计信息（中国区简化版）"""
        stats = {
            'activities_count': self.db.activities.count_documents({}),
            'weight_count': self.db.weight.count_documents({}),
            # 以下在中国区不可用
            'daily_summary_count': 0,
            'sleep_count': 0,
            'rhr_count': 0,
            'monitoring_count': 0
        }
        return stats
    
    def get_date_ranges(self):
        """获取各类数据的日期范围（中国区简化版）"""
        ranges = {}
        
        # 活动数据范围
        first_activity = self.db.activities.find_one(sort=[('startTimeGMT', ASCENDING)])
        last_activity = self.db.activities.find_one(sort=[('startTimeGMT', DESCENDING)])
        if first_activity and last_activity:
            ranges['activities'] = {
                'start': first_activity['startTimeGMT'],
                'end': last_activity['startTimeGMT']
            }
        
        return ranges
    
    # 训练计划相关方法
    def get_training_plan(self, date):
        """获取指定日期的训练计划"""
        try:
            plan = self.db.training_plans.find_one({'date': date})
            return plan
        except Exception as e:
            logger.error(f"获取训练计划失败: {e}")
            return None
    
    def save_training_plan(self, date, plan_data):
        """保存训练计划"""
        try:
            plan_doc = {
                'date': date,
                'plan_type': plan_data.get('plan_type', ''),
                'plan_content': plan_data.get('plan_content', {}),
                'completion': plan_data.get('completion', {
                    'status': 'not_started',
                    'actual_distance': None,
                    'actual_duration': None,
                    'notes': ''
                }),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.training_plans.update_one(
                {'date': date},
                {'$set': plan_doc},
                upsert=True
            )
            return result
        except Exception as e:
            logger.error(f"保存训练计划失败: {e}")
            return None
    
    def update_training_completion(self, date, completion_data):
        """更新训练完成情况"""
        try:
            update_data = {
                'completion': completion_data,
                'updated_at': datetime.utcnow()
            }
            
            result = self.db.training_plans.update_one(
                {'date': date},
                {'$set': update_data}
            )
            return result
        except Exception as e:
            logger.error(f"更新训练完成情况失败: {e}")
            return None
    
    def get_training_plans_by_date_range(self, start_date, end_date):
        """获取日期范围内的训练计划"""
        try:
            # 将日期对象转换为字符串格式
            if hasattr(start_date, 'strftime'):
                start_date_str = start_date.strftime('%Y-%m-%d')
            else:
                start_date_str = str(start_date)
                
            if hasattr(end_date, 'strftime'):
                end_date_str = end_date.strftime('%Y-%m-%d')
            else:
                end_date_str = str(end_date)
            
            plans = list(self.db.training_plans.find({
                'date': {'$gte': start_date_str, '$lte': end_date_str}
            }).sort('date', 1))
            return plans
        except Exception as e:
            logger.error(f"获取训练计划范围失败: {e}")
            return []
    
    def delete_training_plans_by_date_range(self, start_date, end_date):
        """删除日期范围内的训练计划"""
        try:
            result = self.db.training_plans.delete_many({
                'date': {'$gte': start_date, '$lte': end_date}
            })
            return result
        except Exception as e:
            logger.error(f"删除训练计划失败: {e}")
            return None


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


