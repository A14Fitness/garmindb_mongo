#!/usr/bin/env python3
"""
更新Garmin数据
增量下载最新数据并导入到MongoDB
"""

import sys
import os
import logging
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GarminConfigManager
from db import MongoDBClient
from utils import GarminDownloader, DataImporter


def setup_logging(config):
    """设置日志 [[memory:2908108]]"""
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'update.log'
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
    print("Garmin数据更新工具 - 增量更新")
    print("=" * 60)
    
    db_client = None
    
    try:
        # 加载配置
        print("\n1. 加载配置...")
        config = GarminConfigManager()
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("配置加载成功")
        
        # 下载最新数据
        print("\n2. 下载最新数据...")
        downloader = GarminDownloader(config)
        
        start_time = datetime.now()
        downloader.download_all_data(latest=True)
        download_time = datetime.now()
        
        download_duration = (download_time - start_time).total_seconds()
        print(f"  下载完成，用时 {download_duration:.1f} 秒")
        logger.info(f"下载完成，用时 {download_duration:.1f} 秒")
        
        # 连接MongoDB
        print("\n3. 连接到MongoDB...")
        db_client = MongoDBClient(config)
        logger.info("MongoDB连接成功")
        
        # 导入数据
        print("\n4. 导入数据到MongoDB...")
        importer = DataImporter(config, db_client)
        
        total_count = importer.import_all_data()
        end_time = datetime.now()
        
        import_duration = (end_time - download_time).total_seconds()
        total_duration = (end_time - start_time).total_seconds()
        
        print("-" * 60)
        print(f"\n✓ 更新完成！")
        print(f"  下载用时: {download_duration:.1f} 秒")
        print(f"  导入用时: {import_duration:.1f} 秒")
        print(f"  总用时: {total_duration:.1f} 秒")
        print(f"  新增/更新: {total_count} 条数据")
        
        # 显示数据库统计
        print("\n数据库统计:")
        stats = db_client.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # 显示数据范围
        print("\n数据范围:")
        ranges = db_client.get_date_ranges()
        for key, value in ranges.items():
            if 'start' in value and 'end' in value:
                print(f"  {key}: {value['start']} 到 {value['end']}")
        
        logger.info(f"更新完成，用时 {total_duration:.1f} 秒")
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        logging.error(f"更新失败: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if db_client:
            db_client.close()


if __name__ == '__main__':
    main()

