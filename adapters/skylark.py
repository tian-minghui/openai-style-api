from typing import Iterator
from adapters.base import ModelAdapter
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from volcengine.maas import MaasService


class SkylarkAdapter(ModelAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = kwargs.pop("model")
        self.config_args = kwargs
        self.maas = MaasService('maas-api.ml-platform-cn-beijing.volces.com', 'cn-beijing')
        api_key = kwargs.pop("api_key")
        ak, sk = api_key.split(":")
        self.maas.set_ak(ak)
        self.maas.set_sk(sk)

    def chat_completions(self, request: ChatCompletionRequest) -> Iterator[ChatCompletionResponse]:
        data = self.openai_req_2_sl_req(request)
        if request.stream:
            resps = self.maas.stream_chat(data)
            index = 0
            for resp in resps:
                yield ChatCompletionResponse(**self.sl_resp_2_openai_resp_stream(resp, index))
                index += 1
        else:
            resp = self.maas.chat(data)
            yield ChatCompletionResponse(**self.sl_resp_2_openai_resp(resp))

    def sl_resp_2_openai_resp(self, response: dict) -> dict:
        id = response["req_id"]
        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"]["completion_tokens"]
        content = response["choice"]["message"]["content"]
        return self.completion_to_openai_response(
            content,
            model=self.model,
            id=id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def sl_resp_2_openai_resp_stream(self, response: dict, index: int) -> dict:
        id = response["req_id"]
        content = response["choice"]["message"]["content"]
        return self.completion_to_openai_stream_response(
            content,
            self.model,
            index,
            finish_reason="stop" if not content else None,
            id=id,
        )

    def openai_req_2_sl_req(self, request: ChatCompletionRequest) -> dict:
        req = {
            "model": {
                "name": self.model,
            },
            "parameters": {
                "max_new_tokens": request.max_length or self.config_args.get('max_length'),
                "temperature": request.temperature or self.config_args.get('temperature')
            },
            "messages": [
                m.model_dump(exclude_none=True) for m in request.messages
            ]
        }
        return req
