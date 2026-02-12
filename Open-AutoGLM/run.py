#!/usr/bin/env python3
"""
示例：使用 PhoneAgent 执行任务

使用前请设置环境变量：
  export AUTOGLM_API_KEY="your-api-key"
  export PHONE_DEVICE_ID="localhost:5555"  # 可选
"""
import os
from phone_agent import PhoneAgent
from phone_agent.agent import AgentConfig
from phone_agent.model import ModelConfig


def main():
    api_key = os.environ.get("AUTOGLM_API_KEY")
    if not api_key:
        print("Error: AUTOGLM_API_KEY environment variable not set")
        print("Please run: export AUTOGLM_API_KEY='your-api-key'")
        return 1

    device_id = os.environ.get("PHONE_DEVICE_ID", "localhost:5555")
    base_url = os.environ.get("AUTOGLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4")
    model_name = os.environ.get("AUTOGLM_MODEL", "autoglm-phone")

    model_config = ModelConfig(
        base_url=base_url,
        api_key=api_key,
        model_name=model_name,
    )

    agent_config = AgentConfig(device_id=device_id)

    agent = PhoneAgent(model_config=model_config, agent_config=agent_config)

    # 示例任务
    result = agent.run("打开设置")
    print(result)


if __name__ == "__main__":
    exit(main() or 0)
