import copy
import json
from typing import Iterator
from adapters.base import ModelAdapter, serverError, post, stream
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from loguru import logger


class QWenAdapter(ModelAdapter):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.pop("api_key")
        self.model = kwargs.pop("model")
        self.config_args = kwargs
        self.url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:

        data = self.openai_req_2_qw_req(request)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if request.stream:
            headers["X-DashScope-SSE"] = "enable"
            response = stream(self.url, headers, params=data)
            index = 0
            error = False
            last_output = None
            for chunk in response.iter_lines(chunk_size=1024):
                # 移除头部data: 字符
                decoded_line = chunk.decode("utf-8")
                logger.info(f"decoded_line: {decoded_line}")
                if decoded_line.startswith("id"):
                    index = int(decoded_line.lstrip("id:").strip())
                if decoded_line.startswith("event:error"):
                    error = True
                if not decoded_line.startswith("data:"):
                    continue
                decoded_line = decoded_line.lstrip("data:").strip()
                if error:
                    raise serverError(decoded_line)
                output = json.loads(decoded_line)
                openai_resp = self.qw_resp_2_openai_resp_stream(
                    self.qw_stream_output_handle(output, last_output), index
                )
                last_output = output
                yield ChatCompletionResponse(**openai_resp)

        else:
            response = post(self.url, headers=headers, params=data)

            yield ChatCompletionResponse(**self.qw_resp_2_openai_resp(response))

    def qw_stream_output_handle(self, output: dict, last_output: dict):
        prompt_tokens = output["usage"]["input_tokens"]
        completion_tokens = output["usage"]["output_tokens"]
        content = output["output"]["choices"][0]["message"]["content"]
        try:
            last_prompt_tokens = last_output["usage"]["input_tokens"]
            last_completion_tokens = last_output["usage"]["output_tokens"]
            last_content = last_output["output"]["choices"][0]["message"]["content"]
        except:
            last_prompt_tokens = 0
            last_completion_tokens = 0
            last_content = ""
        new_output = copy.deepcopy(output)
        new_output["usage"]["input_tokens"] = prompt_tokens - last_prompt_tokens
        new_output["usage"]["output_tokens"] = completion_tokens - last_completion_tokens
        new_output["output"]["choices"][0]["message"]["content"] = content[
            len(last_content) :
        ]
        return new_output

    def qw_resp_2_openai_resp_stream(self, response: dict, index: int) -> dict:
        id = response["request_id"]
        prompt_tokens = response["usage"]["input_tokens"]
        completion_tokens = response["usage"]["output_tokens"]
        content = response["output"]["choices"][0]["message"]["content"]
        finish_reason = response["output"]["choices"][0]["finish_reason"]
        if finish_reason == "null":
            finish_reason = None
        return self.completion_to_openai_stream_response(
            content,
            self.model,
            index,
            finish_reason=finish_reason,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            id=id,
        )

    def qw_resp_2_openai_resp(self, response: dict) -> dict:
        id = response["request_id"]
        prompt_tokens = response["usage"]["input_tokens"]
        completion_tokens = response["usage"]["output_tokens"]
        content = response["output"]["choices"][0]["message"]["content"]
        return self.completion_to_openai_response(
            content,
            model=self.model,
            id=id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def openai_req_2_qw_req(self, request: ChatCompletionRequest) -> dict:
        d = {}
        if self.model:
            d["model"] = self.model
        else:
            d["model"] = request.model
        if len(self.config_args) > 0:
            d["parameters"] = self.config_args
        else:
            parameters = {}
            if request.temperature:
                parameters["temperature"] = request.temperature
            if request.top_p:
                parameters["top_p"] = request.top_p
            d["parameters"] = parameters
        d["parameters"]["result_format"] = "message"
        d["input"] = {}
        d["input"]["messages"] = [
            m.model_dump(exclude_none=True) for m in request.messages
        ]
        return d
