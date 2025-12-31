import io
import os
import zipfile

import dotenv
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi_mcp import FastApiMCP
from pydantic import BaseModel, Field

# 初始化配置
dotenv.load_dotenv()

app = FastAPI(title="HTML打包上传服务")

# ==================== 配置 ====================
UPLOAD_PLATFORM_BASE_URL = os.getenv('UPLOAD_PLATFORM_BASE_URL', "https://html.luler.top")  # 预览平台基础URL
UPLOAD_CODE = os.getenv('UPLOAD_CODE', "xxxxxx")  # 认证码/项目标识


# ==================== 请求/响应模型 ====================
class HtmlSubmission(BaseModel):
    """HTML提交请求模型"""
    html: str = Field(..., description="完整的HTML页面代码")


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="结果消息")
    preview_url: str = Field(..., description="页面预览URL")


# ==================== 工具函数 ====================
def create_html_zip(html: str, filename: str = "index.html") -> bytes:
    """
    将HTML内容打包成ZIP文件（内存中，不落盘）
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(filename, html.encode('utf-8'))

    zip_buffer.seek(0)
    return zip_buffer.getvalue()


async def upload_to_platform(zip_data: bytes) -> dict:
    """
    将ZIP文件上传到第三方平台

    接口要求:
    - POST form-data
    - code: 认证码
    - file: ZIP文件
    """
    # zip文件名
    zip_filename = f"hello_project_mcp.zip"

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 构造 multipart/form-data 请求
        files = {
            'file': (zip_filename, zip_data, 'application/zip')
        }
        data = {
            'code': UPLOAD_CODE
        }

        response = await client.post(
            UPLOAD_PLATFORM_BASE_URL + "/api/uploadProjectDirect",
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()


# ==================== API 接口 ====================
@app.post(
    "/deployHtml",
    operation_id="deploy_html",
    response_model=UploadResponse,
    summary="部署HTML页面到预览服务器",
    description="""
    将完整的HTML页面代码部署到在线预览服务器。

    **参数说明：**
    - html: 完整的HTML代码（必须使用此参数名）

    使用场景：
    - 当你生成了HTML页面代码后，调用此工具可立即部署上线
    - 部署后会返回一个可访问的预览URL
    """
)
async def deploy_html(submission: HtmlSubmission, request: Request) -> UploadResponse:
    """
    将HTML页面代码打包成ZIP文件并上传到预览平台

    流程：
    1. 接收完整的HTML页面代码
    2. 在内存中打包生成 hello_project_mcp.zip（包含 index.html）
    3. 上传到预览平台接口
    4. 返回预览URL
    """

    try:
        # 1. 在内存中创建ZIP文件
        zip_data = create_html_zip(submission.html)

        # 2. 上传到第三方平台
        try:
            platform_result = await upload_to_platform(zip_data)
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"上传到预览平台失败: HTTP {e.response.status_code}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"无法连接到预览平台: {str(e)}"
            )

        # 3. 解析平台响应
        if platform_result.get("code") != 200:
            raise HTTPException(
                status_code=502,
                detail=f"平台返回错误: {platform_result.get('message', '未知错误')}"
            )

        preview_url = platform_result.get("info", {}).get("url")

        # 4. 返回结果
        return UploadResponse(
            success=True,
            message="HTML打包并上传成功",
            preview_url=preview_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


# ==================== MCP 服务器配置 ====================
mcp = FastApiMCP(
    app,
    name="HTML打包上传服务",
    description="提供HTML页面打包并上传到预览平台的功能，返回可访问的预览URL"
)

mcp.mount_http()  # HTTP入口：/mcp
mcp.mount_sse()  # SSE入口：/sse

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv('PORT', 8989)), reload=os.getenv('DEBUG', '0') == '1')
