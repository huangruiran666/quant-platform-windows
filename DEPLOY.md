# 🚀 一键部署指南

## 项目类型
Python 量化交易平台（Flask + 数据分析 + AI）

---

## 方案 1：Railway（推荐 ⭐）

### 步骤 1：登录 Railway

```bash
cd C:\Users\huangruiran\ai_test
railway login
```

会打开浏览器，用 **GitHub 账号登录**。

### 步骤 2：初始化项目

```bash
railway init
```

选择：
- `Create new project`
- 输入项目名称（如 `quant-platform`）

### 步骤 3：一键部署

```bash
railway up
```

自动完成：
- ✅ 检测 Python 项目
- ✅ 安装依赖（requirements.txt / pyproject.toml）
- ✅ 构建 Docker 镜像
- ✅ 部署到云端

### 步骤 4：获取访问地址

```bash
railway domain
```

得到类似：`https://quant-platform.railway.app`

---

## 方案 2：Render（备选）

### 步骤 1：创建 GitHub 仓库

```bash
cd C:\Users\huangruiran\ai_test
git remote add origin https://github.com/你的用户名/quant-platform.git
git push -u origin main
```

### 步骤 2：在 Render 平台连接

1. 访问 https://render.com
2. 用 GitHub 登录
3. 点击 `New +` → `Web Service`
4. 选择你的仓库
5. 自动检测 Python
6. 点击 `Create Web Service`

### 步骤 3：自动部署

以后每次 `git push` 都会自动部署！

---

## 方案 3：GitHub Actions 自动部署到服务器

如果你有云服务器（AWS/GCP/阿里云）：

### 创建 workflow 文件

```bash
mkdir -p .github/workflows
```

创建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Deploy to server
        run: |
          # 这里添加你的部署命令
          echo "Deploying..."
```

---

## 🎯 最快命令组合

```bash
# 1. 安装 CLI
npm i -g @railway/cli

# 2. 登录
railway login

# 3. 部署
railway up

# 4. 绑定域名
railway domain
```

**完成！** 🎉

---

## ⚠️ 注意事项

### 环境变量

如果你的项目需要 API Key（如 OpenAI、Google Cloud）：

```bash
railway variables set OPENAI_API_KEY=xxx
railway variables set GOOGLE_APPLICATION_CREDENTIALS=xxx
```

### 数据库

Railway 支持一键添加数据库：

```bash
railway add postgres
# 或
railway add redis
```

---

## 📊 平台对比

| 平台 | 免费额度 | 优点 | 缺点 |
|------|----------|------|------|
| Railway | $5/月 | 最简单，自动识别 | 免费额度有限 |
| Render | 免费层 | 永久免费，支持 Python | 资源有限 |
| Vercel | 免费 | 速度快 | 不适合 Python 后端 |
| Cloudflare Pages | 免费 | CDN 强大 | 只适合前端 |

---

## 🎁 终极建议

对于你的 **量化交易平台**：

```
GitHub (代码托管)
   ↓
Railway (自动部署)
   ↓
https://your-quant-platform.railway.app
```

**每次 push 自动部署**，完全自动化！
