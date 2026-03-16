# 🚀 GitHub 部署指南

## 📋 准备工作

✅ Git 仓库已初始化
✅ 第一次提交已完成
✅ .gitignore 已配置（敏感文件已排除）

## 🌐 创建 GitHub 仓库

### 方法1: 通过 GitHub 网页创建（推荐）

1. **登录 GitHub**
   - 访问 [https://github.com](https://github.com)
   - 登录你的账号

2. **创建新仓库**
   - 点击右上角 `+` → `New repository`
   - 仓库名称：`ai-video-platform`
   - 描述：`AI-powered video creation platform with automatic storyboard, image, and video generation`
   - 选择 `Public` 或 `Private`
   - ⚠️ **不要**勾选：
     - ❌ Add a README file（我们已经有了）
     - ❌ Add .gitignore（我们已经有了）
     - ❌ Choose a license（可以选择MIT）
   - 点击 `Create repository`

3. **获取仓库地址**
   - 创建后会显示仓库地址
   - 选择 HTTPS：`https://github.com/你的用户名/ai-video-platform.git`

## 🔗 连接本地仓库到 GitHub

### 在项目目录执行命令

```bash
cd /Users/kupor/Desktop/ai-video-platform

# 添加 GitHub 远程仓库
git remote add origin https://github.com/你的用户名/ai-video-platform.git

# 验证远程仓库
git remote -v

# 推送代码到 GitHub
git push -u origin main
```

### 如果出现认证错误

使用 GitHub Personal Access Token：

1. **生成 Token**
   - 访问：https://github.com/settings/tokens
   - 点击 `Generate new token` → `Generate new token (classic)`
   - 勾选权限：
     - ✅ `repo`（完整仓库访问权限）
   - 点击 `Generate token`
   - **复制 token**（只显示一次！）

2. **使用 Token 推送**
   ```bash
   # 推送时会提示输入用户名和密码
   # 用户名：输入你的 GitHub 用户名
   # 密码：粘贴刚才生成的 token（不是 GitHub 密码）
   git push -u origin main
   ```

### 或者配置 SSH（更方便）

```bash
# 1. 生成 SSH key（如果还没有）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 添加到 GitHub
#    - 访问：https://github.com/settings/keys
#    - 点击 `New SSH key`
#    - 粘贴公钥内容
#    - 点击 `Add SSH key`

# 4. 修改远程仓库地址为 SSH
git remote set-url origin git@github.com:你的用户名/ai-video-platform.git

# 5. 推送
git push -u origin main
```

## 📝 后续推送

推送代码更新到 GitHub：

```bash
# 查看修改状态
git status

# 添加所有修改
git add .

# 提交修改
git commit -m "描述你的修改"

# 推送到 GitHub
git push
```

## 🎯 验证部署

1. **访问你的仓库**
   ```
   https://github.com/你的用户名/ai-video-platform
   ```

2. **检查文件**
   - README.md ✅
   - backend/ ✅
   - frontend/ ✅
   - .gitignore ✅

3. **查看代码**
   - 点击任意文件查看内容
   - 确认代码已正确上传

## 🔄 克隆到其他电脑

在其他电脑上获取项目：

```bash
# 使用 HTTPS
git clone https://github.com/你的用户名/ai-video-platform.git

# 或使用 SSH（如果已配置）
git clone git@github.com:你的用户名/ai-video-platform.git

# 进入项目目录
cd ai-video-platform

# 安装后端依赖
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API keys

# 安装前端依赖
cd ../frontend
npm install

# 配置前端环境变量
cp .env.example .env
# 已自动配置好 API_URL
```

## 🌟 GitHub Page（可选）

如果想在 GitHub Pages 上部署前端：

1. **在 `frontend/vite.config.ts` 添加 base**
   ```typescript
   export default defineConfig({
     plugins: [react()],
     base: '/ai-video-platform/', // 你的仓库名
   })
   ```

2. **构建前端**
   ```bash
   cd frontend
   npm run build
   ```

3. **推送到 GitHub**
   ```bash
   git add frontend/dist
   git commit -m "Add production build"
   git push
   ```

4. **在 GitHub 启用 Pages**
   - 仓库 → `Settings` → `Pages`
   - Source: 选择 `Deploy from a branch`
   - Branch: `main` / `root`
   - 点击 `Save`

## 📊 README 徽章（可选）

在 README.md 顶部添加项目状态徽章：

```markdown
![GitHub stars](https://img.shields.io/github/stars/你的用户名/ai-video-platform)
![GitHub forks](https://img.shields.io/github/forks/你的用户名/ai-video-platform)
![GitHub issues](https://img.shields.io/github/issues/你的用户名/ai-video-platform)
![License](https://img.shields.io/github/license/你的用户名/ai-video-platform)
```

## 🔐 安全检查清单

上传到 GitHub 前，确认以下内容：

- ✅ `.env` 文件在 .gitignore 中
- ✅ `venv/` 目录被忽略
- ✅ `node_modules/` 被忽略
- ✅ `*.db` 数据库文件被忽略
- ✅ 没有提交 API keys
- ✅ 没有提交敏感信息

检查方法：
```bash
# 查看将被追踪的文件
git ls-files

# 搜索是否包含敏感信息
git grep "sk-" . || echo "✅ 未发现 API key"
git grep "SECRET" . || echo "✅ 未发现 SECRET"
```

## 🎉 完成！

现在你的项目已经成功部署到 GitHub 了！

**仓库地址**：`https://github.com/你的用户名/ai-video-platform`

你可以：
- 📤 分享给其他人
- 🤝 接受 Pull Request
- 🌟 展示你的作品
- 📝 使用 Issues 追踪 bug

---

**祝您使用愉快！** 🚀
