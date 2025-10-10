#!/bin/bash
# 允许MongoDB远程访问配置脚本

echo "================================"
echo "MongoDB远程访问配置"
echo "================================"

if [ "$EUID" -ne 0 ]; then 
    echo "请使用root权限运行: sudo bash $0"
    exit 1
fi

echo ""
echo "选择配置方式："
echo "1) 允许所有IP访问（开发环境，不安全）"
echo "2) 只允许特定IP访问（推荐）"
echo "3) 启用认证（最安全）"
echo ""
read -p "请选择 [1-3]: " choice

case $choice in
    1)
        echo "配置为允许所有IP访问..."
        sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf
        ;;
    2)
        read -p "请输入允许访问的IP地址: " client_ip
        sed -i "s/bindIp: 127.0.0.1/bindIp: 127.0.0.1,$client_ip/" /etc/mongod.conf
        echo "已允许 $client_ip 访问"
        ;;
    3)
        echo "启用认证模式..."
        read -p "请输入管理员用户名 [admin]: " admin_user
        admin_user=${admin_user:-admin}
        read -sp "请输入管理员密码: " admin_pass
        echo ""
        
        # 修改bindIp
        sed -i 's/bindIp: 127.0.0.1/bindIp: 0.0.0.0/' /etc/mongod.conf
        
        # 添加认证配置
        if ! grep -q "authorization: enabled" /etc/mongod.conf; then
            echo "security:" >> /etc/mongod.conf
            echo "  authorization: enabled" >> /etc/mongod.conf
        fi
        
        # 创建用户
        echo "创建管理员用户..."
        mongosh admin --eval "db.createUser({user: '$admin_user', pwd: '$admin_pass', roles: ['root']})" 2>/dev/null
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac

echo ""
echo "重启MongoDB..."
systemctl restart mongod
sleep 2

if systemctl is-active --quiet mongod; then
    echo ""
    echo "✓ 配置成功！"
    echo ""
    echo "MongoDB监听状态:"
    netstat -tuln | grep 27017
    echo ""
    echo "获取服务器IP:"
    echo "  hostname -I | awk '{print \$1}'"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "  服务器IP: $SERVER_IP"
    echo ""
    echo "MongoDB Compass连接字符串:"
    if [ "$choice" = "3" ]; then
        echo "  mongodb://${admin_user}:${admin_pass}@${SERVER_IP}:27017/?authSource=admin"
    else
        echo "  mongodb://${SERVER_IP}:27017/"
    fi
    echo ""
    echo "注意事项:"
    echo "  1. 确保防火墙允许27017端口"
    echo "  2. 如果使用云服务器，需要在安全组开放27017端口"
    echo "  3. 生产环境强烈建议启用认证"
    echo ""
else
    echo ""
    echo "✗ MongoDB启动失败"
    echo "查看日志: journalctl -u mongod -n 50"
    echo ""
fi

