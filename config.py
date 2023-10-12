import json
from typing import Dict

from pydantic import BaseModel
from loguru import logger


class ModelConfig(BaseModel):
    token: str
    type: str
    config: dict


token_2_modelconfig: Dict[str, ModelConfig] = dict()
config_path = "model-config.json"


def load_model_config():
    with open(config_path) as f:
        data = json.load(f)
        for config in data:
            type = config.pop("type")
            token = config.pop("token")
            args = config
            model_config = ModelConfig(token=token, type=type, config=args)
            token_2_modelconfig[token] = model_config
    logger.info(
        f"load model config from {config_path}, token_2_modelconfig:{token_2_modelconfig}")


def get_model_config(token):
    return token_2_modelconfig.get(token, None)


def get_all_model_config():
    return token_2_modelconfig.values()


if __name__ == "__main__":
    load_model_config()
    print(get_model_config("123"))
    print(get_all_model_config())
    print(get_model_config("GxqT3BlbkFJj"))
