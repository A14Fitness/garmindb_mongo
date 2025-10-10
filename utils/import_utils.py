#!/usr/bin/env python3
"""
数据导入工具
将下载的JSON文件导入到MongoDB
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

logger = logging.getLogger(__name__)


class DataImporter:
    """数据导入器"""

    def __init__(self, config_manager, db_client):
        """
        初始化导入器
        
        Args:
            config_manager: 配置管理器实例
            db_client: MongoDB客户端实例
        """
        self.config = config_manager
        self.db = db_client

    def _load_json_file(self, filepath):
        """加载JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载文件失败 {filepath}: {e}")
            return None

    def _get_json_files(self, directory):
        """获取目录中的所有JSON文件"""
        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return []
        
        json_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.join(root, file))
        
        return sorted(json_files)

    def import_daily_summaries(self):
        """导入每日汇总数据"""
        logger.info("导入每日汇总数据...")
        
        summary_dir = os.path.join(self.config.get_base_dir(), 'daily_summary')
        json_files = self._get_json_files(summary_dir)
        
        if not json_files:
            logger.warning("没有找到每日汇总数据文件")
            return 0
        
        count = 0
        for filepath in tqdm(json_files, desc="导入每日汇总"):
            data = self._load_json_file(filepath)
            if data:
                from ..db.models import DailySummaryData
                summary = DailySummaryData.from_json_data(data)
                if self.db.insert_daily_summary(summary):
                    count += 1
        
        logger.info(f"成功导入 {count} 条每日汇总数据")
        return count

    def import_sleep_data(self):
        """导入睡眠数据"""
        logger.info("导入睡眠数据...")
        
        sleep_dir = self.config.get_sleep_dir()
        json_files = self._get_json_files(sleep_dir)
        
        if not json_files:
            logger.warning("没有找到睡眠数据文件")
            return 0
        
        count = 0
        for filepath in tqdm(json_files, desc="导入睡眠数据"):
            data = self._load_json_file(filepath)
            if data:
                from ..db.models import SleepData
                sleep = SleepData.from_json_data(data)
                if self.db.insert_sleep_data(sleep):
                    count += 1
        
        logger.info(f"成功导入 {count} 条睡眠数据")
        return count

    def import_weight_data(self):
        """导入体重数据"""
        logger.info("导入体重数据...")
        
        weight_dir = self.config.get_weight_dir()
        json_files = self._get_json_files(weight_dir)
        
        if not json_files:
            logger.warning("没有找到体重数据文件")
            return 0
        
        # 过滤掉范围文件，只导入单日文件
        daily_files = [f for f in json_files if '_to_' not in f]
        
        count = 0
        for filepath in tqdm(daily_files, desc="导入体重数据"):
            data = self._load_json_file(filepath)
            if data:
                from ..db.models import WeightData
                # 如果是数组，遍历每个条目
                if isinstance(data, list):
                    for entry in data:
                        weight = WeightData.from_json_data(entry)
                        if self.db.insert_weight_data(weight):
                            count += 1
                else:
                    weight = WeightData.from_json_data(data)
                    if self.db.insert_weight_data(weight):
                        count += 1
        
        logger.info(f"成功导入 {count} 条体重数据")
        return count

    def import_rhr_data(self):
        """导入静息心率数据"""
        logger.info("导入静息心率数据...")
        
        rhr_dir = self.config.get_rhr_dir()
        json_files = self._get_json_files(rhr_dir)
        
        if not json_files:
            logger.warning("没有找到静息心率数据文件")
            return 0
        
        count = 0
        for filepath in tqdm(json_files, desc="导入静息心率"):
            data = self._load_json_file(filepath)
            if data and isinstance(data, dict):
                # 检查是否有静息心率数据
                if 'restingHeartRate' in data and data['restingHeartRate']:
                    from ..db.models import RestingHeartRateData
                    rhr = RestingHeartRateData.from_json_data(data)
                    if self.db.insert_rhr_data(rhr):
                        count += 1
        
        logger.info(f"成功导入 {count} 条静息心率数据")
        return count

    def import_activities(self):
        """导入活动数据"""
        logger.info("导入活动数据...")
        
        activities_dir = self.config.get_activities_dir()
        json_files = self._get_json_files(activities_dir)
        
        if not json_files:
            logger.warning("没有找到活动数据文件")
            return 0
        
        # 只导入摘要文件或详情文件（优先详情）
        activity_files = {}
        for filepath in json_files:
            filename = os.path.basename(filepath)
            if '_summary.json' in filename:
                activity_id = filename.replace('_summary.json', '')
                if activity_id not in activity_files or '_details' not in activity_files[activity_id]:
                    activity_files[activity_id] = filepath
            elif '_details.json' in filename:
                activity_id = filename.replace('_details.json', '')
                activity_files[activity_id] = filepath
        
        count = 0
        for activity_id, filepath in tqdm(activity_files.items(), desc="导入活动"):
            data = self._load_json_file(filepath)
            if data:
                from ..db.models import ActivityData
                activity = ActivityData.from_json_data(data)
                if self.db.insert_activity_data(activity):
                    count += 1
        
        logger.info(f"成功导入 {count} 条活动数据")
        return count

    def import_all_data(self):
        """导入所有数据"""
        logger.info("=" * 50)
        logger.info("开始导入数据到MongoDB")
        logger.info("=" * 50)
        
        total_count = 0
        
        # 导入各类数据
        if self.config.is_stat_enabled('monitoring'):
            total_count += self.import_daily_summaries()
        
        if self.config.is_stat_enabled('sleep'):
            total_count += self.import_sleep_data()
        
        if self.config.is_stat_enabled('weight'):
            total_count += self.import_weight_data()
        
        if self.config.is_stat_enabled('rhr'):
            total_count += self.import_rhr_data()
        
        if self.config.is_stat_enabled('activities'):
            total_count += self.import_activities()
        
        logger.info("=" * 50)
        logger.info(f"数据导入完成，共导入 {total_count} 条数据")
        logger.info("=" * 50)
        
        # 显示统计信息
        stats = self.db.get_stats()
        logger.info("\n数据库统计:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
        return total_count


if __name__ == '__main__':
    # 测试导入器
    from ..config import GarminConfigManager
    from ..db import MongoDBClient
    
    config = GarminConfigManager()
    db_client = MongoDBClient(config)
    importer = DataImporter(config, db_client)
    
    importer.import_all_data()
    
    db_client.close()

