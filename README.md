# Garmin Activity Data Sync Tool

> A sports data management tool designed specifically for China region Garmin users

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/mongodb-6.0+-green.svg)](https://www.mongodb.com/)

**[English](README.md)** | **[中文文档](README_CN.md)**

---

## 📖 Introduction

A MongoDB-based Garmin activity data management tool that automatically downloads all your sports records from Garmin Connect and stores them in a local database.

**Verified Working:** 243 activity records successfully synced ✅

## ✨ Core Features

- ✅ Automatically download all sports records from Garmin Connect
- ✅ MongoDB database storage with powerful query capabilities
- ✅ Support for all activity types (running, swimming, cycling, etc.)
- ✅ Command-line query tools and MongoDB Compass visualization
- ✅ Incremental updates with cron job support

## ⚠️ Important Notes

**China Region API Limitations:**
- ✅ **Activity data** (running, swimming, cycling, etc.): **Fully supported**
- ❌ **Daily summary, sleep, heart rate data**: API returns 403 (not supported)

**Reason:** API endpoint restrictions on Garmin China servers, not a tool issue.

**International users:** Set `"domain": "garmin.com"` for full functionality.

## 🚀 Quick Start

### Requirements

- Python 3.8+
- MongoDB 6.0+
- Linux/MacOS

### Installation Steps

#### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Install MongoDB

**Use provided script (recommended):**
```bash
sudo bash install_mongodb_offline.sh
```

If permission issues occur:
```bash
sudo bash fix_mongodb_permissions.sh
```

**Verify MongoDB is running:**
```bash
sudo systemctl status mongod
netstat -tuln | grep 27017
```

#### 3. Configure Garmin Account

```bash
# Copy example config
cp config/garmin_config.json.example config/garmin_config.json

# Edit configuration
nano config/garmin_config.json
```

**China region configuration:**
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

**International users:** Change domain to `"garmin.com"`

#### 4. Fix Data Directory Permissions

```bash
sudo chown -R $USER:$USER ./mydata/
```

#### 5. Download and Import Data

```bash
# Download data
python scripts/download_all.py

# Import to MongoDB (use fixed import script)
python standalone_import.py
```

#### 6. View Data

```bash
python scripts/display.py --activities
```

## 💡 Usage

### Daily Updates

```bash
# Download latest activities
python scripts/download_all.py

# Import to MongoDB
python standalone_import.py
```

### Query Activities

```bash
# View all activities
python scripts/display.py --activities

# View running records
python scripts/display.py --activities --activity-type running

# View swimming records
python scripts/display.py --activities --activity-type lap_swimming

# View cycling records
python scripts/display.py --activities --activity-type cycling

# View last 30 days
python scripts/display.py --activities --days 30

# View statistics
python scripts/display.py --stats
```

### Using MongoDB Compass

**Connection string:**
- Local: `mongodb://localhost:27017/`
- Remote: `mongodb://server_ip:27017/`

**Database:** `garmin_health`  
**Collection:** `activities`

## 📊 Data Analysis Examples

### Statistics by Activity Type

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['garmin_health']

# Statistics by type
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
    print(f"{result['_id']}: {result['count']} times, {distance_km:.2f}km")
```

### Query Recent Running

```python
# Last 10 running activities
running = list(
    db.activities.find({'activityType': 'running'})
    .sort('startTimeGMT', -1)
    .limit(10)
)

for activity in running:
    name = activity['activityName']
    distance = activity['distance'] / 1000
    duration = activity['duration'] / 60
    print(f"{name}: {distance:.2f}km, {duration:.1f}min")
```

### Export to CSV

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

## 🔧 Troubleshooting

### Q: Why only activity data?

**A:** China region Garmin has disabled these APIs (return 403):
- `/usersummary-service/` - Daily summary
- `/wellness-service/` - Sleep data
- `/userstats-service/` - Resting heart rate

This is a server restriction, not a tool issue.

### Q: Data fields are null?

**A:** Use the fixed import script:
```bash
python standalone_import.py
```

This script correctly parses both summary and details file formats.

### Q: MongoDB connection failed?

**A:**
```bash
# Check MongoDB status
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod
```

### Q: Garmin login failed?

**A:**
- China users: ensure domain is `garmin.cn`
- Check username and password
- Delete session file: `rm mydata/.garmin_session`

### Q: Permission error?

**A:**
```bash
sudo chown -R $USER:$USER ./mydata/
chmod -R 755 ./mydata/
```

### Q: How to setup scheduled updates?

**A:**
```bash
crontab -e

# Daily update at 2 AM
0 2 * * * cd /path/to/garmin && python3 scripts/download_all.py && python3 standalone_import.py >> cron.log 2>&1
```

## 📁 Project Structure

```
garmin/
├── config/                        # Configuration module
│   ├── garmin_config.json.example # Config example
│   └── garmin_config_manager.py   # Config manager
├── db/                            # Database module
│   ├── mongodb_client.py          # MongoDB client
│   └── models.py                  # Data models
├── utils/                         # Utilities
│   ├── download_utils.py          # Download tool
│   └── import_utils.py            # Import tool
├── scripts/                       # Executable scripts
│   ├── download_all.py            # Download data
│   ├── display.py                 # Query and display
│   ├── import_data.py             # Import data
│   └── update.py                  # Incremental update
├── mydata/                        # Data directory (auto-created)
│   ├── activities/                # Activity JSON files
│   ├── weight/                    # Weight data
│   └── fit/                       # User info
├── standalone_import.py           # ⭐Standalone import script (recommended)
├── install_mongodb_offline.sh    # MongoDB installation
├── fix_mongodb_permissions.sh    # Permission fix
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT License
├── README.md                      # English docs (this file)
└── README_CN.md                   # Chinese docs
```

## 🔑 Key Technical Points

### 1. China Region Domain

```json
{
    "garmin": {
        "domain": "garmin.cn"
    }
}
```

**Note:** Not `garmin.com` or `garmin.com.cn`

### 2. SSL Certificate Handling

Code automatically handles China region SSL certificate issues.

### 3. Data File Formats

Tool automatically recognizes two formats:
- **summary files**: Data at root level
- **details files**: Data in `summaryDTO` object

### 4. Deduplication

Uses MongoDB unique index on `activityId`

## 🎯 Test Results

**Test Environment:**
- OS: Ubuntu 24.04
- Python: 3.10 (conda environment)
- MongoDB: 6.0.12
- Garmin Region: China (garmin.cn)

**Successfully Synced:**
- ✅ 243 sports records
- ✅ Multiple types including running, swimming, cycling
- ✅ All data fields complete

**Supported Activity Types:**
- running
- lap_swimming
- cycling
- walking
- hiking
- and more...

## 🛠️ Technology Stack

- **Python 3.8+**: Programming language
- **MongoDB 6.0+**: Data storage
- **pymongo**: MongoDB driver
- **garth**: Garmin API client
- **tqdm**: Progress bar

## 🤝 Contributing

Contributions welcome!

**Especially welcome:**
- Discovery of other accessible China region APIs
- Code optimization and bug fixes
- Documentation improvements
- Usage feedback

**How to contribute:**
1. Fork the project
2. Create a feature branch
3. Submit a Pull Request

## 📄 License

MIT License - For personal learning and research use only.

Please comply with Garmin Connect's terms of service when using this tool.

## 🙏 Acknowledgments

This project is inspired by:
- [GarminDB](https://github.com/tcgoetz/GarminDB) - SQLite-based Garmin tool
- [Garth](https://github.com/matin/garth) - Garmin API client

---

## Quick Command Reference

```bash
# Download data
python scripts/download_all.py

# Import to MongoDB (recommended)
python standalone_import.py

# View activities
python scripts/display.py --activities

# View statistics
python scripts/display.py --stats

# MongoDB connection
mongodb://localhost:27017/
```

---

**⭐ If this project helps you, please give it a Star!**

**Happy exercising!** 🏃‍♂️🏊‍♂️🚴‍♂️
