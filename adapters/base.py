import json
import time
from typing import Union, Iterator

from openai import OpenAIError
import requests
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from utils.util import num_tokens_from_string
from loguru import logger


api_timeout_seconds = 300

"""
http:
status_code:429

body:
{
    "error": {
        "message": "You exceeded your current quota, please check your plan and billing details. For more information on this error, read the docs: https://platform.openai.com/docs/guides/error-codes/api-errors.",
        "type": "insufficient_quota",
        "param": null,
        "code": "insufficient_quota"
    }
}

https://platform.openai.com/docs/guides/error-codes/api-errors
"""


class UDFApiError(OpenAIError):
    def __init__(self, message, status: int = 500, code="server_error"):
        super(UDFApiError, self).__init__(message)
        self.http_status = status
        self._message = message


def authentication_error():
    return UDFApiError("Invalid Authentication", 401, "")


def rate_limit_error(message):
    return UDFApiError(message, 429, "")


def serverError(message):
    return UDFApiError(message, 500)


def invalid_request_error(message):
    return UDFApiError(message, 400)


def resp_text(resp):
    resp_str = None
    if resp is not None:
        resp_str = f"status_code:{resp.status_code}: {resp.text}"
    return resp_str


def post(
    api_url, headers: dict, params: dict, timeout=api_timeout_seconds, proxies=None
):
    resp = None
    try:
        resp = requests.post(
            url=api_url,
            headers=headers,
            data=json.dumps(params),
            timeout=timeout,
            proxies=proxies,
        )
        if requests.codes.ok != resp.status_code:
            raise UDFApiError(resp.text, resp.status_code)
        return json.loads(resp.text)
    finally:
        logger.debug(
            f"【http.post】 请求url：{api_url}, headers:{headers}, params:{params}, resp:{resp_text(resp)}"
        )


def stream(
    api_url, headers: dict, params: dict, timeout=api_timeout_seconds, proxies=None
):
    resp = None
    try:
        resp = requests.post(
            api_url,
            stream=True,
            headers=headers,
            json=params,
            # data=json.dumps(params),
            timeout=timeout,
            proxies=proxies,
        )
        if requests.codes.ok != resp.status_code:
            raise UDFApiError(resp.text, resp.status_code)
        return resp
    finally:
        logger.debug(
            f"【http.stream】 请求url：{api_url}, headers:{headers}, params:{params}, resp:{resp_text(resp)}"
        )


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

    # completion 转 openai_response
    def completion_to_openai_response(
        self, completion: str, model: str = "default", **kargs
    ):
        completion_tokens = kargs.get("completion_tokens")
        if completion_tokens is None:
            completion_tokens = num_tokens_from_string(completion)
        prompt_tokens = kargs.get("prompt_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens
        id = kargs.get("id", f"chatcmpl-{str(time.time())}")
        finish_reason = kargs.get("finish_reason", "stop")
        created = kargs.get("created", int(time.time()))
        openai_response = {
            "id": id,
            "object": "chat.completion",
            "created": created,
            "model": model,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": completion,
                    },
                    "index": 0,
                    "finish_reason": finish_reason,
                }
            ],
        }
        return openai_response



    # stream下  每次的completion  转  openai_stream_response
    def completion_to_openai_stream_response(
        self, completion: str, model: str = "default", index = 0, **kargs
    ):
        completion_tokens = kargs.get("completion_tokens")
        if completion_tokens is None:
            completion_tokens = num_tokens_from_string(completion)
        prompt_tokens = kargs.get("prompt_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens
        id = kargs.get("id", f"chatcmpl-{str(time.time())}")
        finish_reason = kargs.get("finish_reason", "stop")
        created = kargs.get("created", int(time.time()))
        index = kargs.get("index", 0)
        openai_response = {
            "id": id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            "choices": [
                {
                    "delta": {
                        "role": "assistant",
                        "content": completion,
                    },
                    "index": index,
                    "finish_reason": finish_reason,
                }
            ],
        }
        return openai_response
