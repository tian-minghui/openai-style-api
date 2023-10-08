

import json
from typing import Iterator, Union
from core.adapters.base import ModelAdapter
from core.protocol import ChatCompletionRequest, ChatCompletionResponse
import requests
from loguru import logger


class AzureAdapter(ModelAdapter):
    """
        https://learn.microsoft.com/en-us/azure/ai-services/openai/chatgpt-quickstart?pivots=rest-api&tabs=command-line#rest-api
        curl $AZURE_OPENAI_ENDPOINT/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-05-15 \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_OPENAI_KEY" \
  -d '{"messages":[{"role": "system", "content": "You are a helpful assistant."},{"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},{"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},{"role": "user", "content": "Do other Azure AI services support this too?"}]}'
    """
    param_list = ["messages", "temperature", "n", "stream", "stop", "max_tokens", "presence_penalty",
                  "frequency_penalty", "logit_bias", "user", "function_call", "functions"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.end_point = kwargs.pop("api_base", None)
        self.api_key = kwargs.pop("api_key", None)
        self.api_version = kwargs.pop("api_version", None)
        self.deployment_id = kwargs.pop("deployment_id", None)
        self.config_args = kwargs

    def chat_completions(self, request: ChatCompletionRequest) -> Union[ChatCompletionResponse, Iterator[ChatCompletionResponse]]:
        # 发起post请求
        header = {}
        header["Content-Type"] = "application/json"
        header["api-key"] = self.api_key
        url = f"{self.end_point}openai/deployments/{self.deployment_id}/chat/completions?api-version={self.api_version}"
        req_args = self.convert_param(request)
        logger.info(f"AzureOpenAiModel url: {url}, data: {req_args}")
        response = requests.post(
            url, headers=header, data=json.dumps(req_args), stream=request.stream)
        if response.status_code != 200:
            raise Exception(response.content)
        if request.stream:
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
            data = response.json()
            resp = ChatCompletionResponse(**data)
            yield resp

    def convert_param(self, request: ChatCompletionRequest):
        req_args = request.model_dump(exclude_none=True, exclude_defaults=True)
        req_args.update(self.config_args)
        # 请求有未识别参数会报错，这里过滤下   Unrecognized request argument supplied: type
        param = {k: v for k, v in req_args.items() if k in self.param_list}
        return param
