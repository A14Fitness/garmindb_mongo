# 快速开始指南

## 5分钟快速上手

### 步骤1：安装依赖

```bash
# 进入garmin目录
cd /home/wangyuanchun/myFitness/data/garmin

# 安装Python依赖
pip install -r requirements.txt
```

### 步骤2：确保MongoDB运行

```bash
# 检查MongoDB是否运行
sudo systemctl status mongodb

# 如果未运行，启动MongoDB
sudo systemctl start mongodb
```

### 步骤3：配置工具

运行交互式配置脚本：

```bash
python scripts/setup.py
```

按照提示输入：
- MongoDB连接信息（默认localhost:27017可直接回车）
- Garmin Connect用户名和密码
- 数据起始日期

### 步骤4：下载和导入数据

**方法1：一键完成（推荐）**
```bash
python scripts/update.py
```

**方法2：分步执行**
```bash
# 先下载
python scripts/download_all.py

# 再导入
python scripts/import_data.py
```

### 步骤5：查看数据

```bash
# 查看所有数据概览
python scripts/display.py

# 只查看活动
python scripts/display.py --activities

# 查看最近30天的数据
python scripts/display.py --days 30
```

## 常用命令

### 每日更新
```bash
python scripts/update.py
```

### 查看不同类型的数据
```bash
# 数据库统计
python scripts/display.py --stats

# 活动记录
python scripts/display.py --activities --days 7

# 跑步记录
python scripts/display.py --activities --activity-type running

# 每日汇总
python scripts/display.py --daily --days 7

# 睡眠记录
python scripts/display.py --sleep --days 7

# 体重记录
python scripts/display.py --weight
```

## 设置定时任务

编辑crontab：
```bash
crontab -e
```

添加定时任务（每天凌晨2点自动更新）：
```
0 2 * * * cd /home/wangyuanchun/myFitness/data/garmin && /usr/bin/python3 scripts/update.py >> update_cron.log 2>&1
```

## 目录说明

- `config/` - 配置文件（需要自己创建garmin_config.json）
- `db/` - 数据库操作代码
- `utils/` - 工具函数
- `scripts/` - 可执行脚本
- `mydata/` - 下载的数据文件（自动创建）
- `*.log` - 日志文件

## 故障排除

**问题1：配置文件不存在**
```bash
# 运行设置脚本
python scripts/setup.py
```

**问题2：MongoDB连接失败**
```bash
# 检查MongoDB状态
sudo systemctl status mongodb

# 启动MongoDB
sudo systemctl start mongodb
```

**问题3：Garmin登录失败**
- 检查用户名密码是否正确
- 删除会话文件后重试：`rm mydata/.garmin_session`

## 获取帮助

查看详细文档：
```bash
cat README.md
```

查看脚本帮助：
```bash
python scripts/display.py --help
```

## 数据分析

数据存储在MongoDB中，您可以：
1. 使用MongoDB工具直接查询
2. 使用display.py脚本查看
3. 编写自己的Python脚本分析数据
4. 使用Jupyter Notebook进行可视化分析

MongoDB连接示例：
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['garmin_health']

# 查询最近的活动
activities = db.activities.find().sort('startTimeGMT', -1).limit(10)
for activity in activities:
    print(activity['activityName'], activity['distance'])
```

祝您使用愉快！

