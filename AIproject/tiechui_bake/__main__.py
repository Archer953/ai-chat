# 搬入：main() 函数
# 职责：协调各模块，主对话循环

"""
铁锤巴克 - AI 矮人铁匠对话系统
================================
功能概述：
    1. 基于 DeepSeek API 实现的多轮角色扮演对话系统
    2. 支持流式输出，提供实时的打字机效果
    3. 对话历史持久化存储，支持断点续聊
    4. 完整的 Prompt Engineering 设计，包含角色设定、边界控制和 Few-shot 示例

技术架构：
    - LLM 服务：DeepSeek Chat API
    - 数据持久化：JSON 文件存储
    - 对话管理：基于 messages 列表的上下文维护

数据持久化策略：
    采用完整保存策略（Full Preservation Strategy）：
    - 将包含 system prompt 在内的完整 messages 列表序列化为 JSON
    - 下次启动时直接反序列化，无需重新构建上下文
    - 优势：逻辑简单、状态完整、不易出错
    - 权衡：文件体积略大，但对话轮次通常有限，可接受

作者：[RK8848]
版本：1.0.0
最后更新：2026-04-10
"""
import logging
import sys

# main.py - 入口文件调用一次
from tiechui_bake.utils.logger import setup_logger
from tiechui_bake.services.persistence import PersistenceLayer
from tiechui_bake.services.ai_service import AIClientManager, stream_chat_completion
from tiechui_bake.config.settings import Configuration

setup_logger() # 配置一次
logger = logging.getLogger(__name__) # 模块级logger
config = Configuration()

# ============================================================================
# 主程序入口 (Main Entry Point)
# ============================================================================

def main() -> None:
    """
    程序主入口，协调各模块完成对话循环。

    执行流程：
        1. 加载或初始化对话历史
        2. 初始化 API 客户端
        3. 进入无限对话循环
        4. 处理用户输入和特殊命令
        5. 调用 AI 生成响应
        6. 更新并保存对话历史
    """
    # 阶段一：加载持久化数据
    messages = PersistenceLayer.load_conversation_history(config.conversation_history_file)

    # 阶段二：初始化 API 客户端
    client = AIClientManager.get_client()
    if client is None:
        logger.error("[致命错误] 无法连接到 AI 服务，程序退出")
        sys.exit(1)

    # 阶段三：欢迎界面
    print("\n" + "=" * 50)
    print("🔨 欢迎来到铁锤巴克的铁匠铺！")
    print("💡 输入 'quit' 或 'exit' 结束对话")
    print("=" * 50 + "\n")

    # 如果有历史对话，提示玩家
    if len(messages) > 1:
        logger.info("[系统] 继续上次的对话...\n")

    # 阶段四：主对话循环
    while True:
        try:
            # 获取用户输入
            user_input = input("> 你：").strip()

            # 命令处理：退出程序
            if user_input.lower() in ["exit", "quit"]:
                print("\n👋 巴克：哼！下次带够金币再来！")
                break

            # 命令处理：空输入跳过
            if not user_input:
                continue

            # 将用户消息加入上下文
            messages.append({"role": "user", "content": user_input})

            # 调用 AI 生成响应
            print("🔨 巴克：", end="")
            assistant_response = stream_chat_completion(client, messages)
            print("\n")  # 响应结束后换行

            # 将 AI 响应加入上下文
            messages.append({"role": "assistant", "content": assistant_response})

        except KeyboardInterrupt:
            # 优雅处理 Ctrl+C 中断
            logger.info("\n\n[系统] 收到中断信号，正在保存并退出...")
            break
        except Exception as e:
            # 兜底异常处理，防止单次对话错误导致整个程序崩溃
            logger.error(f"\n[错误] 发生未知异常: {e}")
            continue

    # 阶段五：保存并退出
    PersistenceLayer.save_conversation_history(messages, config.conversation_history_file)
    logger.info("[系统] 程序正常退出")


# ============================================================================
# 脚本执行入口00
# ============================================================================
if __name__ == "__main__":
    main()