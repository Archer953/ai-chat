import sys
import os

# 搬入：Configuration 类
# 职责：管理所有配置项、环境变量验证

# ============================================================================
# 配置常量区 (Configuration Constants)
# ============================================================================
# 所有可调整的系统配置集中在此，便于维护和环境切换

class Configuration:
    # 配置初始化s
    def __init__(self):
        # API 配置
        # 注意：API Key 必须通过环境变量传入，禁止硬编码，这是安全最佳实践
        self._api_key: str = os.environ.get("DEEPSEEK_API_KEY")
        if not self._api_key:
            print("错误：环境变量 DEEPSEEK_API_KEY 未设置", file=sys.stderr)
            print("请在终端执行：export DEEPSEEK_API_KEY='your-api-key-here'", file=sys.stderr)
            sys.exit(1)

        # DeepSeek API 端点
        self._base_url: str = "https://api.deepseek.com"

        # 使用的模型版本
        self._model: str = "deepseek-chat"

        # 文件路径配置
        self._conversation_history_file: str = r"E:\AIproject\tiechui_bake\save_conversations\conversation_history.json"  # 对话存档文件

        # 对话参数配置
        self._temperature: float = 1.0  # 生成随机性，1.0 为最高，适合角色扮演的多样性

    # 获取密钥
    @property
    def api_key(self) -> str:
        return self._api_key

    # 获取地址
    @property
    def base_url(self) -> str:
        return self._base_url

    # 获取模型
    @property
    def model(self) -> str:
        return self._model

    # 获取对话文件存储路径
    @property
    def conversation_history_file(self) -> str:
        return self._conversation_history_file

    # 获取温度参数
    @property
    def temperature(self) -> float:
        return self._temperature

