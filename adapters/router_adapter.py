from typing import Iterator
from adapters.base import ModelAdapter
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
import random
from loguru import logger


class RouterAdapter(ModelAdapter):
    def __init__(self, factory_method, **kwargs):
        super().__init__(**kwargs)
        self.router_strategy = kwargs.pop("router_strategy", None)
        self.token_pool = kwargs.pop("token_pool", None)
        self.factory_method = factory_method
        if self.router_strategy == "round-robin":
            self.round_cnt = 0

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        token = None
        adapter = None
        if self.router_strategy == "round-robin":
            index = self.round_cnt % len(self.token_pool)
            self.round_cnt = self.round_cnt + 1
            token = self.token_pool[index]
            adapter = self.factory_method(token)

        elif self.router_strategy == "random":
            token = random.sample(self.token_pool, 1)
            adapter = self.factory_method(token)
        else:
            raise ValueError("Unknown router strategy: {}".format(self.router_strategy))
        logger.info(f"RouterAdapter select:token:{token}, adapter:{adapter}")
        return adapter.chat_completions(request)
