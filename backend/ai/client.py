"""Minimax API 客户端 - Anthropic 兼容接口"""
import os
import json
from typing import Optional
import httpx


class AIClient:
    """Minimax AI 分类客户端"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = base_url or os.getenv("MINIMAX_API_BASE", "https://api.minimax.chat/v1")

        if not self.api_key:
            raise ValueError("MINIMAX_API_KEY environment variable is required")

    def classify(self, text: str, system_prompt: str) -> dict:
        """
        调用 AI 进行消费分类
        返回: {"category": str, "amount": float|None, "confidence": float}
        """
        url = f"{self.base_url}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "MiniMax-M2.7",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "max_tokens": 1024,
            "temperature": 0.1,
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

            message = data.get("choices", [{}])[0].get("message", {})
            content = message.get("content", "")

            # 兼容：如果content为空，尝试从reasoning_content提取JSON
            if not content:
                reasoning = message.get("reasoning_content", "")
                import re
                match = re.search(r'\{[^}]+\}', reasoning, re.DOTALL)
                if match:
                    content = match.group()

            if not content:
                raise ValueError("Empty response from AI")

            # 解析 JSON
            result = json.loads(content)
            return {
                "category": result.get("category", "其他"),
                "amount": result.get("amount"),
                "confidence": result.get("confidence", 0.5),
            }

        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error {e.response.status_code}: {e.response.text}")
        except json.JSONDecodeError:
            # 尝试从文本中提取 JSON
            import re
            match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Invalid JSON response: {content[:100]}")
        except Exception as e:
            raise RuntimeError(f"AI classification failed: {e}")


_client: Optional[AIClient] = None


def get_client() -> AIClient:
    global _client
    if _client is None:
        _client = AIClient()
    return _client


def classify_with_ai(text: str, system_prompt: str) -> dict:
    """快捷函数：使用 AI 分类"""
    return get_client().classify(text, system_prompt)
