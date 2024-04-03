from typing import Iterator
from adapters.base import ModelAdapter
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from loguru import logger
from utils.util import num_tokens_from_string
from clients.claude_web_client import ClaudeWebClient
import time


class ClaudeWebModel(ModelAdapter):
    def __init__(self, **kwargs):
        self.cookie = kwargs.pop("cookie", None)
        self.proxies = kwargs.pop("proxies", None)
        self.client = ClaudeWebClient(self.cookie, proxies=self.proxies)
        self.prompt = kwargs.pop(
            "prompt",
            "The information in [] is the context of the conversation. \
                                 Please ignore the JSON format of the context \
                                 during the conversation and answer the user's latest conversation: {newMessage} \n {history}",
        )
        self.single_conversation = kwargs.pop("single_conversation", False)
        if self.single_conversation:
            self.conversation_id = kwargs.pop("conversation_id", None)
            if self.conversation_id is None:
                self.conversation_id = self.client.create_new_chat()["uuid"]
        self.config_args = kwargs

    def convertOpenAIParams2ClaudePrompt(self, request: ChatCompletionRequest) -> str:
        messages = request.messages
        if len(messages) < 2:
            return messages[0].content
        newMessage = messages[-1].content
        history = [
            message.model_dump(exclude_none=True)
            for message in messages[: len(messages) - 1]
        ]
        return self.prompt.format(newMessage=newMessage, history=history)

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        claudePrompt = self.convertOpenAIParams2ClaudePrompt(request)
        conversation_id = self.conversation_id
        if not self.single_conversation:
            conversation_id = self.client.create_new_chat()["uuid"]
        response = self.client.send_message(claudePrompt, conversation_id)
        if request.stream:  # 假的stream
            resp = self.claude_to_openai_stream_response(response)
        else:
            resp = self.claude_to_openai_response(response)
        logger.info(
            f"ClaudeWebModel req:{request}, conversation_id:{conversation_id}, claudePrompt:{claudePrompt} ,resp:{resp}"
        )
        yield ChatCompletionResponse(**resp)

    def claude_to_openai_stream_response(self, completion: str):
        return self.completion_to_openai_stream_response(completion)

    def claude_to_openai_response(self, completion: str):
        return self.completion_to_openai_response(completion)
