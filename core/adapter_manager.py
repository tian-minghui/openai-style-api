

import json
from loguru import logger
from core.adapters.azure import AzureAdapter
from core.adapters.base import ModelAdapter
from core.adapters.claude import ClaudeModel
from core.adapters.claude_web import ClaudeWebModel
from core.adapters.proxy import ProxyAdapter
from core.adapters.zhipu_api import ZhiPuApiModel

key2Config = {}


class ModelConfig():
    def __init__(self, key, type, kwargs=dict()):
        self.type = type
        self.key = key
        self.kwargs = kwargs

    def __str__(self) -> str:
        # 打印所有属性和值
        return json.dumps(self.__dict__)


# 从model-config.json中读取配置 存储到key2Config
def load(config_path="model-config.json"):
    with open(config_path) as f:
        data = json.load(f)
        for key, config in data.items():
            type = config.pop("type")
            mc = ModelConfig(key, type, config)
            key2Config[key] = mc
            logger.info(f"key: {key}, ModelConfig: {mc}")


def getModelByKey(key: str) -> ModelAdapter:
    config = key2Config.get(key)
    if config is not None:
        return getModel(config)
    return None


model_instance_dict = {}


def getModel(config: ModelConfig) -> ModelAdapter:
    model = model_instance_dict.get(config.key)
    if model is not None:
        return model
    if config.type == "openai" or config.type == "proxy":
        model = ProxyAdapter(**config.kwargs)
        model_instance_dict[config.key] = model
        return model
    if config.type == "azure":
        model = AzureAdapter(**config.kwargs)
        model_instance_dict[config.key] = model
        return model
    if config.type == "claude":
        model = ClaudeModel(**config.kwargs)
        model_instance_dict[config.key] = model
        return model
    if config.type == "claude-web":
        model = ClaudeWebModel(**config.kwargs)
        model_instance_dict[config.key] = model
        return model
    if config.type == "zhipu-api":
        model = ZhiPuApiModel(**config.kwargs)
        model_instance_dict[config.key] = model
        return model
    raise ValueError(f"unknown model type: {config.type}")


load()

if __name__ == "__main__":
    print(getModelByKey("f2b7295fc440db7f"))
