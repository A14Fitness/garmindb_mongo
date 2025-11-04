#!/usr/bin/env python3
"""
初始化设置脚本
帮助用户快速配置Garmin数据同步工具
"""

import sys
import os
import json
import shutil

def main():
    """主函数"""
    print("=" * 60)
    print("Garmin健康数据MongoDB同步工具 - 初始化设置")
    print("=" * 60)
    
    # 获取配置目录
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
    config_file = os.path.join(config_dir, 'garmin_config.json')
    example_file = os.path.join(config_dir, 'garmin_config.json.example')
    
    # 检查配置文件是否已存在
    if os.path.exists(config_file):
        print("\n配置文件已存在！")
        overwrite = input("是否要重新配置？(y/n): ").strip().lower()
        if overwrite != 'y':
            print("保持现有配置。")
            return
    
    # 复制示例配置文件
    print("\n开始配置...")
    shutil.copy(example_file, config_file)
    
    # 加载配置
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # MongoDB配置
    print("\n" + "=" * 60)
    print("MongoDB配置")
    print("=" * 60)
    
    use_default_mongo = input("使用默认MongoDB配置（localhost:27999）？(Y/n): ").strip().lower()
    if use_default_mongo != 'n':
        print("使用默认MongoDB配置")
    else:
        mongo_host = input("MongoDB主机地址 [localhost]: ").strip() or "localhost"
        mongo_port = input("MongoDB端口 [27999]: ").strip() or "27999"
        mongo_user = input("MongoDB用户名（无则留空）: ").strip()
        mongo_pass = input("MongoDB密码（无则留空）: ").strip()
        mongo_db = input("数据库名称 [garmin_health]: ").strip() or "garmin_health"
        
        config['mongodb']['host'] = mongo_host
        config['mongodb']['port'] = int(mongo_port)
        config['mongodb']['username'] = mongo_user
        config['mongodb']['password'] = mongo_pass
        config['mongodb']['database'] = mongo_db
    
    # Garmin凭证
    print("\n" + "=" * 60)
    print("Garmin Connect账号配置")
    print("=" * 60)
    print("请输入您的Garmin Connect登录信息：")
    
    garmin_user = input("Garmin用户名（邮箱）: ").strip()
    garmin_pass = input("Garmin密码: ").strip()
    
    if not garmin_user or not garmin_pass:
        print("\n✗ 错误: 必须提供Garmin用户名和密码！")
        sys.exit(1)
    
    config['credentials']['user'] = garmin_user
    config['credentials']['password'] = garmin_pass
    
    # 数据起始日期
    print("\n" + "=" * 60)
    print("数据起始日期配置")
    print("=" * 60)
    print("请输入要下载数据的起始日期（格式：YYYY-MM-DD）")
    print("建议设置为您开始使用Garmin设备的日期")
    
    start_date = input("起始日期 [2020-01-01]: ").strip() or "2020-01-01"
    
    config['data']['weight_start_date'] = start_date
    config['data']['sleep_start_date'] = start_date
    config['data']['rhr_start_date'] = start_date
    config['data']['monitoring_start_date'] = start_date
    
    # 保存配置
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print("\n" + "=" * 60)
    print("✓ 配置完成！")
    print("=" * 60)
    print(f"\n配置文件已保存到: {config_file}")
    print("\n下一步操作：")
    print("  1. 确保MongoDB正在运行")
    print("  2. 运行 'python scripts/download_all.py' 下载所有数据")
    print("  3. 运行 'python scripts/import_data.py' 导入数据到MongoDB")
    print("  4. 运行 'python scripts/display.py' 查看数据")
    print("\n或者运行 'python scripts/update.py' 一次性完成下载和导入")


if __name__ == '__main__':
    main()

