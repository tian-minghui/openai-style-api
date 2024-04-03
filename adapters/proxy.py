import json
from typing import Iterator
from adapters.base import ModelAdapter, stream, post
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from loguru import logger


class ProxyAdapter(ModelAdapter):
    """
    proxy适配器，直接当作代理调用openai或者是第三方代理服务（openai-sb，ohmygpt等）
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.api_key = kwargs.pop("api_key", None)
        self.api_base = kwargs.pop("api_base", None)
        self.config_args = kwargs

    def chat_completions(self, request: ChatCompletionRequest) -> Iterator[ChatCompletionResponse]:
        """
        https://platform.openai.com/docs/api-reference/chat/create
        https://platform.openai.com/docs/guides/gpt/chat-completions-api
        """
        header = {}
        header["Content-Type"] = "application/json"
        header["Authorization"] = "Bearer " + self.api_key
        url = f"{self.api_base}chat/completions"
        req_args = self.convert_param(request)
        logger.info(f"ProxyAdapter url: {url}, data: {req_args}")
        if request.stream:
            response = stream(url, header, req_args)
            for chunk in response.iter_lines(chunk_size=1024):
                # 移除头部data: 字符
                decoded_line = chunk.decode('utf-8')
                logger.info(f"decoded_line: {decoded_line}")
                decoded_line = decoded_line.lstrip("data:").strip()
                if "[DONE]" == decoded_line:
                    break
                if decoded_line:
                    yield ChatCompletionResponse(**json.loads(decoded_line))
        else:
            response = post(url, header, req_args)
            resp = ChatCompletionResponse(**response)
            yield resp

    def convert_param(self, request: ChatCompletionRequest):
        req_args = request.model_dump(exclude_none=True, exclude_defaults=True)
        req_args.update(self.config_args)
        return req_args
