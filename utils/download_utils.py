#!/usr/bin/env python3
"""
Garmin数据下载工具
从Garmin Connect下载各种健康数据
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from tqdm import tqdm

try:
    from garth import Client as GarthClient
    from garth.exc import GarthHTTPError, GarthException
except ImportError:
    print("错误: 需要安装 garth 库")
    print("请运行: pip install garth")
    sys.exit(1)

logger = logging.getLogger(__name__)


class GarminDownloader:
    """Garmin数据下载器"""

    # Garmin Connect API URLs
    garmin_connect_user_profile_url = "/userprofile-service/userprofile"
    garmin_connect_wellness_url = "/wellness-service/wellness"
    garmin_connect_sleep_daily_url = garmin_connect_wellness_url + "/dailySleepData"
    garmin_connect_rhr = "/userstats-service/wellness/daily"
    garmin_connect_weight_url = "/weight-service/weight/dateRange"
    garmin_connect_activity_search_url = "/activitylist-service/activities/search/activities"
    garmin_connect_activity_service_url = "/activity-service/activity"
    garmin_connect_download_service_url = "/download-service/files"
    garmin_connect_usersummary_url = "/usersummary-service/usersummary"
    garmin_connect_daily_summary_url = garmin_connect_usersummary_url + "/daily"
    garmin_connect_daily_hydration_url = garmin_connect_usersummary_url + "/hydration/allData"
    garmin_connect_splits_url = "/activity-service/activity/{activity_id}/splits"
    garmin_connect_laps_url = "/activity-service/activity/{activity_id}/laps"

    download_days_overlap = 3  # 重新下载最近几天的数据

    def __init__(self, config_manager):
        """
        初始化下载器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config = config_manager
        self.garth_session_file = self.config.get_session_file()
        self.garth = GarthClient()
        
        # 获取域名并配置
        domain = self.config.get_garmin_domain()
        logger.info(f"初始化 GarminDownloader，使用域名: {domain}")
        
        try:
            self.garth.configure(domain=domain)
            logger.info(f"Garth 客户端配置成功，域名: {domain}")
        except Exception as e:
            logger.error(f"配置 Garth 客户端失败: {e}", exc_info=True)
            raise
        
        # 禁用SSL验证（中国区证书问题临时解决方案）
        # 注意：国际区（garmin.com）通常不需要禁用SSL验证，但为了兼容性保留
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.garth.sess.verify = False
        
        self.display_name = None
        self.full_name = None

    def _save_json_to_file(self, filename, data):
        """保存JSON数据到文件"""
        try:
            with open(f'{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"保存数据到 {filename}.json")
            return True
        except Exception as e:
            logger.error(f"保存文件失败 {filename}.json: {e}")
            return False

    def _resume_session(self):
        """恢复Garmin会话"""
        if os.path.isfile(self.garth_session_file):
            logger.info(f"从 {self.garth_session_file} 加载会话")
            try:
                with open(self.garth_session_file, "r", encoding="utf-8") as file:
                    self.garth.loads(file.read())
                return True
            except Exception as e:
                logger.warning(f"加载会话失败: {e}")
                return False
        else:
            logger.info(f"会话文件不存在: {self.garth_session_file}")
        return False

    def _save_session(self):
        """保存Garmin会话"""
        logger.info(f"保存会话到 {self.garth_session_file}")
        try:
            with open(self.garth_session_file, "w", encoding="utf-8") as file:
                file.write(self.garth.dumps())
            return True
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
            return False

    def _login(self):
        """登录到Garmin Connect"""
        username = self.config.get_user()
        password = self.config.get_password()
        domain = self.config.get_garmin_domain()
        
        if not username or not password:
            raise ValueError("缺少配置: 需要用户名和密码。请编辑 garmin_config.json")

        logger.info(f"登录到Garmin Connect: username={username}, domain={domain}")
        try:
            # 确保使用正确的域名
            if self.garth.domain != domain:
                logger.warning(f"域名不匹配，重新配置: 当前={self.garth.domain}, 期望={domain}")
                self.garth.configure(domain=domain)
            
            logger.info(f"开始调用 garth.login()...")
            self.garth.login(username, password)
            logger.info("garth.login() 调用成功，保存会话...")
            self._save_session()
            logger.info(f"✅ 登录成功: username={username}, domain={domain}")
            return True
        except GarthHTTPError as e:
            logger.error(f"Garmin HTTP 错误: status_code={e.status_code}, response={e.response_text}")
            raise
        except GarthException as e:
            logger.error(f"Garmin 异常: {e}")
            raise
        except Exception as e:
            logger.error(f"登录失败: {e}", exc_info=True)
            raise

    def login(self):
        """登录或恢复会话"""
        expected_username = self.config.get_user()
        
        # 尝试恢复会话
        session_resumed = self._resume_session()
        
        if session_resumed:
            # ⚠️ 重要：验证 session 中的用户是否匹配当前配置中的用户
            try:
                session_username = self.garth.username
                if session_username != expected_username:
                    logger.warning(f"⚠️ Session 用户不匹配！Session中的用户: {session_username}, 期望的用户: {expected_username}")
                    logger.warning(f"   删除旧的 session 文件并重新登录...")
                    # 删除旧的 session 文件
                    if os.path.exists(self.garth_session_file):
                        os.remove(self.garth_session_file)
                    # 重新创建 garth 客户端
                    self.garth = GarthClient()
                    self.garth.configure(domain=self.config.get_garmin_domain())
                    import urllib3
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    self.garth.sess.verify = False
                    session_resumed = False  # 标记需要重新登录
            except GarthException:
                logger.warning("Session 无效，需要重新登录")
                session_resumed = False
        
        # 如果没有恢复会话或用户不匹配，重新登录
        if not session_resumed:
            self._login()

        try:
            # 测试会话是否有效
            _ = self.garth.username
        except GarthException:
            logger.warning("会话已过期，重新登录")
            self._login()

        # ⚠️ 重要：再次验证用户是否匹配
        try:
            actual_username = self.garth.username
            if actual_username != expected_username:
                logger.error(f"❌ 登录后用户不匹配！实际用户: {actual_username}, 期望用户: {expected_username}")
                raise ValueError(f"登录用户不匹配: 期望 {expected_username}, 实际 {actual_username}")
        except Exception as e:
            logger.error(f"验证用户失败: {e}")
            raise

        # 获取用户信息
        try:
            profile_dir = self.config.get_fit_files_dir()
            self._save_json_to_file(
                f'{profile_dir}/social-profile',
                self.garth.profile
            )
            self._save_json_to_file(
                f'{profile_dir}/user-settings',
                self.garth.connectapi(f'{self.garmin_connect_user_profile_url}/user-settings')
            )
            self._save_json_to_file(
                f'{profile_dir}/personal-information',
                self.garth.connectapi(f'{self.garmin_connect_user_profile_url}/personal-information')
            )

            self.display_name = self.garth.profile.get('displayName', '')
            self.full_name = self.garth.profile.get('fullName', '')
            logger.info(f"用户: {self.full_name} ({self.display_name})")
            logger.info(f"✅ 验证通过：登录用户 {actual_username} 匹配配置用户 {expected_username}")
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")

        return True

    def download_daily_summary(self, start_date, days):
        """
        下载每日汇总数据
        
        Args:
            start_date: 开始日期
            days: 下载天数
        """
        logger.info(f"下载每日汇总数据: {start_date} 开始，共 {days} 天")
        
        summary_dir = self.config.get_base_dir()
        os.makedirs(f'{summary_dir}/daily_summary', exist_ok=True)
        
        success_count = 0
        for day in tqdm(range(days), desc="每日汇总"):
            download_date = start_date + timedelta(days=day)
            date_str = download_date.strftime('%Y-%m-%d')
            
            try:
                url = f"{self.garmin_connect_daily_summary_url}/{date_str}"
                data = self.garth.connectapi(url)
                
                if data:
                    filename = f'{summary_dir}/daily_summary/{date_str}'
                    if self._save_json_to_file(filename, data):
                        success_count += 1
                else:
                    logger.debug(f"{date_str} 无数据")
            except Exception as e:
                logger.warning(f"下载 {date_str} 每日汇总失败: {e}")
        
        logger.info(f"成功保存 {success_count}/{days} 个每日汇总文件")

    def download_sleep(self, start_date, days):
        """
        下载睡眠数据
        
        Args:
            start_date: 开始日期
            days: 下载天数
        """
        logger.info(f"下载睡眠数据: {start_date} 开始，共 {days} 天")
        
        sleep_dir = self.config.get_sleep_dir()
        
        success_count = 0
        for day in tqdm(range(days), desc="睡眠数据"):
            download_date = start_date + timedelta(days=day)
            date_str = download_date.strftime('%Y-%m-%d')
            
            try:
                url = f"{self.garmin_connect_sleep_daily_url}/{date_str}"
                data = self.garth.connectapi(url)
                
                if data and 'dailySleepDTO' in data:
                    filename = f'{sleep_dir}/{date_str}'
                    if self._save_json_to_file(filename, data['dailySleepDTO']):
                        success_count += 1
                else:
                    logger.debug(f"{date_str} 无睡眠数据")
            except Exception as e:
                logger.warning(f"下载 {date_str} 睡眠数据失败: {e}")
        
        logger.info(f"成功保存 {success_count}/{days} 个睡眠数据文件")

    def download_weight(self, start_date, end_date):
        """
        下载体重数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        """
        logger.info(f"下载体重数据: {start_date} 到 {end_date}")
        
        weight_dir = self.config.get_weight_dir()
        
        try:
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            url = f"{self.garmin_connect_weight_url}?startDate={start_str}&endDate={end_str}"
            data = self.garth.connectapi(url)
            
            if data:
                # 保存完整数据
                filename = f'{weight_dir}/weight_{start_str}_to_{end_str}'
                self._save_json_to_file(filename, data)
                
                # 按日期分别保存
                for entry in data:
                    if 'date' in entry:
                        entry_date = datetime.fromtimestamp(entry['date'] / 1000).strftime('%Y-%m-%d')
                        filename = f'{weight_dir}/{entry_date}'
                        self._save_json_to_file(filename, entry)
                        
                logger.info(f"下载了 {len(data)} 条体重数据")
        except Exception as e:
            logger.error(f"下载体重数据失败: {e}")

    def download_resting_heart_rate(self, start_date, days):
        """
        下载静息心率数据
        
        Args:
            start_date: 开始日期
            days: 下载天数
        """
        logger.info(f"下载静息心率数据: {start_date} 开始，共 {days} 天")
        
        rhr_dir = self.config.get_rhr_dir()
        
        success_count = 0
        for day in tqdm(range(days), desc="静息心率"):
            download_date = start_date + timedelta(days=day)
            date_str = download_date.strftime('%Y-%m-%d')
            
            try:
                url = f"{self.garmin_connect_rhr}/{date_str}"
                data = self.garth.connectapi(url)
                
                if data:
                    filename = f'{rhr_dir}/{date_str}'
                    if self._save_json_to_file(filename, data):
                        success_count += 1
                else:
                    logger.debug(f"{date_str} 无心率数据")
            except Exception as e:
                logger.warning(f"下载 {date_str} 静息心率数据失败: {e}")
        
        logger.info(f"成功保存 {success_count}/{days} 个静息心率文件")

    def download_activities(self, start_index=0, limit=100):
        """
        下载活动列表
        
        Args:
            start_index: 起始索引
            limit: 下载数量
        """
        logger.info(f"下载活动数据: 从 {start_index} 开始，限制 {limit} 个")
        
        activities_dir = self.config.get_activities_dir()
        
        try:
            url = f"{self.garmin_connect_activity_search_url}?start={start_index}&limit={limit}"
            activities = self.garth.connectapi(url)
            
            if activities:
                logger.info(f"获取到 {len(activities)} 个活动")
                
                for activity in tqdm(activities, desc="下载活动详情"):
                    activity_id = activity.get('activityId')
                    if activity_id:
                        # 保存活动摘要
                        filename = f'{activities_dir}/{activity_id}_summary'
                        self._save_json_to_file(filename, activity)
                        
                        # 下载活动详情
                        try:
                            details_url = f"{self.garmin_connect_activity_service_url}/{activity_id}"
                            details = self.garth.connectapi(details_url)
                            if details:
                                filename = f'{activities_dir}/{activity_id}_details'
                                self._save_json_to_file(filename, details)
                        except Exception as e:
                            logger.debug(f"下载活动 {activity_id} 详情失败: {e}")
                        
                        # 下载分段数据
                        self.download_activity_splits(activity_id)
                
                return activities
            else:
                logger.info("没有获取到活动数据")
                return []
        except Exception as e:
            logger.error(f"下载活动失败: {e}")
            return []

    def download_activity_fit(self, activity_id):
        """
        下载活动的FIT文件
        
        Args:
            activity_id: 活动ID
        """
        try:
            activities_dir = self.config.get_activities_dir()
            url = f"{self.garmin_connect_download_service_url}/activity/{activity_id}"
            
            # 下载FIT文件
            fit_data = self.garth.download(url)
            
            if fit_data:
                filename = f'{activities_dir}/{activity_id}.fit'
                with open(filename, 'wb') as f:
                    f.write(fit_data)
                logger.debug(f"下载FIT文件: {filename}")
                return True
        except Exception as e:
            logger.debug(f"下载活动 {activity_id} 的FIT文件失败: {e}")
        
        return False

    def download_activity_splits(self, activity_id):
        """
        下载活动的分段数据
        
        Args:
            activity_id: 活动ID
        """
        try:
            activities_dir = self.config.get_activities_dir()
            
            # 尝试下载splits数据
            try:
                url = self.garmin_connect_splits_url.format(activity_id=activity_id)
                splits_data = self.garth.connectapi(url)
                if splits_data:
                    filename = f'{activities_dir}/{activity_id}_splits'
                    if self._save_json_to_file(filename, splits_data):
                        logger.debug(f"下载分段数据: {filename}")
                        return True
            except Exception as e:
                logger.debug(f"下载活动 {activity_id} 的splits数据失败: {e}")
            
            # 尝试下载laps数据
            try:
                url = self.garmin_connect_laps_url.format(activity_id=activity_id)
                laps_data = self.garth.connectapi(url)
                if laps_data:
                    filename = f'{activities_dir}/{activity_id}_laps'
                    if self._save_json_to_file(filename, laps_data):
                        logger.debug(f"下载分段数据: {filename}")
                        return True
            except Exception as e:
                logger.debug(f"下载活动 {activity_id} 的laps数据失败: {e}")
                
        except Exception as e:
            logger.debug(f"下载活动 {activity_id} 的分段数据失败: {e}")
        
        return False

    def download_all_data(self, latest=False):
        """
        下载所有数据（中国区仅支持活动数据）
        
        Args:
            latest: 是否只下载最新数据
        """
        logger.info("=" * 50)
        logger.info("开始下载Garmin数据")
        logger.info("=" * 50)
        
        # 登录
        self.login()
        
        today = date.today()
        
        # 中国区：只下载活动数据（其他API返回403 Forbidden）
        logger.info("中国区Garmin - 下载活动数据")
        
        # 下载活动数据
        if self.config.is_stat_enabled('activities'):
            if latest:
                limit = self.config.get_download_latest_activities()
            else:
                limit = self.config.get_download_all_activities()
            
            activities = self.download_activities(0, limit)
            logger.info(f"成功下载 {len(activities)} 个活动")
        
        # 下载体重数据（可选）
        if self.config.is_stat_enabled('weight'):
            start_date = self.config.get_start_date('weight')
            if start_date:
                end_date = today
                try:
                    self.download_weight(start_date, end_date)
                except Exception as e:
                    logger.warning(f"下载体重数据失败: {e}")
        
        logger.info("=" * 50)
        logger.info("数据下载完成")
        logger.info("=" * 50)


if __name__ == '__main__':
    # 测试下载器
    from ..config import GarminConfigManager
    
    config = GarminConfigManager()
    downloader = GarminDownloader(config)
    
    # 下载最新数据
    downloader.download_all_data(latest=True)

