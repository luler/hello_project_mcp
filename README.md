# HTML 部署 MCP 服务

一个基于 FastAPI 的 MCP 服务器，可将 HTML 页面代码一键部署到在线预览平台，返回可访问的 URL。

## ✨ 功能

- 🚀 一键部署 HTML 页面到在线服务器
- 🔗 返回可直接访问的预览链接
- 🤖 支持 MCP 协议，可与 Claude、Cursor 等 AI 工具集成

## 📋 环境要求

- Python 3.12+

## 🛠️ 安装

```bash
# 克隆项目
git clone https://github.com/luler/hello_project_mcp.git
cd hello_project_mcp

# 安装依赖
pip install -r requirements.txt
```

## 🚀 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8989` 启动。

## 📡 MCP 端点

| 端点                          | 协议   | 用途                    |
|-----------------------------|------|-----------------------|
| `http://localhost:8989/mcp` | HTTP | Streamable HTTP 传输    |
| `http://localhost:8989/sse` | SSE  | Server-Sent Events 传输 |

## 🔧 配置 MCP 客户端

### Claude Desktop

编辑配置文件：

```json
{
  "mcpServers": {
    "html-deploy": {
      "url": "http://localhost:8989/sse"
    }
  }
}
```

### Cursor

在 Cursor 设置中添加 MCP 服务器：

```json
{
  "mcpServers": {
    "html-deploy": {
      "url": "http://localhost:8989/sse"
    }
  }
}
```

### Cherry Studio / 其他客户端

使用 SSE 端点：`http://localhost:8989/sse`

## 💬 使用示例

配置完成后，在 AI 对话中可以这样使用：

```
帮我做一个贪吃蛇游戏，用 deploy_html 部署，给我链接
```

```
创建一个渐变背景的登录页面，然后部署上线
```

```
写一个动态时钟页面，deploy_html 发布一下
```

AI 会自动生成 HTML 代码并调用 `deploy_html` 工具进行部署，返回预览链接。

## 📖 API 文档

启动服务后访问：

- Swagger UI: http://localhost:8989/docs
- ReDoc: http://localhost:8989/redoc

### deploy_html

部署 HTML 页面到预览服务器。

**请求：**

```json
{
  "html": "<!DOCTYPE html><html>...</html>"
}
```

**响应：**

```json
{
  "success": true,
  "message": "HTML打包并上传成功",
  "preview_url": "https://html.luler.top/preview/xxxxx"
}
```

## ⚙️ 配置说明

通过环境变量或 `.env` 文件配置：

```bash
UPLOAD_PLATFORM_BASE_URL=https://html.luler.top  # 预览平台地址
UPLOAD_CODE=xxxxxx  # 项目标识
PORT=8989  # 服务端口
DEBUG=0  # 调试模式（1为开启热重载）
```
