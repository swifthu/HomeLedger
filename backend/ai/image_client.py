"""MiniMax 图片理解客户端 - Token Plan MCP"""
import os
import base64
import requests
from typing import Optional


class ImageUnderstandClient:
    """图片理解客户端 - 使用 MiniMax Token Plan VLM API"""

    def __init__(self, api_key: Optional[str] = None, api_host: Optional[str] = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.api_host = api_host or os.getenv("MINIMAX_API_HOST", "https://api.minimax.io")

        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY environment variable is required")

    def understand_image(self, image_data: bytes, prompt: str) -> dict:
        """
        分析图片内容

        Args:
            image_data: 图片二进制数据
            prompt: 提问/分析请求

        Returns:
            {"content": str} - 图片分析结果
        """
        # 将图片转为 base64
        b64_data = base64.b64encode(image_data).decode("utf-8")

        # 检测图片格式
        if image_data[:8] == b'\x89PNG\r\n\x1a\n':
            mime_type = "image/png"
        elif image_data[:2] == b'\xff\xd8':
            mime_type = "image/jpeg"
        elif image_data[:4] == b'RIFF' and image_data[8:12] == b'WEBP':
            mime_type = "image/webp"
        else:
            mime_type = "image/png"

        data_url = f"data:{mime_type};base64,{b64_data}"

        url = f"{self.api_host}/v1/coding_plan/vlm"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "MM-API-Source": "Minimax-MCP",
        }
        payload = {
            "prompt": prompt,
            "image_url": data_url,
        }

        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()

        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code", 0) != 0:
            raise RuntimeError(f"VLM API error: {base_resp.get('status_msg')}")

        return {"content": data.get("content", "")}


_client: Optional[ImageUnderstandClient] = None


def get_image_client() -> ImageUnderstandClient:
    global _client
    if _client is None:
        _client = ImageUnderstandClient()
    return _client


def understand_receipt(image_data: bytes) -> dict:
    """
    识别小票/发票图片，返回结构化信息

    返回: {
        "items": [{"name": str, "amount": float}],
        "total": float,
        "store": str,
        "date": str,
    }
    """
    client = get_image_client()
    result = client.understand_image(
        image_data,
        "请分析这张小票/发票图片，提取所有消费项目和金额，返回JSON格式："
        '{"items":[{"name":"商品名称","amount":金额}],"total":总金额,"store":"商店名称","date":"日期"}'
        "，只返回JSON，不要其他文字。如果无法识别，返回空对象{}。"
    )

    import json
    try:
        return json.loads(result["content"])
    except (json.JSONDecodeError, KeyError):
        return {}
