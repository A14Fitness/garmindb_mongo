# Garmin活动数据同步工具

> 专为中国区Garmin用户设计的运动数据管理工具

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/mongodb-6.0+-green.svg)](https://www.mongodb.com/)

**[English](README.md)** | **[中文文档](README_CN.md)**

---

## 📖 简介

这是一个基于MongoDB的Garmin运动活动数据管理工具，可以自动从Garmin Connect下载您的所有运动记录并存储到本地数据库。

**已验证可用：** 243个活动记录成功同步 ✅

## ✨ 核心功能

- ✅ 自动从Garmin Connect下载所有运动记录
- ✅ MongoDB数据库存储，支持复杂查询
- ✅ 支持跑步、游泳、骑行等所有运动类型
- ✅ 命令行查询工具和MongoDB Compass可视化
- ✅ 增量更新，支持定时任务

## ⚠️ 重要提示

**中国区API限制：**
- ✅ **活动数据**（running, swimming, cycling等）：**完全可用**
- ❌ **每日汇总、睡眠、心率数据**：API返回403（暂不支持）

**原因：** Garmin中国区服务器的API端点限制，不是工具问题。

**国际版用户：** 配置 `"domain": "garmin.com"` 可使用全部功能。

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MongoDB 6.0+
- Linux/MacOS

### 安装步骤

#### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 2. 安装MongoDB

**使用提供的脚本（推荐）：**
```bash
sudo bash install_mongodb_offline.sh
```

如遇权限问题：
```bash
sudo bash fix_mongodb_permissions.sh
```

**验证MongoDB运行：**
```bash
sudo systemctl status mongod
netstat -tuln | grep 27017
```

#### 3. 配置Garmin账号

```bash
# 复制配置示例
cp config/garmin_config.json.example config/garmin_config.json

# 编辑配置
nano config/garmin_config.json
```

**中国区用户配置：**
```json
{
    "garmin": {
        "domain": "garmin.cn"
    },
    "credentials": {
        "user": "your_email@example.com",
        "password": "your_password"
    }
}
```

**国际版用户：** 将domain改为 `"garmin.com"`

#### 4. 修复数据目录权限

```bash
sudo chown -R $USER:$USER ./mydata/
```

#### 5. 下载并导入数据

```bash
# 下载数据
python scripts/download_all.py

# 导入MongoDB（使用修复版导入脚本）
python standalone_import.py
```

#### 6. 查看数据

```bash
python scripts/display.py --activities
```

## 💡 使用方法

### 日常更新

```bash
# 下载最新活动
python scripts/download_all.py

# 导入到MongoDB
python standalone_import.py
```

### 查询活动

```bash
# 查看所有活动
python scripts/display.py --activities

# 查看跑步记录
python scripts/display.py --activities --activity-type running

# 查看游泳记录
python scripts/display.py --activities --activity-type lap_swimming

# 查看骑行记录
python scripts/display.py --activities --activity-type cycling

# 查看最近30天
python scripts/display.py --activities --days 30

# 查看统计信息
python scripts/display.py --stats
```

### 使用MongoDB Compass

**连接字符串：**
- 本地：`mongodb://localhost:27017/`
- 远程：`mongodb://服务器IP:27017/`

**数据库：** `garmin_health`  
**集合：** `activities`

## 📊 数据分析示例

### 统计各类运动

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['garmin_health']

# 统计各类型运动
pipeline = [
    {'$group': {
        '_id': '$activityType',
        'count': {'$sum': 1},
        'total_distance': {'$sum': '$distance'},
        'total_calories': {'$sum': '$calories'}
    }},
    {'$sort': {'count': -1}}
]

for result in db.activities.aggregate(pipeline):
    distance_km = result['total_distance'] / 1000
    print(f"{result['_id']}: {result['count']}次, {distance_km:.2f}km")
```

### 查询最近跑步

```python
# 最近10次跑步
running = list(
    db.activities.find({'activityType': 'running'})
    .sort('startTimeGMT', -1)
    .limit(10)
)

for activity in running:
    name = activity['activityName']
    distance = activity['distance'] / 1000
    duration = activity['duration'] / 60
    print(f"{name}: {distance:.2f}km, {duration:.1f}分钟")
```

### 导出为CSV

```python
import csv

activities = list(db.activities.find())

with open('activities.csv', 'w', encoding='utf-8', newline='') as f:
    fields = ['activityId', 'activityName', 'activityType', 
              'startTimeGMT', 'distance', 'duration', 'calories']
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    
    for activity in activities:
        row = {field: activity.get(field, '') for field in fields}
        writer.writerow(row)
```

## 🔧 常见问题

### Q: 为什么只有活动数据？

**A:** 中国区Garmin的以下API被禁用（返回403）：
- `/usersummary-service/` - 每日汇总
- `/wellness-service/` - 睡眠数据
- `/userstats-service/` - 静息心率

这是Garmin服务器限制，不是工具问题。

### Q: 数据字段为null怎么办？

**A:** 使用修复版导入脚本：
```bash
python standalone_import.py
```

此脚本能正确解析summary和details两种文件格式。

### Q: MongoDB连接失败？

**A:** 
```bash
# 检查MongoDB状态
sudo systemctl status mongod

# 启动MongoDB
sudo systemctl start mongod
```

### Q: Garmin登录失败？

**A:**
- 中国区确保domain为 `garmin.cn`
- 检查用户名密码是否正确
- 删除会话文件：`rm mydata/.garmin_session`

### Q: 权限错误？

**A:**
```bash
sudo chown -R $USER:$USER ./mydata/
chmod -R 755 ./mydata/
```

### Q: 如何设置定时更新？

**A:**
```bash
crontab -e

# 每天凌晨2点自动更新
0 2 * * * cd /path/to/garmin && python3 scripts/download_all.py && python3 standalone_import.py >> cron.log 2>&1
```

## 📁 项目结构

```
garmin/
├── config/                        # 配置模块
│   ├── garmin_config.json.example # 配置示例
│   └── garmin_config_manager.py   # 配置管理器
├── db/                            # 数据库模块
│   ├── mongodb_client.py          # MongoDB客户端
│   └── models.py                  # 数据模型
├── utils/                         # 工具模块
│   ├── download_utils.py          # 下载工具
│   └── import_utils.py            # 导入工具
├── scripts/                       # 可执行脚本
│   ├── download_all.py            # 下载数据
│   ├── display.py                 # 查询展示
│   ├── import_data.py             # 导入数据
│   └── update.py                  # 增量更新
├── mydata/                        # 数据目录（自动创建）
│   ├── activities/                # 活动JSON文件
│   ├── weight/                    # 体重数据
│   └── fit/                       # 用户信息
├── standalone_import.py           # ⭐独立导入脚本（推荐）
├── install_mongodb_offline.sh    # MongoDB安装脚本
├── fix_mongodb_permissions.sh    # 权限修复脚本
├── requirements.txt               # Python依赖
├── LICENSE                        # MIT许可证
├── README.md                      # 英文文档
└── README_CN.md                   # 中文文档（本文件）
```

## 🔑 关键技术点

### 1. 中国区域名配置

```json
{
    "garmin": {
        "domain": "garmin.cn"
    }
}
```

**注意：** 不是 `garmin.com` 也不是 `garmin.com.cn`

### 2. SSL证书处理

代码已自动处理中国区SSL证书问题，无需手动配置。

### 3. 数据文件格式

工具自动识别两种格式：
- **summary文件**：数据在根级别
- **details文件**：数据在`summaryDTO`对象中

### 4. 去重机制

使用MongoDB唯一索引：`activityId`

## 🎯 实际测试结果

**测试环境：**
- 系统：Ubuntu 24.04
- Python：3.10 (conda环境)
- MongoDB：6.0.12
- Garmin区域：中国区 (garmin.cn)

**成功同步：**
- ✅ 243个运动记录
- ✅ 包含跑步、游泳、骑行等多种类型
- ✅ 所有字段数据完整

**支持的活动类型：**
- running（跑步）
- lap_swimming（泳池游泳）
- cycling（骑行）
- walking（步行）
- hiking（徒步）
- 等等...

## 🛠️ 技术栈

- **Python 3.8+**: 开发语言
- **MongoDB 6.0+**: 数据存储
- **pymongo**: MongoDB驱动
- **garth**: Garmin API客户端
- **tqdm**: 进度条

## 🤝 贡献

欢迎贡献代码和建议！

**特别欢迎：**
- 中国区其他可用API的发现
- 代码优化和Bug修复
- 文档改进
- 使用反馈

**贡献方式：**
1. Fork本项目
2. 创建特性分支
3. 提交Pull Request

## 📄 许可证

MIT License - 仅供个人学习和研究使用。

使用本工具时请遵守Garmin Connect的服务条款。

## 🙏 致谢

本项目参考了：
- [GarminDB](https://github.com/tcgoetz/GarminDB) - SQLite版Garmin工具
- [Garth](https://github.com/matin/garth) - Garmin API客户端

---

## 快速命令参考

```bash
# 下载数据
python scripts/download_all.py

# 导入MongoDB（推荐）
python standalone_import.py

# 查看活动
python scripts/display.py --activities

# 查看统计
python scripts/display.py --stats

# MongoDB连接
mongodb://localhost:27017/
```

---

**⭐ 如果这个项目对您有帮助，请给个Star！**

**祝您运动愉快！** 🏃‍♂️🏊‍♂️🚴‍♂️
