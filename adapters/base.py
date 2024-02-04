import time
from typing import Union, Iterator
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from utils.util import num_tokens_from_string


class ModelAdapter:
    def __init__(self, **kwargs):
        pass

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        """
        返回一个迭代器对象
         stream为false   第一个就是结果
        """
        pass

    def completion_to_openai_response(self, completion: str, model: str = "default"):
        completion_tokens = num_tokens_from_string(completion)
        openai_response = {
            "id": f"chatcmpl-{str(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": completion_tokens,
                "total_tokens": completion_tokens,
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": completion,
                    },
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
        }
        return openai_response

    def completion_to_openai_stream_response(
        self, completion: str, model: str = "default"
    ):
        completion_tokens = num_tokens_from_string(completion)
        openai_response = {
            "id": f"chatcmpl-{str(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": completion_tokens,
                "total_tokens": completion_tokens,
            },
            "choices": [
                {
                    "delta": {
                        "role": "assistant",
                        "content": completion,
                    },
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
        }
        return openai_response
