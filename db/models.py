#!/usr/bin/env python3
"""
数据模型
定义各种健康数据的结构
"""

from datetime import datetime
from typing import Dict, Any, Optional


class MonitoringData:
    """监控数据模型（心率、步数、强度等）"""
    
    @staticmethod
    def from_fit_data(fit_data: Dict[str, Any]) -> Dict[str, Any]:
        """从FIT文件数据创建监控数据"""
        return {
            'timestamp': fit_data.get('timestamp'),
            'date': fit_data.get('timestamp').date() if fit_data.get('timestamp') else None,
            'heart_rate': fit_data.get('heart_rate'),
            'steps': fit_data.get('steps'),
            'intensity': fit_data.get('intensity'),
            'calories': fit_data.get('calories'),
            'distance': fit_data.get('distance'),
            'active_time': fit_data.get('active_time'),
            'climb': fit_data.get('ascent'),
            'descent': fit_data.get('descent'),
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建监控数据"""
        return {
            'date': json_data.get('calendarDate'),
            'steps': json_data.get('totalSteps'),
            'distance': json_data.get('totalDistanceMeters'),
            'calories': json_data.get('activeKilocalories'),
            'active_time': json_data.get('activeTimeInSeconds'),
            'moderate_intensity_minutes': json_data.get('moderateIntensityMinutes'),
            'vigorous_intensity_minutes': json_data.get('vigorousIntensityMinutes'),
            'floors_climbed': json_data.get('floorsAscended'),
            'created_at': datetime.utcnow()
        }


class SleepData:
    """睡眠数据模型"""
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建睡眠数据"""
        return {
            'calendarDate': json_data.get('calendarDate'),
            'sleepStartTimestampGMT': json_data.get('sleepStartTimestampGMT'),
            'sleepEndTimestampGMT': json_data.get('sleepEndTimestampGMT'),
            'sleepTimeSeconds': json_data.get('sleepTimeSeconds'),
            'deepSleepSeconds': json_data.get('deepSleepSeconds'),
            'lightSleepSeconds': json_data.get('lightSleepSeconds'),
            'remSleepSeconds': json_data.get('remSleepSeconds'),
            'awakeSleepSeconds': json_data.get('awakeSleepSeconds'),
            'averageSpO2Value': json_data.get('averageSpO2Value'),
            'lowestSpO2Value': json_data.get('lowestSpO2Value'),
            'highestSpO2Value': json_data.get('highestSpO2Value'),
            'averageRespirationValue': json_data.get('averageRespirationValue'),
            'averageHeartRate': json_data.get('averageHeartRate'),
            'sleepScores': json_data.get('sleepScores'),
            'sleepLevels': json_data.get('sleepLevels'),
            'created_at': datetime.utcnow()
        }


class WeightData:
    """体重数据模型"""
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建体重数据"""
        return {
            'date': json_data.get('date'),
            'calendarDate': json_data.get('calendarDate'),
            'weight': json_data.get('weight'),
            'bmi': json_data.get('bmi'),
            'bodyFat': json_data.get('bodyFat'),
            'bodyWater': json_data.get('bodyWater'),
            'boneMass': json_data.get('boneMass'),
            'muscleMass': json_data.get('muscleMass'),
            'sourceType': json_data.get('sourceType'),
            'created_at': datetime.utcnow()
        }


class RestingHeartRateData:
    """静息心率数据模型"""
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建静息心率数据"""
        return {
            'calendarDate': json_data.get('calendarDate'),
            'restingHeartRate': json_data.get('restingHeartRate'),
            'created_at': datetime.utcnow()
        }


class ActivityData:
    """活动数据模型"""
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建活动数据"""
        return {
            'activityId': json_data.get('activityId'),
            'activityName': json_data.get('activityName'),
            'activityType': json_data.get('activityType', {}).get('typeKey'),
            'activityTypeDisplay': json_data.get('activityType', {}).get('typeKey'),
            'startTimeGMT': json_data.get('startTimeGMT'),
            'startTimeLocal': json_data.get('startTimeLocal'),
            'duration': json_data.get('duration'),
            'distance': json_data.get('distance'),
            'averageSpeed': json_data.get('averageSpeed'),
            'maxSpeed': json_data.get('maxSpeed'),
            'calories': json_data.get('calories'),
            'averageHR': json_data.get('averageHR'),
            'maxHR': json_data.get('maxHR'),
            'elevationGain': json_data.get('elevationGain'),
            'elevationLoss': json_data.get('elevationLoss'),
            'averageTemperature': json_data.get('averageTemperature'),
            'steps': json_data.get('steps'),
            'averageCadence': json_data.get('averageRunningCadenceInStepsPerMinute'),
            'maxCadence': json_data.get('maxRunningCadenceInStepsPerMinute'),
            'strideLength': json_data.get('strideLength'),
            'vO2Max': json_data.get('vO2MaxValue'),
            'trainingEffect': json_data.get('aerobicTrainingEffect'),
            'anaerobicTrainingEffect': json_data.get('anaerobicTrainingEffect'),
            'locationName': json_data.get('locationName'),
            'startLatitude': json_data.get('startLatitude'),
            'startLongitude': json_data.get('startLongitude'),
            'endLatitude': json_data.get('endLatitude'),
            'endLongitude': json_data.get('endLongitude'),
            'deviceName': json_data.get('deviceName'),
            'raw_data': json_data,  # 保存原始数据
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def from_fit_data(fit_data: Dict[str, Any], activity_id: int) -> Dict[str, Any]:
        """从FIT文件数据创建活动数据"""
        return {
            'activityId': activity_id,
            'startTimeGMT': fit_data.get('start_time'),
            'duration': fit_data.get('total_timer_time'),
            'distance': fit_data.get('total_distance'),
            'calories': fit_data.get('total_calories'),
            'averageHR': fit_data.get('avg_heart_rate'),
            'maxHR': fit_data.get('max_heart_rate'),
            'elevationGain': fit_data.get('total_ascent'),
            'elevationLoss': fit_data.get('total_descent'),
            'averageSpeed': fit_data.get('avg_speed'),
            'maxSpeed': fit_data.get('max_speed'),
            'steps': fit_data.get('total_steps'),
            'raw_fit_data': fit_data,
            'created_at': datetime.utcnow()
        }


class DailySummaryData:
    """每日汇总数据模型"""
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建每日汇总数据"""
        return {
            'calendarDate': json_data.get('calendarDate'),
            'totalSteps': json_data.get('totalSteps'),
            'totalDistance': json_data.get('totalDistanceMeters'),
            'activeCalories': json_data.get('activeKilocalories'),
            'bmrCalories': json_data.get('bmrKilocalories'),
            'totalCalories': json_data.get('totalKilocalories'),
            'minHeartRate': json_data.get('minHeartRate'),
            'maxHeartRate': json_data.get('maxHeartRate'),
            'restingHeartRate': json_data.get('restingHeartRate'),
            'moderateIntensityMinutes': json_data.get('moderateIntensityMinutes'),
            'vigorousIntensityMinutes': json_data.get('vigorousIntensityMinutes'),
            'intensityMinutesGoal': json_data.get('intensityMinutesGoal'),
            'floorsAscended': json_data.get('floorsAscended'),
            'floorsDescended': json_data.get('floorsDescended'),
            'stepsGoal': json_data.get('dailyStepGoal'),
            'distanceGoal': json_data.get('userDailySummary', {}).get('distanceGoalInMeters'),
            'activeTimeSeconds': json_data.get('activeTimeInSeconds'),
            'sedentaryTimeSeconds': json_data.get('sedentaryTimeInSeconds'),
            'sleepTimeSeconds': json_data.get('sleepTimeInSeconds'),
            'stressLevel': json_data.get('averageStressLevel'),
            'bodyBatteryCharged': json_data.get('bodyBatteryChargedValue'),
            'bodyBatteryDrained': json_data.get('bodyBatteryDrainedValue'),
            'bodyBatteryHighest': json_data.get('bodyBatteryHighestValue'),
            'bodyBatteryLowest': json_data.get('bodyBatteryLowestValue'),
            'raw_data': json_data,
            'created_at': datetime.utcnow()
        }


class UserProfile:
    """用户配置数据模型"""
    
    @staticmethod
    def from_json_data(json_data: Dict[str, Any]) -> Dict[str, Any]:
        """从JSON数据创建用户配置数据"""
        return {
            'userId': json_data.get('id'),
            'displayName': json_data.get('displayName'),
            'fullName': json_data.get('fullName'),
            'profileImageUrl': json_data.get('profileImageUrl'),
            'level': json_data.get('level'),
            'created_at': datetime.utcnow()
        }

