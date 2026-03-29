"""
LLMs 文档路由 - 遵循 llmstxt.org 规范
暴露 doc/quant-qmt-proxy/llms/ 目录下的文档文件
"""
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

router = APIRouter(prefix="/llms", tags=["LLMs 文档"])

_DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "doc", "quant-qmt-proxy", "llms")


def _read_doc(filename: str) -> str:
    filepath = os.path.normpath(os.path.join(_DOCS_DIR, filename))
    if not filepath.startswith(os.path.normpath(_DOCS_DIR)):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail=f"Document '{filename}' not found")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


@router.get("/", response_class=PlainTextResponse, summary="LLMs 文档索引")
async def llms_index():
    """返回 llms.txt 主索引文件（遵循 llmstxt.org 规范）"""
    return _read_doc("llms.txt")


@router.get("/llms.txt", response_class=PlainTextResponse, include_in_schema=False)
async def llms_txt():
    """llms.txt 兼容路径"""
    return _read_doc("llms.txt")


@router.get("/api.txt", response_class=PlainTextResponse, summary="完整 REST API 参考")
async def llms_api():
    """返回完整的 REST API 接口文档"""
    return _read_doc("api.txt")


@router.get("/data.txt", response_class=PlainTextResponse, summary="行情数据模块文档")
async def llms_data():
    """返回行情数据模块详细说明（订阅、K线、tick、Level2、数据下载）"""
    return _read_doc("data.txt")


@router.get("/trading.txt", response_class=PlainTextResponse, summary="交易模块文档")
async def llms_trading():
    """返回交易模块详细说明（连接、下单、撤单、持仓查询）"""
    return _read_doc("trading.txt")


@router.get("/{filename}", response_class=PlainTextResponse, summary="获取指定文档文件", include_in_schema=False)
async def llms_file(filename: str):
    """返回指定的文档文件（仅限 .txt 文件）"""
    if not filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are served under /llms/")
    return _read_doc(filename)
