#!/bin/bash
# MongoDB离线安装脚本

echo "================================"
echo "MongoDB 离线安装脚本"
echo "================================"

# 检查是否在root权限下
if [ "$EUID" -ne 0 ]; then 
    echo "请使用root权限运行: sudo bash $0"
    exit 1
fi

# MongoDB版本
MONGO_VERSION="6.0.12"
MONGO_TAR="mongodb-linux-x86_64-ubuntu2204-${MONGO_VERSION}.tgz"
MONGO_URL="https://fastdl.mongodb.org/linux/${MONGO_TAR}"

echo "步骤1: 下载MongoDB..."
cd /tmp

if [ -f "${MONGO_TAR}" ]; then
    echo "MongoDB压缩包已存在，跳过下载"
else
    echo "正在下载MongoDB ${MONGO_VERSION}..."
    echo "如果下载失败，请手动下载并放到 /tmp/ 目录："
    echo "  下载地址: ${MONGO_URL}"
    echo ""
    
    wget "${MONGO_URL}"
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "✗ 自动下载失败"
        echo ""
        echo "请手动下载MongoDB:"
        echo "  1. 访问: https://www.mongodb.com/try/download/community"
        echo "  2. 选择版本: ${MONGO_VERSION}"
        echo "  3. 选择平台: Ubuntu 22.04 x64"
        echo "  4. 下载.tgz文件"
        echo "  5. 上传到服务器的 /tmp/ 目录"
        echo "  6. 重新运行此脚本"
        echo ""
        exit 1
    fi
fi

echo "步骤2: 解压MongoDB..."
tar -zxf "${MONGO_TAR}"

MONGO_DIR="mongodb-linux-x86_64-ubuntu2204-${MONGO_VERSION}"

if [ ! -d "${MONGO_DIR}" ]; then
    echo "✗ 解压失败"
    exit 1
fi

echo "步骤3: 安装MongoDB..."
# 如果已存在，先删除
rm -rf /usr/local/mongodb
mv "${MONGO_DIR}" /usr/local/mongodb

# 创建符号链接
ln -sf /usr/local/mongodb/bin/* /usr/local/bin/

echo "步骤4: 创建必要的目录..."
mkdir -p /home/wangyuanchun/mongodb_data
mkdir -p /var/log/mongodb
chown -R wangyuanchun:wangyuanchun /home/wangyuanchun/mongodb_data
chown -R wangyuanchun:wangyuanchun /var/log/mongodb

echo "步骤5: 创建配置文件..."
cat > /etc/mongod.conf <<'EOF'
storage:
  dbPath: /home/wangyuanchun/mongodb_data
  journal:
    enabled: true
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
net:
  port: 27017
  bindIp: 127.0.0.1
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
EOF

echo "步骤6: 创建systemd服务..."
cat > /etc/systemd/system/mongod.service <<'EOF'
[Unit]
Description=MongoDB Database Server
Documentation=https://docs.mongodb.org/manual
After=network-online.target
Wants=network-online.target

[Service]
User=wangyuanchun
Group=wangyuanchun
Type=forking
ExecStart=/usr/local/bin/mongod --config /etc/mongod.conf --fork
ExecStop=/usr/local/bin/mongod --shutdown --config /etc/mongod.conf
PIDFile=/home/wangyuanchun/mongodb_data/mongod.lock
LimitNOFILE=64000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "步骤7: 启动MongoDB服务..."
systemctl daemon-reload
systemctl start mongod
systemctl enable mongod

sleep 3

echo "步骤8: 验证安装..."
if systemctl is-active --quiet mongod; then
    echo ""
    echo "================================"
    echo "✓ MongoDB安装成功！"
    echo "================================"
    echo ""
    echo "MongoDB信息:"
    echo "  版本: $(mongod --version | head -n 1)"
    echo "  数据目录: /home/wangyuanchun/mongodb_data"
    echo "  日志文件: /var/log/mongodb/mongod.log"
    echo "  配置文件: /etc/mongod.conf"
    echo "  端口: 27017"
    echo ""
    echo "管理命令:"
    echo "  查看状态: systemctl status mongod"
    echo "  停止服务: systemctl stop mongod"
    echo "  启动服务: systemctl start mongod"
    echo "  重启服务: systemctl restart mongod"
    echo "  查看日志: tail -f /var/log/mongodb/mongod.log"
    echo ""
    echo "连接MongoDB:"
    echo "  mongosh  # MongoDB Shell"
    echo ""
    echo "现在可以运行Garmin数据同步了:"
    echo "  cd ~/myCoach/data/garmin"
    echo "  python scripts/update.py"
    echo ""
else
    echo ""
    echo "✗ MongoDB启动失败"
    echo ""
    echo "请查看日志:"
    echo "  journalctl -u mongod -n 50"
    echo "  tail -f /var/log/mongodb/mongod.log"
    echo ""
fi

