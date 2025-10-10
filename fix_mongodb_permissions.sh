#!/bin/bash
# 修复MongoDB权限问题

echo "================================"
echo "修复MongoDB权限和启动"
echo "================================"

echo "步骤1: 修复数据目录权限..."
chmod -R 755 /home/wangyuanchun/myCoach/data/garmin/mydata/
chmod -R 755 /var/log/mongodb/

echo "步骤2: 修改MongoDB服务配置（以root运行）..."
cat > /etc/systemd/system/mongod.service <<'EOF'
[Unit]
Description=MongoDB Database Server
After=network-online.target

[Service]
User=root
Group=root
Type=forking
ExecStart=/usr/local/bin/mongod --config /etc/mongod.conf --fork
ExecStop=/usr/local/bin/mongod --shutdown --config /etc/mongod.conf
PIDFile=/home/wangyuanchun/myCoach/data/garmin/mydata/mongod.lock
Restart=always

[Install]
WantedBy=multi-user.target
EOF

echo "步骤3: 更新配置文件路径..."
cat > /etc/mongod.conf <<'EOF'
storage:
  dbPath: /home/wangyuanchun/myCoach/data/garmin/mydata
  journal:
    enabled: true
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongod.log
net:
  port: 27017
  bindIp: 0.0.0.0
processManagement:
  timeZoneInfo: /usr/share/zoneinfo
EOF

echo "步骤4: 重新加载systemd..."
systemctl daemon-reload

echo "步骤5: 启动MongoDB..."
systemctl start mongod
systemctl enable mongod

sleep 3

echo ""
echo "步骤6: 检查状态..."
if systemctl is-active --quiet mongod; then
    echo ""
    echo "✓ MongoDB启动成功！"
    echo ""
    systemctl status mongod
    echo ""
    echo "监听端口:"
    netstat -tuln | grep 27017
    echo ""
    echo "服务器IP:"
    hostname -I | awk '{print $1}'
    echo ""
    echo "MongoDB Compass连接字符串:"
    echo "  mongodb://$(hostname -I | awk '{print $1}'):27017/"
    echo ""
else
    echo ""
    echo "✗ MongoDB启动失败"
    echo ""
    echo "查看错误:"
    journalctl -xeu mongod.service -n 20
    echo ""
fi

