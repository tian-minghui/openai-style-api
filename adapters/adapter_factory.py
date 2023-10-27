import json
from loguru import logger
from adapters.azure import AzureAdapter
from adapters.base import ModelAdapter
from adapters.claude import ClaudeModel
from adapters.claude_web import ClaudeWebModel
from adapters.proxy import ProxyAdapter
from adapters.zhipu_api import ZhiPuApiModel
from adapters.xunfei_spark import XunfeiSparkAPIModel
from adapters.router_adapter import RouterAdapter

model_instance_dict = {}


def get_adapter(instanceKey: str):
    model = model_instance_dict.get(instanceKey)
    if model is None:
        raise Exception("model not found")
    return model


def init_adapter(instanceKey: str, type: str, **kwargs) -> ModelAdapter:
    model = model_instance_dict.get(instanceKey)
    if model is not None:
        return model
    try:
        if type == "openai" or type == "proxy":
            model = ProxyAdapter(**kwargs)
        elif type == "azure":
            model = AzureAdapter(**kwargs)

        elif type == "claude":
            model = ClaudeModel(**kwargs)

        elif type == "claude-web":
            model = ClaudeWebModel(**kwargs)

        elif type == "zhipu-api":
            model = ZhiPuApiModel(**kwargs)

        elif type == "xunfei-spark-api":
            model = XunfeiSparkAPIModel(**kwargs)

        elif type == "router":
            model = RouterAdapter(factory_method=get_adapter, **kwargs)

        else:
            raise ValueError(f"unknown model type: {type}")
    except Exception as e:
        logger.error(f"init model failed {instanceKey},{type},{kwargs}: {e}")
    if model is not None:
        model_instance_dict[instanceKey] = model
    return model


def clear_adapters():
    model_instance_dict.clear()
