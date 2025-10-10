# 项目架构说明

## 概述

本项目是一个基于MongoDB的Garmin健康数据同步工具，采用模块化设计，便于扩展和维护。

## 技术栈

- **Python 3.8+**: 主要编程语言
- **MongoDB**: 数据存储
- **pymongo**: MongoDB Python驱动
- **garth**: Garmin Connect API客户端
- **tqdm**: 进度条显示

## 项目结构

```
garmin/
├── __init__.py                 # 包初始化文件
├── config/                     # 配置模块
│   ├── __init__.py
│   ├── garmin_config.json.example  # 配置文件示例
│   └── garmin_config_manager.py    # 配置管理器
│       - 负责读取和管理配置
│       - 提供配置访问接口
│       - 自动创建必要的目录
│
├── db/                         # 数据库模块
│   ├── __init__.py
│   ├── mongodb_client.py       # MongoDB客户端
│   │   - 管理数据库连接
│   │   - 提供数据CRUD操作
│   │   - 创建和管理索引
│   │   - 提供统计和查询方法
│   └── models.py               # 数据模型
│       - 定义各种健康数据的结构
│       - 提供数据转换方法（JSON -> MongoDB文档）
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── download_utils.py       # 下载工具
│   │   - 管理Garmin Connect登录
│   │   - 下载各类健康数据
│   │   - 保存数据为JSON文件
│   └── import_utils.py         # 导入工具
│       - 读取JSON文件
│       - 转换数据格式
│       - 导入到MongoDB
│
├── scripts/                    # 可执行脚本
│   ├── __init__.py
│   ├── setup.py                # 交互式配置脚本
│   ├── download_all.py         # 下载所有历史数据
│   ├── update.py               # 增量更新（下载+导入）
│   ├── import_data.py          # 导入数据到MongoDB
│   └── display.py              # 查询和展示数据
│
├── mydata/                     # 数据存储目录（自动创建）
│   ├── .garmin_session         # Garmin会话文件
│   ├── fit/                    # FIT文件和用户配置
│   ├── activities/             # 活动数据JSON
│   ├── daily_summary/          # 每日汇总JSON
│   ├── sleep/                  # 睡眠数据JSON
│   ├── weight/                 # 体重数据JSON
│   └── rhr/                    # 静息心率JSON
│
├── requirements.txt            # Python依赖
├── .gitignore                  # Git忽略文件
├── README.md                   # 项目主文档
├── QUICKSTART.md              # 快速开始指南
├── EXAMPLES.md                # 使用示例
└── ARCHITECTURE.md            # 本文件
```

## 核心模块详解

### 1. 配置模块 (config/)

**GarminConfigManager**
- 职责：管理所有配置项
- 功能：
  - 读取JSON配置文件
  - 提供配置访问方法
  - 自动创建必要的目录
  - 设置日志级别

**配置文件结构**
```json
{
    "mongodb": {...},           # MongoDB连接配置
    "garmin": {...},           # Garmin域名配置
    "credentials": {...},      # 登录凭证
    "data": {...},            # 数据起始日期
    "directories": {...},     # 数据目录配置
    "enabled_stats": {...},   # 功能开关
    "settings": {...}         # 其他设置
}
```

### 2. 数据库模块 (db/)

**MongoDBClient**
- 职责：管理MongoDB连接和数据操作
- 功能：
  - 连接管理和自动重连
  - 创建和管理索引
  - 数据插入和更新（支持upsert）
  - 数据查询和统计
  - 日期范围查询

**数据集合（Collections）**
- `daily_summary`: 每日汇总数据
- `activities`: 活动记录
- `sleep`: 睡眠记录
- `weight`: 体重记录
- `resting_heart_rate`: 静息心率
- `monitoring`: 监控数据（可选）

**models**
- 定义数据模型
- 提供数据转换静态方法
- 标准化数据格式

### 3. 工具模块 (utils/)

**GarminDownloader**
- 职责：从Garmin Connect下载数据
- 功能：
  - 登录和会话管理
  - 下载各类健康数据
  - 保存为JSON文件
  - 错误处理和重试

**支持的数据类型**
- 每日汇总 (Daily Summary)
- 睡眠数据 (Sleep)
- 体重数据 (Weight)
- 静息心率 (Resting Heart Rate)
- 活动列表和详情 (Activities)
- FIT文件 (可选)

**DataImporter**
- 职责：将JSON数据导入MongoDB
- 功能：
  - 批量读取JSON文件
  - 数据格式转换
  - 批量导入MongoDB
  - 进度显示和统计

### 4. 脚本模块 (scripts/)

**setup.py**
- 交互式配置向导
- 帮助用户快速设置

**download_all.py**
- 下载所有历史数据
- 适合首次使用

**update.py**
- 下载最新数据并导入
- 适合日常更新

**import_data.py**
- 将下载的JSON导入MongoDB
- 可单独运行

**display.py**
- 查询和展示数据
- 支持多种过滤选项

## 数据流程

### 下载流程

```
用户 -> download_all.py
  -> GarminDownloader.login()
  -> GarminDownloader.download_all_data()
    -> 调用各类数据下载方法
      -> 保存JSON到mydata/目录
```

### 导入流程

```
用户 -> import_data.py
  -> MongoDBClient.connect()
  -> DataImporter.import_all_data()
    -> 读取JSON文件
    -> 转换为MongoDB文档格式
      -> MongoDBClient.insert_*()
        -> 写入MongoDB
```

### 更新流程

```
用户 -> update.py
  -> 下载最新数据 (download_all_data(latest=True))
  -> 导入到MongoDB (import_all_data())
  -> 显示统计信息
```

## 设计特点

### 1. 模块化设计
- 各模块职责清晰
- 低耦合高内聚
- 易于测试和维护

### 2. 配置驱动
- 所有配置集中管理
- 易于定制和扩展
- 支持多环境配置

### 3. 数据持久化
- JSON文件作为中间存储
- MongoDB作为最终存储
- 可重复导入，不丢失数据

### 4. 错误处理
- 完善的异常处理
- 详细的日志记录
- 用户友好的错误提示

### 5. 增量更新
- 支持增量下载
- 避免重复下载
- 提高更新效率

### 6. 可扩展性
- 易于添加新的数据类型
- 支持自定义数据处理
- 可集成到其他系统

## MongoDB数据模型

### 索引策略

每个集合都创建了合适的索引：

- **activities**: 
  - activityId (unique)
  - startTimeGMT (desc)
  - activityType

- **daily_summary**:
  - calendarDate (unique, desc)

- **sleep**:
  - calendarDate (desc)
  - sleepStartTimestampGMT (desc)

- **weight**:
  - date (desc)

- **resting_heart_rate**:
  - calendarDate (desc)

### 数据一致性

- 使用upsert保证数据不重复
- 唯一索引防止重复插入
- 时间戳记录数据创建时间

## 安全考虑

1. **凭证保护**
   - 配置文件不提交到git
   - 支持密码文件存储
   - 会话文件加密存储

2. **数据隐私**
   - 数据存储在本地
   - 不上传到第三方服务器
   - 用户完全控制数据

3. **错误恢复**
   - 完整的日志记录
   - 失败可重试
   - 数据不会丢失

## 性能优化

1. **批量操作**
   - 批量插入数据
   - 减少数据库连接次数

2. **索引优化**
   - 关键字段建立索引
   - 优化查询性能

3. **增量更新**
   - 只下载最新数据
   - 减少网络传输

4. **进度显示**
   - 使用tqdm显示进度
   - 用户体验友好

## 扩展建议

### 1. 添加新数据类型
1. 在 `download_utils.py` 添加下载方法
2. 在 `models.py` 添加数据模型
3. 在 `mongodb_client.py` 添加数据库操作
4. 在 `import_utils.py` 添加导入逻辑

### 2. 数据分析功能
- 创建新的分析脚本
- 使用MongoDB聚合框架
- 集成数据可视化库

### 3. Web界面
- 使用Flask/Django创建Web应用
- 提供数据可视化界面
- 支持在线查询和分析

### 4. 数据导出
- 导出为CSV/Excel
- 生成PDF报告
- 同步到其他平台

## 测试建议

### 单元测试
```python
# 测试配置管理器
def test_config_manager():
    config = GarminConfigManager()
    assert config.get_database_name() == "garmin_health"

# 测试数据模型
def test_activity_model():
    data = {...}
    activity = ActivityData.from_json_data(data)
    assert activity['activityId'] is not None
```

### 集成测试
- 测试完整的下载-导入流程
- 测试数据库操作
- 测试查询功能

## 故障排除

### 常见问题定位

1. **配置问题**: 检查 `garmin_config.json`
2. **连接问题**: 检查网络和MongoDB状态
3. **数据问题**: 查看日志文件
4. **性能问题**: 检查索引和查询语句

### 日志级别

配置中可设置日志级别：
- DEBUG: 详细调试信息
- INFO: 一般信息（推荐）
- WARNING: 警告信息
- ERROR: 错误信息

## 维护建议

1. **定期备份**: 定期备份MongoDB数据
2. **日志清理**: 定期清理旧日志文件
3. **版本更新**: 及时更新依赖包
4. **监控运行**: 监控定时任务执行状态

## 总结

本项目采用清晰的模块化设计，将数据下载、存储、查询等功能分离，使得代码易于理解、维护和扩展。通过MongoDB存储数据，既保证了查询性能，又提供了灵活的数据分析能力。

