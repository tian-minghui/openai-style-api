from loguru import logger
from adapters.azure import AzureAdapter
from adapters.base import ModelAdapter, invalid_request_error
from adapters.claude import ClaudeModel
from adapters.claude_web import ClaudeWebModel
from adapters.proxy import ProxyAdapter
from adapters.zhipu_api import ZhiPuApiModel
from adapters.xunfei_spark import XunfeiSparkAPIModel
from adapters.router_adapter import RouterAdapter
from adapters.model_name_router_adapter import ModelNameRouterAdapter
from adapters.gemini_adapter import GeminiAdapter
from adapters.bing_sydney import BingSydneyModel
from adapters.qwen import QWenAdapter
from adapters.skylark import SkylarkAdapter
model_instance_dict = {}


def get_adapter(instanceKey: str):
    model = model_instance_dict.get(instanceKey)
    if model is None:
        raise invalid_request_error("model not found")
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
        elif type == "model-name-router":
            model = ModelNameRouterAdapter(factory_method=get_adapter, **kwargs)
        elif type == "gemini":
            model = GeminiAdapter(**kwargs)
        elif type == "bing-sydney":
            model = BingSydneyModel(**kwargs)
        elif type == "qwen":
            model = QWenAdapter(**kwargs)
        elif type == "skylark":
            model = SkylarkAdapter(**kwargs)
        else:
            raise ValueError(f"unknown model type: {type}")
    except Exception as e:
        logger.exception(f"init model failed {instanceKey},{type},{kwargs}: {e}")
    if model is not None:
        model_instance_dict[instanceKey] = model
    return model


def clear_adapters():
    model_instance_dict.clear()
