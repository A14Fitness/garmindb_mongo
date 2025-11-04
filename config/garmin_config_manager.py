#!/usr/bin/env python3
"""
Garmin配置管理器
管理从配置文件中读取和使用配置
"""

import os
import json
import logging
from datetime import datetime, date
from pathlib import Path

logger = logging.getLogger(__name__)


class GarminConfigManager:
    """管理Garmin配置的类"""

    def __init__(self, config_path=None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径。如果为None，则在默认位置查找
        """
        if config_path is None:
            # 默认配置路径
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config', 'garmin_config.json'
            )
        
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging()
    
    def _load_config(self):
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请复制 garmin_config.json.example 为 garmin_config.json 并编辑"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _setup_logging(self):
        """设置日志级别"""
        log_level = self.config.get('settings', {}).get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # MongoDB配置
    def get_mongodb_config(self):
        """获取MongoDB配置"""
        return self.config.get('mongodb', {})
    
    def get_mongodb_uri(self):
        """获取MongoDB连接URI"""
        mongo_config = self.get_mongodb_config()
        username = mongo_config.get('username', '')
        password = mongo_config.get('password', '')
        host = mongo_config.get('host', 'localhost')
        port = mongo_config.get('port', 27999)
        auth_source = mongo_config.get('auth_source', 'admin')
        
        if username and password:
            return f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
        else:
            return f"mongodb://{host}:{port}/"
    
    def get_database_name(self):
        """获取数据库名称"""
        return self.config.get('mongodb', {}).get('database', 'garmin_health')
    
    # Garmin配置
    def get_garmin_domain(self):
        """获取Garmin域名"""
        return self.config.get('garmin', {}).get('domain', 'garmin.com')
    
    def get_garmin_base_domain(self):
        """获取Garmin基础域名"""
        domain = self.get_garmin_domain()
        return f"https://connect.{domain}"
    
    # 凭证配置
    def get_user(self):
        """获取Garmin用户名"""
        return self.config.get('credentials', {}).get('user', '')
    
    def get_password(self):
        """获取Garmin密码"""
        password = self.config.get('credentials', {}).get('password', '')
        password_file = self.config.get('credentials', {}).get('password_file')
        
        if password_file and os.path.exists(password_file):
            with open(password_file, 'r') as f:
                return f.read().strip()
        
        return password
    
    # 数据配置
    def get_start_date(self, stat_type):
        """
        获取特定数据类型的起始日期
        
        Args:
            stat_type: 数据类型（weight, sleep, rhr, monitoring）
        
        Returns:
            date对象
        """
        key = f"{stat_type}_start_date"
        date_str = self.config.get('data', {}).get(key)
        if date_str:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        return None
    
    def get_download_latest_activities(self):
        """获取下载最新活动的数量"""
        return self.config.get('data', {}).get('download_latest_activities', 25)
    
    def get_download_all_activities(self):
        """获取下载全部活动的数量"""
        return self.config.get('data', {}).get('download_all_activities', 1000)
    
    # 目录配置
    def get_base_dir(self):
        """获取基础数据目录"""
        base_dir = self.config.get('directories', {}).get('base_dir', 'mydata')
        
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(base_dir):
            # 相对于garmin目录
            base_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                base_dir
            )
        
        # 确保目录存在
        os.makedirs(base_dir, exist_ok=True)
        return base_dir
    
    def get_fit_files_dir(self):
        """获取FIT文件目录"""
        fit_dir = os.path.join(self.get_base_dir(), 'fit')
        os.makedirs(fit_dir, exist_ok=True)
        return fit_dir
    
    def get_activities_dir(self):
        """获取活动数据目录"""
        activities_dir = os.path.join(self.get_base_dir(), 'activities')
        os.makedirs(activities_dir, exist_ok=True)
        return activities_dir
    
    def get_monitoring_dir(self, year=None):
        """获取监控数据目录"""
        if year is None:
            year = datetime.now().year
        monitoring_dir = os.path.join(self.get_base_dir(), 'monitoring', str(year))
        os.makedirs(monitoring_dir, exist_ok=True)
        return monitoring_dir
    
    def get_sleep_dir(self):
        """获取睡眠数据目录"""
        sleep_dir = os.path.join(self.get_base_dir(), 'sleep')
        os.makedirs(sleep_dir, exist_ok=True)
        return sleep_dir
    
    def get_weight_dir(self):
        """获取体重数据目录"""
        weight_dir = os.path.join(self.get_base_dir(), 'weight')
        os.makedirs(weight_dir, exist_ok=True)
        return weight_dir
    
    def get_rhr_dir(self):
        """获取静息心率数据目录"""
        rhr_dir = os.path.join(self.get_base_dir(), 'rhr')
        os.makedirs(rhr_dir, exist_ok=True)
        return rhr_dir
    
    def get_session_file(self):
        """获取Garmin会话文件路径"""
        session_file = os.path.join(self.get_base_dir(), '.garmin_session')
        return session_file
    
    # 功能开关配置
    def is_stat_enabled(self, stat_type):
        """检查特定统计数据类型是否启用"""
        return self.config.get('enabled_stats', {}).get(stat_type, True)
    
    # 设置配置
    def is_metric(self):
        """是否使用公制单位"""
        return self.config.get('settings', {}).get('metric', True)
    
    def get_default_display_activities(self):
        """获取默认显示的活动类型"""
        return self.config.get('settings', {}).get(
            'default_display_activities',
            ['walking', 'running', 'cycling']
        )
    
    # 检查配置
    def get_checkup_look_back_days(self):
        """获取数据检查回溯天数"""
        return self.config.get('checkup', {}).get('look_back_days', 90)


if __name__ == '__main__':
    # 测试配置管理器
    config = GarminConfigManager()
    print(f"MongoDB URI: {config.get_mongodb_uri()}")
    print(f"Database: {config.get_database_name()}")
    print(f"Base Dir: {config.get_base_dir()}")
    print(f"Garmin Domain: {config.get_garmin_base_domain()}")

