import json
from typing import Dict, List

from pydantic import BaseModel
from loguru import logger
from adapters.adapter_factory import init_adapter, clear_adapters
import os

class ModelConfig(BaseModel):
    token: str
    type: str
    config: dict


token_2_modelconfig: Dict[str, ModelConfig] = dict()
config_path = "model-config.json"
if not os.path.exists(config_path):
    config_path = "model-config-default.json"


def load_model_config():
    with open(config_path) as f:
        data = json.load(f)
        for config in data:
            model_config = ModelConfig(
                token=config.get("token"),
                type=config.get("type"),
                config=config.get("config"),
            )
            token_2_modelconfig[config.get("token")] = model_config
    init_all_adapter()
    logger.info(
        f"load model config from {config_path}, token_2_modelconfig:{token_2_modelconfig}"
    )


def init_all_adapter():
    clear_adapters()
    for token, config in token_2_modelconfig.items():
        init_adapter(token, config.type, **config.config)


def get_model_config(token):
    return token_2_modelconfig.get(token, None)


def get_all_model_config():
    return [
        config.model_dump(exclude_none=True) for config in token_2_modelconfig.values()
    ]


def update_model_config(config: List[ModelConfig]):
    """
    更新模型配置
    :param json_str:
    :return:
    """
    for config in config:
        token = config.token
        token_2_modelconfig[token] = config
    with open(config_path, "w") as f:
        json.dump([config.model_dump() for config in token_2_modelconfig.values()], f)
    logger.info(f"update model config to {config_path}")
    load_model_config()


if __name__ == "__main__":
    load_model_config()
    print(get_model_config("123"))
    print(get_all_model_config())
    print(get_model_config("GxqT3BlbkFJj"))
