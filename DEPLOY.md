# 🚀 一键部署指南 - 奇点量化平台

## ✅ 已完成配置

- [x] Git 仓库初始化
- [x] 部署配置文件创建 (Procfile, railway.toml, render.yaml)
- [x] .gitignore 配置（保护敏感信息）
- [x] Railway CLI 安装

---

## 📋 部署方式对比

| 方式 | 适合 | 部署命令 |
|------|------|----------|
| **Railway** | 快速测试/演示 | `railway up` |
| **Render** | 长期运行 | GitHub 自动部署 |
| **本地运行** | 开发调试 | `python dashboard.py` |

---

## 🎯 方案 1：Railway 一键部署（最快）

### 步骤 1：推送到 GitHub

```bash
cd C:\Users\huangruiran\ai_test

# 在 GitHub 上创建新仓库，然后：
git remote add origin https://github.com/你的用户名/quant-platform.git
git branch -M main
git push -u origin main
```

### 步骤 2：登录 Railway

```bash
railway login
```

浏览器会自动打开，用 GitHub 账号登录。

### 步骤 3：部署

```bash
railway up
```

选择：
1. `Deploy from GitHub repo`
2. 选择你的仓库 `quant-platform`

### 步骤 4：设置环境变量

在 Railway 控制台添加：

```
AZURE_OPENAI_KEY=你的密钥
AZURE_OPENAI_ENDPOINT=你的端点
GOOGLE_APPLICATION_CREDENTIALS=你的凭证
```

### 步骤 5：获取访问地址

```bash
railway domain
```

得到：`https://quant-platform.railway.app`

---

## 🎯 方案 2：Render 自动部署

### 步骤 1：访问 Render

前往 https://render.com 并用 GitHub 登录

### 步骤 2：创建 Web Service

1. 点击 `New +` → `Web Service`
2. 选择你的仓库 `quant-platform`
3. 配置：
   - **Build Command**: `pip install -r requirements_gcp.txt`
   - **Start Command**: `python main.py`
4. 添加环境变量（同上）
5. 点击 `Create Web Service`

### 步骤 3：自动部署

以后每次 `git push` 都会自动部署！

---

## 🎯 方案 3：本地运行（开发模式）

### 启动量化终端

```bash
cd C:\Users\huangruiran\ai_test
python dashboard.py
```

或双击：
```
Launch_Dashboard.bat
```

---

## ⚡ 快速命令参考

```bash
# 安装 Railway CLI（已完成）
npm i -g @railway/cli

# 登录
railway login

# 查看项目状态
railway status

# 部署
railway up

# 查看日志
railway logs

# 设置环境变量
railway variables set KEY=value

# 绑定自定义域名
railway domain add your-domain.com
```

---

## 🔐 安全提醒

以下文件已被 .gitignore 保护，**不会被上传**：

- `.env` - 环境变量
- `singularity_key` - API 密钥
- `*.log` - 日志文件
- `*.csv` - 数据缓存

部署前请确保在平台设置好环境变量！

---

## 📊 部署后检查清单

- [ ] 环境变量已设置
- [ ] 网站可以访问
- [ ] 日志无错误
- [ ] 数据库连接正常
- [ ] API 调用正常

---

## 🆘 故障排除

### 部署失败

```bash
# 查看详细日志
railway logs --lines 100
```

### 本地测试部署

```bash
# 安装依赖
pip install -r requirements_gcp.txt

# 运行
python main.py
```

---

## 🎉 完成！

现在你的量化平台已经部署到云端！

**访问地址**: `https://你的项目.railway.app` 或 `https://你的项目.onrender.com`
