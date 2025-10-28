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
        # 判断是summary还是details文件
        is_details = 'summaryDTO' in json_data
        
        if is_details:
            # details文件：数据在summaryDTO中
            summary = json_data.get('summaryDTO', {})
            activity_type_obj = json_data.get('activityTypeDTO', {})
            metadata = json_data.get('metadataDTO', {})
        else:
            # summary文件：数据在根级别
            summary = json_data
            activity_type_obj = json_data.get('activityType', {})
            metadata = {}
        
        # 提取activityType
        activity_type = activity_type_obj.get('typeKey') if isinstance(activity_type_obj, dict) else activity_type_obj
        
        return {
            'activityId': json_data.get('activityId'),
            'activityName': json_data.get('activityName'),
            'activityType': activity_type,
            'activityTypeDisplay': activity_type,
            'startTimeGMT': summary.get('startTimeGMT'),
            'startTimeLocal': summary.get('startTimeLocal'),
            'duration': summary.get('duration'),
            'movingDuration': summary.get('movingDuration'),
            'elapsedDuration': summary.get('elapsedDuration'),
            'distance': summary.get('distance'),
            'averageSpeed': summary.get('averageSpeed'),
            'maxSpeed': summary.get('maxSpeed'),
            'calories': summary.get('calories'),
            'bmrCalories': summary.get('bmrCalories'),
            'averageHR': summary.get('averageHR'),
            'maxHR': summary.get('maxHR'),
            'minHR': summary.get('minHR'),
            'elevationGain': summary.get('elevationGain'),
            'elevationLoss': summary.get('elevationLoss'),
            'minElevation': summary.get('minElevation'),
            'maxElevation': summary.get('maxElevation'),
            'averageTemperature': summary.get('averageTemperature'),
            'steps': summary.get('steps'),
            'averageCadence': summary.get('averageRunningCadenceInStepsPerMinute') or summary.get('averageSwimCadence'),
            'maxCadence': summary.get('maxRunningCadenceInStepsPerMinute'),
            'averageRunCadence': summary.get('averageRunningCadenceInStepsPerMinute'),
            'averageSwimCadence': summary.get('averageSwimCadence'),
            'strideLength': summary.get('strideLength'),
            'averageStrideLength': summary.get('averageStrideLength'),
            'vO2Max': summary.get('vO2MaxValue'),
            'trainingEffect': summary.get('trainingEffect') or summary.get('aerobicTrainingEffect'),
            'anaerobicTrainingEffect': summary.get('anaerobicTrainingEffect'),
            'locationName': json_data.get('locationName'),
            'startLatitude': json_data.get('startLatitude'),
            'startLongitude': json_data.get('startLongitude'),
            'endLatitude': json_data.get('endLatitude'),
            'endLongitude': json_data.get('endLongitude'),
            'deviceName': json_data.get('deviceName'),
            # 游泳专属字段
            'poolLength': summary.get('poolLength'),
            'numberOfActiveLengths': summary.get('numberOfActiveLengths'),
            'totalNumberOfStrokes': summary.get('totalNumberOfStrokes'),
            'averageStrokes': summary.get('averageStrokes'),
            'averageSWOLF': summary.get('averageSWOLF'),
            'averageStrokeDistance': summary.get('averageStrokeDistance'),
            'unitOfPoolLength': summary.get('unitOfPoolLength'),
            # 骑行专属字段
            'averagePower': summary.get('averagePower'),
            'maxPower': summary.get('maxPower'),
            'averageCadence_cycling': summary.get('averageCadence'),
            # 跑步专属字段
            'ascentTime': summary.get('ascentTime'),
            'descentTime': summary.get('descentTime'),
            'flatTime': summary.get('flatTime'),
            # 训练相关
            'moderateIntensityMinutes': summary.get('moderateIntensityMinutes'),
            'vigorousIntensityMinutes': summary.get('vigorousIntensityMinutes'),
            'trainingEffectLabel': summary.get('trainingEffectLabel'),
            'activityTrainingLoad': summary.get('activityTrainingLoad'),
            'directWorkoutFeel': summary.get('directWorkoutFeel'),
            'directWorkoutRpe': summary.get('directWorkoutRpe'),
            'recoveryHeartRate': summary.get('recoveryHeartRate'),
            # 元数据
            'lapCount': metadata.get('lapCount'),
            'hasSplits': metadata.get('hasSplits'),
            'hasChartData': metadata.get('hasChartData'),
            'elevationCorrected': metadata.get('elevationCorrected'),
            'manualActivity': metadata.get('manualActivity'),
            'personalRecord': metadata.get('personalRecord'),
            'favorite': metadata.get('favorite'),
            'raw_data': json_data,  # 保存原始数据
            'splits_data': None,  # 分段数据（稍后从splits/laps文件加载）
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


