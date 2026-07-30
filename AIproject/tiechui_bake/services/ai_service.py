# 搬入：initialize_client() 和 stream_chat_completion()
# 职责：API 客户端管理、流式对话处理

from tiechui_bake.config.settings import Configuration


from openai import OpenAI
from typing import List, Dict, Optional
import logging

# ============================================================================
# AI 交互层 (AI Interaction Layer)
# ============================================================================
# 封装与 DeepSeek API 的交互逻辑，包括客户端初始化和流式对话

config = Configuration()
logger = logging.getLogger(__name__) # 模块级logger

class AIClientManager:
    """ AI 客户端单例管理器 """
    _instance: Optional[OpenAI] = None

    @classmethod
    def get_client(cls) -> Optional[OpenAI]:
        """ 获取单例客户端 """
        if cls._instance is None:
            cls._instance = cls._initialize_client()

        return cls._instance

    @classmethod
    def _initialize_client(cls) -> Optional[OpenAI]:

        """
        初始化 OpenAI 兼容客户端。

        Returns:
            OpenAI 客户端实例，失败时返回 None

        Note:
            客户端实例是可复用的，应在程序生命周期中保持单例使用
        """
        try:
            client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url,
            )
            logger.info("API 客户端初始化成功")
            return client
        except Exception as e:
            logger.error(f"[错误] API 客户端初始化失败: {e}", exc_info=True)
            return None


def stream_chat_completion(
        client: OpenAI,
        messages: List[Dict[str, str]]
) -> str:
    """
    执行流式对话，逐字符输出 AI 响应，实现打字机效果。

    工作流程：
        1. 发起流式 API 请求 (stream=True)
        2. 遍历响应数据块，提取增量内容
        3. 实时打印到控制台，同时累积完整响应
        4. 返回完整响应用于存档

    Args:
        client: 已初始化的 OpenAI 客户端
        messages: 包含完整上下文的对话历史

    Returns:
        str: AI 的完整响应文本
    """

    # 创建用于存储对话的容器
    full_response = ""
    logger.debug("容器创建成功")

    try:
        # 发起流式请求
        stream = client.chat.completions.create( # type: ignore
            messages=messages,
            model=config.model,
            temperature=config.temperature,
            stream=True
        )
        logger.debug(f"开始流式响应，消息数: {len(messages)}")

        # 逐块处理响应流
        for chunk in stream:
            # delta.content 可能为 None（如流结束标志）
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                # flush=True 确保实时显示，不会因缓冲而延迟
                print(content, end="", flush=True)

        logger.debug(f"流式响应完成，响应长度: {len(full_response)}")

    except Exception as e:
        # 网络异常、API 限流等情况的容错处理
        error_msg = f'{{"emotion": "困惑", "dialogue": "呃...炉子好像灭了，老子今天不在状态！"}}'
        logger.error(f"\n[错误] API 调用失败: {e}")
        return error_msg

    return full_response

