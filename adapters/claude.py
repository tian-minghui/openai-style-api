import json
from typing import Iterator
import requests
from adapters.base import ModelAdapter, post, stream
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from loguru import logger
from utils.util import num_tokens_from_string
import time

# 默认的model映射，不过request中的model参数会被config覆盖
model_map = {
    "gpt-3.5-turbo": "claude-instant-1",
    "gpt-3.5-turbo-0613": "claude-instant-1",
    "gpt-4": "claude-2",
    "gpt-4-0613": "claude-2",
}

stop_reason_map = {
    "stop_sequence": "stop",
    "max_tokens": "length",
}

role_map = {
    "system": "Human",
    "user": "Human",
    "assistant": "Assistant",
}

# 参考  https://github.com/jtsang4/claude-to-chatgpt


class ClaudeModel(ModelAdapter):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.pop("api_key", None)
        self.anthropic_version = kwargs.pop("anthropic-version", None)
        self.model = kwargs.pop("model", None)
        self.config_args = kwargs

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        """
        https://docs.anthropic.com/claude/reference/getting-started-with-the-api
        """
        openai_params = request.model_dump_json()
        claude_params = self.openai_to_claude_params(openai_params)
        url = "https://api.anthropic.com/v1/complete"
        headers = {
            "x-api-key": self.api_key,
            "accept": "application/json",
            "content-type": "application/json",
            "anthropic-version": self.anthropic_version,
        }
        if request.stream:
            response = stream(url, headers, claude_params)
            for chunk in response.iter_lines(chunk_size=1024):
                # 移除头部data: 字符
                decoded_line = chunk.decode("utf-8")
                logger.info(f"decoded_line: {decoded_line}")
                decoded_line = decoded_line.lstrip("data:").strip()
                json_line = json.loads(decoded_line)
                stop_reason = json_line.get("stop_reason")
                openai_response = None
                if stop_reason:
                    openai_response = self.claude_to_chatgpt_response_stream(
                        {
                            "completion": "",
                            "stop_reason": stop_reason,
                        }
                    )
                else:
                    completion = json_line.get("completion")
                    if completion:
                        openai_response = self.claude_to_chatgpt_response_stream(
                            decoded_line
                        )
                if openai_response:
                    yield ChatCompletionResponse(**openai_response)
        else:
            response = post(url, headers, claude_params)
            openai_response = self.claude_to_chatgpt_response(response)
            yield ChatCompletionResponse(**openai_response)

    def convert_messages_to_prompt(self, messages):
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            transformed_role = role_map[role]
            prompt += f"\n\n{transformed_role.capitalize()}: {content}"
        prompt += "\n\nAssistant: "
        return prompt

    def openai_to_claude_params(self, openai_params):
        model = model_map.get(openai_params["model"], "claude-2")
        messages = openai_params["messages"]

        prompt = self.convert_messages_to_prompt(messages)

        claude_params = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens_to_sample": 100000,
        }

        if openai_params.get("max_tokens"):
            claude_params["max_tokens_to_sample"] = openai_params["max_tokens"]

        if openai_params.get("stop"):
            claude_params["stop_sequences"] = openai_params.get("stop")

        if openai_params.get("temperature"):
            claude_params["temperature"] = openai_params.get("temperature")

        if openai_params.get("stream"):
            claude_params["stream"] = True

        claude_params.update(self.config_args)
        return claude_params

    def claude_to_chatgpt_response_stream(self, claude_response):
        completion = claude_response.get("completion", "")
        finish_reason = (
            stop_reason_map[claude_response.get("stop_reason")]
            if claude_response.get("stop_reason")
            else None
        )
        return self.completion_to_openai_stream_response(
            completion, self.model, finish_reason=finish_reason
        )

    def claude_to_chatgpt_response(self, claude_response):
        completion = claude_response.get("completion", "")
        finish_reason = (
            stop_reason_map[claude_response.get("stop_reason")]
            if claude_response.get("stop_reason")
            else None
        )
        return self.completion_to_openai_response(
            completion, self.model, finish_reason=finish_reason
        )
