#!/usr/bin/env python3
"""
下载所有Garmin数据
从Garmin Connect下载所有历史健康数据
"""

import sys
import os
import logging
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import GarminConfigManager
from utils import GarminDownloader


def setup_logging(config):
    """设置日志 [[memory:2908108]]"""
    log_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'download_all.log'
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
    print("Garmin数据下载工具 - 下载所有数据")
    print("=" * 60)
    
    try:
        # 加载配置
        print("\n1. 加载配置...")
        config = GarminConfigManager()
        setup_logging(config)
        logger = logging.getLogger(__name__)
        logger.info("配置加载成功")
        
        # 创建下载器
        print("\n2. 初始化下载器...")
        downloader = GarminDownloader(config)
        logger.info("下载器初始化成功")
        
        # 下载所有数据
        print("\n3. 开始下载数据...")
        print("注意: 首次下载可能需要较长时间，请耐心等待")
        print("-" * 60)
        
        start_time = datetime.now()
        downloader.download_all_data(latest=False)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print("-" * 60)
        print(f"\n✓ 下载完成！")
        print(f"  用时: {duration:.1f} 秒")
        print(f"  数据保存在: {config.get_base_dir()}")
        print("\n下一步:")
        print("  运行 'python scripts/import_data.py' 将数据导入MongoDB")
        
        logger.info(f"下载完成，用时 {duration:.1f} 秒")
        
    except FileNotFoundError as e:
        print(f"\n✗ 错误: {e}")
        print("\n请按以下步骤操作:")
        print("  1. 复制 config/garmin_config.json.example 为 config/garmin_config.json")
        print("  2. 编辑 config/garmin_config.json，填入你的Garmin账号信息")
        print("  3. 重新运行此脚本")
        sys.exit(1)
    except ValueError as e:
        print(f"\n✗ 配置错误: {e}")
        print("\n请检查配置文件 config/garmin_config.json")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        logging.error(f"下载失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

