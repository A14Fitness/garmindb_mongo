# Garmin健康数据MongoDB同步工具

这是一个基于MongoDB的Garmin健康数据同步工具，可以从Garmin Connect下载您的所有健康数据并存储到MongoDB数据库中。

## 功能特性

- ✅ 从Garmin Connect自动下载健康数据
- ✅ 支持多种数据类型：
  - 每日活动汇总（步数、距离、卡路里等）
  - 睡眠记录（深睡、浅睡、REM睡眠等）
  - 体重和身体成分数据
  - 静息心率数据
  - 运动活动详情
- ✅ 数据存储在MongoDB数据库
- ✅ 增量更新支持
- ✅ 数据查询和展示
- ✅ 完整的日志记录

## 目录结构

```
garmin/
├── config/                     # 配置文件目录
│   ├── garmin_config.json.example  # 配置文件示例
│   ├── garmin_config_manager.py    # 配置管理器
│   └── __init__.py
├── db/                         # 数据库模块
│   ├── mongodb_client.py       # MongoDB客户端
│   ├── models.py               # 数据模型
│   └── __init__.py
├── utils/                      # 工具模块
│   ├── download_utils.py       # 下载工具
│   ├── import_utils.py         # 导入工具
│   └── __init__.py
├── scripts/                    # 脚本目录
│   ├── download_all.py         # 下载所有数据
│   ├── update.py               # 增量更新数据
│   ├── import_data.py          # 导入数据到MongoDB
│   ├── display.py              # 查询和展示数据
│   └── __init__.py
├── mydata/                     # 数据存储目录（自动创建）
│   ├── fit/                    # FIT文件
│   ├── activities/             # 活动数据
│   ├── daily_summary/          # 每日汇总
│   ├── sleep/                  # 睡眠数据
│   ├── weight/                 # 体重数据
│   └── rhr/                    # 静息心率数据
├── requirements.txt            # Python依赖
└── README.md                   # 本文件
```

## 安装步骤

### 1. 安装依赖

确保您已经安装了Python 3.8或更高版本，以及MongoDB数据库。

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 2. 安装MongoDB

如果您还没有安装MongoDB，请参考[MongoDB官方文档](https://docs.mongodb.com/manual/installation/)进行安装。

Ubuntu/Debian:
```bash
sudo apt-get install mongodb
```

macOS:
```bash
brew install mongodb-community
```

### 3. 配置

复制配置文件示例并编辑：

```bash
cd config
cp garmin_config.json.example garmin_config.json
```

编辑 `garmin_config.json`，填入您的信息：

```json
{
    "mongodb": {
        "host": "localhost",
        "port": 27017,
        "database": "garmin_health",
        "username": "",
        "password": ""
    },
    "credentials": {
        "user": "your_garmin_email",
        "password": "your_garmin_password"
    },
    "data": {
        "weight_start_date": "2020-01-01",
        "sleep_start_date": "2020-01-01",
        "rhr_start_date": "2020-01-01",
        "monitoring_start_date": "2020-01-01"
    }
}
```

**重要配置说明：**
- `mongodb`: MongoDB连接配置
- `credentials`: Garmin Connect账号密码
- `data`: 各类数据的起始日期（建议设置为您开始使用Garmin设备的日期）

## 使用方法

### 首次使用 - 下载所有历史数据

```bash
# 1. 下载所有数据
python scripts/download_all.py

# 2. 导入数据到MongoDB
python scripts/import_data.py
```

### 日常使用 - 增量更新

```bash
# 下载最新数据并导入（推荐定期运行，如每天一次）
python scripts/update.py
```

### 查询和展示数据

```bash
# 显示所有信息（默认）
python scripts/display.py

# 只显示统计信息
python scripts/display.py --stats

# 显示最近7天的活动
python scripts/display.py --activities --days 7

# 显示特定类型的活动
python scripts/display.py --activities --activity-type running

# 显示最近的每日汇总
python scripts/display.py --daily --days 7

# 显示睡眠记录
python scripts/display.py --sleep --days 7

# 显示体重记录
python scripts/display.py --weight
```

## 数据库结构

工具会在MongoDB中创建以下集合（collection）：

### 1. daily_summary - 每日汇总
```javascript
{
  calendarDate: "2024-01-01",
  totalSteps: 10000,
  totalDistance: 8000,  // 米
  activeCalories: 500,
  totalCalories: 2200,
  restingHeartRate: 60,
  sleepTimeSeconds: 28800,
  // ... 更多字段
}
```

### 2. activities - 活动记录
```javascript
{
  activityId: 123456789,
  activityName: "晨跑",
  activityType: "running",
  startTimeGMT: "2024-01-01T06:00:00Z",
  duration: 3600,
  distance: 10000,  // 米
  calories: 600,
  averageHR: 150,
  // ... 更多字段
}
```

### 3. sleep - 睡眠记录
```javascript
{
  calendarDate: "2024-01-01",
  sleepTimeSeconds: 28800,
  deepSleepSeconds: 7200,
  lightSleepSeconds: 18000,
  remSleepSeconds: 3600,
  averageHeartRate: 55,
  // ... 更多字段
}
```

### 4. weight - 体重记录
```javascript
{
  date: "2024-01-01",
  weight: 70.5,  // 公斤
  bmi: 22.5,
  bodyFat: 15.0,  // 百分比
  // ... 更多字段
}
```

### 5. resting_heart_rate - 静息心率
```javascript
{
  calendarDate: "2024-01-01",
  restingHeartRate: 60
}
```

### 6. monitoring - 监控数据（实时数据，如果下载）
```javascript
{
  timestamp: ISODate("2024-01-01T12:00:00Z"),
  heart_rate: 75,
  steps: 5000,
  calories: 250
  // ... 更多字段
}
```

## 日志文件

所有操作都会生成日志文件，位于garmin目录下：

- `download_all.log` - 下载所有数据的日志
- `update.log` - 增量更新的日志
- `import_data.log` - 数据导入的日志
- `display.log` - 数据展示的日志

## 定期自动更新

您可以设置cron任务来定期自动更新数据：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨2点更新）
0 2 * * * cd /home/wangyuanchun/myFitness/data/garmin && /usr/bin/python3 scripts/update.py >> update_cron.log 2>&1
```

## 故障排除

### 1. 无法连接到MongoDB
- 确保MongoDB服务正在运行：`sudo systemctl status mongodb`
- 检查配置文件中的MongoDB连接信息

### 2. Garmin登录失败
- 检查用户名和密码是否正确
- 确保网络连接正常
- 删除会话文件 `mydata/.garmin_session` 后重试

### 3. 数据下载缓慢
- 首次下载所有历史数据可能需要较长时间，请耐心等待
- 之后使用增量更新会快很多

### 4. 导入数据时出错
- 检查MongoDB是否有足够的磁盘空间
- 查看日志文件了解详细错误信息

## 参考资料

本工具参考了以下优秀项目：
- [GarminDB](https://github.com/tcgoetz/GarminDB) - 使用SQLite的Garmin数据处理工具
- [Garth](https://github.com/matin/garth) - Garmin Connect API客户端

## 许可证

本项目仅供个人学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请通过GitHub Issues联系。

