#!/usr/bin/env python3
"""
导入数据到MongoDB
将下载的JSON数据导入到MongoDB数据库
"""

import sys
import os
import logging
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GarminConfigManager
from db import MongoDBClient
from utils import DataImporter


def setup_logging(config):
    """设置日志 [[memory:2908108]]"""
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'import_data.log'
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main():
    """主函数"""
    print("=" * 60)
    print("Garmin数据导入工具 - 导入数据到MongoDB")
    print("=" * 60)
    
    db_client = None
    
    try:
        # 加载配置
        print("\n1. 加载配置...")
        config = GarminConfigManager()
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("配置加载成功")
        
        # 连接MongoDB
        print("\n2. 连接到MongoDB...")
        db_client = MongoDBClient(config)
        logger.info("MongoDB连接成功")
        
        # 创建导入器
        print("\n3. 初始化导入器...")
        importer = DataImporter(config, db_client)
        logger.info("导入器初始化成功")
        
        # 清空已有数据（避免重复和错误数据）
        print("\n4. 清空旧数据...")
        db_client.db.activities.delete_many({})
        db_client.db.weight.delete_many({})
        logger.info("已清空activities和weight集合")
        
        # 导入数据
        print("\n5. 开始导入数据...")
        print("   提示：如果数据还是null，请完全退出Python，清除缓存后重试")
        print("-" * 60)
        
        start_time = datetime.now()
        total_count = importer.import_all_data()
        end_time = datetime.now()
        
        # 验证导入的数据
        print("\n验证导入的数据:")
        sample = db_client.get_activity_by_id(360757114)
        if sample:
            print(f"  示例活动 360757114:")
            print(f"    startTimeGMT: {sample.get('startTimeGMT')}")
            print(f"    activityType: {sample.get('activityType')}")
            print(f"    distance: {sample.get('distance')}")
            if sample.get('startTimeGMT'):
                print("  ✓ 数据正确！")
            else:
                print("  ✗ 警告：数据字段为null，可能是Python缓存问题")
                print("  解决：完全退出终端，重新启动后再运行")
        
        duration = (end_time - start_time).total_seconds()
        
        print("-" * 60)
        print(f"\n✓ 导入完成！")
        print(f"  共导入: {total_count} 条数据")
        print(f"  用时: {duration:.1f} 秒")
        
        # 显示数据库统计
        print("\n数据库统计:")
        stats = db_client.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        logger.info(f"导入完成，共 {total_count} 条数据，用时 {duration:.1f} 秒")
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        logging.error(f"导入失败: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if db_client:
            db_client.close()


if __name__ == '__main__':
    main()

