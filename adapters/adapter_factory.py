

import json
from loguru import logger
from adapters.azure import AzureAdapter
from adapters.base import ModelAdapter
from adapters.claude import ClaudeModel
from adapters.claude_web import ClaudeWebModel
from adapters.proxy import ProxyAdapter
from adapters.zhipu_api import ZhiPuApiModel

model_instance_dict = {}


def get_adapter(instanceKey: str, type: str, **kwargs) -> ModelAdapter:
    model = model_instance_dict.get(instanceKey)
    if model is not None:
        return model
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

    else:
        raise ValueError(f"unknown model type: {type}")

    model_instance_dict[instanceKey] = model
    return model


def clear_instances():
    model_instance_dict.clear()
