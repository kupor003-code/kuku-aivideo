#!/bin/bash

echo "🚀 AI Video Platform - GitHub 推送工具"
echo "======================================"
echo ""

# 检查是否在项目目录
if [ ! -d ".git" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

echo "📋 请按以下步骤操作："
echo ""
echo "1. 打开这个链接创建 Token："
echo "   https://github.com/settings/tokens/new"
echo ""
echo "2. 配置 Token："
echo "   - Note: kuku-aivideo"
echo "   - Expiration: No expiration"
echo "   - 勾选: repo (Full control)"
echo "   - 点击: Generate token"
echo ""
echo "3. 复制 Token（只显示一次！）"
echo ""

# 读取 token
read -p "🔑 请粘贴你的 GitHub Token: " token

# 检查 token 不为空
if [ -z "$token" ]; then
    echo "❌ Token 不能为空"
    exit 1
fi

echo ""
echo "⏳ 正在推送到 GitHub..."
echo ""

# 推送代码，使用 token
git push -u origin main 2>&1 | head -20

# 检查推送是否成功
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "🌉 你的项目已部署到 GitHub："
    echo "   https://github.com/kupor003-code/kuku-aivideo"
    echo ""
else
    echo ""
    echo "❌ 推送失败，请检查："
    echo "   1. Token 是否正确"
    echo "   2. 网络连接是否正常"
    echo "   3. 仓库名称是否正确"
fi
