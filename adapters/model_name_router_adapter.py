from typing import Iterator
from adapters.base import ModelAdapter
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from loguru import logger


class ModelNameRouterAdapter(ModelAdapter):
    def __init__(self, factory_method, **kwargs):
        super().__init__(**kwargs)
        self.model_2_token: dict = kwargs.pop("model-2-token", {})
        self.default_token = self.model_2_token.get("default", None)
        self.factory_method = factory_method

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        token = None
        adapter = None
        model_name = request.model
        if model_name in self.model_2_token:
            token = self.model_2_token[model_name]
            adapter = self.factory_method(token)
        else:
            assert self.default_token is not None, "No default token is specified"
            token = self.default_token
            adapter = self.factory_method(token)
        logger.info(
            f"ModelNameRouterAdapter model_name:{model_name} select:token:{token}, adapter:{adapter}"
        )
        return adapter.chat_completions(request)
