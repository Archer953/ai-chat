# 搬入：PersistenceLayer 类的两个方法
# 职责：对话历史的保存和加载

from tiechui_bake.core.prompts import PromptEngineering
from tiechui_bake.config.settings import Configuration

import os
import json
import logging
from typing import List,Dict

logger = logging.getLogger(__name__) # 模块级logger
config = Configuration()


# ============================================================================
# 数据持久化层 (Persistence Layer)
# ============================================================================
# 负责对话历史的存储与恢复，实现断点续聊功能
# 采用 JSON 格式进行序列化，兼顾可读性和通用性
class PersistenceLayer:
    @staticmethod
    def load_conversation_history(filepath: str) -> List[Dict[str, str]]:
        system_prompt = PromptEngineering().system_prompt
        """
        从 JSON 文件加载完整的对话历史。

        实现细节：
            - 如果文件存在且格式正确，直接返回反序列化的 messages 列表
            - 如果文件不存在（首次运行），返回仅包含 system prompt 的初始列表
            - 此设计保证了每次启动都能获得正确的上下文状态

        Args:
            filepath: 存档文件的路径

        Returns:
            List[Dict[str, str]]: 完整的 messages 列表，格式符合 OpenAI API 规范

        Raises:
            无显式抛出异常，所有异常内部处理，返回初始状态以保证程序可继续运行
        """
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                    # 防御性编程：验证加载的数据结构是否符合预期
                    if isinstance(messages, list) and len(messages) > 0:
                        logger.info(f"[系统] 已加载历史对话，共 {len(messages) - 1} 轮")
                        return messages
                    else:
                        logger.warning("[系统] 存档格式异常，将创建新对话")
            except (json.JSONDecodeError, IOError) as e:
                # 文件损坏或读取失败时的降级处理
                logger.error(f"[系统] 读取存档失败 ({e})，将创建新对话")

        # 首次运行或异常情况：返回初始对话状态
        logger.info("[系统] 开始新的对话")
        return [{"role": "system", "content": system_prompt}]

    @staticmethod
    def save_conversation_history(messages: List[Dict[str, str]], filepath: str) -> None:
        """
        将完整的对话历史序列化并保存到 JSON 文件。

        设计考量：
            - 使用 indent=2 提高文件可读性，便于人工检查
            - ensure_ascii=False 保留中文原文，避免 Unicode 转义
            - 采用覆盖写入（'w'）而非追加（'a'），因为 messages 已包含完整历史

        Args:
            messages: 完整的对话历史列表
            filepath: 目标保存路径
        """
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            logger.info(f"[系统] 对话历史已保存至 {filepath}")
        except IOError as e:
            logger.error(f"[错误] 保存对话历史失败: {e}")

