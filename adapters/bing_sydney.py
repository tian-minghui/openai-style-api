import asyncio
from typing import Iterator
from adapters.base import ModelAdapter
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse
from clients.sydney import SydneyClient
from loguru import logger


class BingSydneyModel(ModelAdapter):
    def __init__(self, **kwargs):
        self.cookie = kwargs.pop("cookie")
        self.style = kwargs.pop("style")

        self.proxy = kwargs.pop("proxy", None)
        # 没找到合适的prompt 此prompt返回结果   My mistake, I can’t give a response to that right now. Let’s try a different topic.
        # self.prompt = kwargs.pop(
        #     "prompt",
        #     "The information in [] is the context of the conversation. \
        #                          Please ignore the JSON format of the context \
        #                          during the conversation and answer the user's latest conversation: {newMessage} \n {history}",
        # )
        self.config_args = kwargs

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        """
        返回一个迭代器对象
         stream为false   第一个就是结果
        """

        if request.stream:
            result = asyncio.run(self.__chat_stream_help(request))
            for item in result:
                logger.info(item)
                yield ChatCompletionResponse(
                    **self.completion_to_openai_stream_response(item, request.model)
                )
        else:
            async_gen = self.__chat_help(request)
            result = asyncio.run(async_gen)
            logger.info(result)
            yield ChatCompletionResponse(
                **self.completion_to_openai_response(result, request.model)
            )

    def convertOpenAIParams2Prompt(self, request: ChatCompletionRequest) -> str:
        messages = request.messages
        if len(messages) < 2:
            return messages[0].content
        # 暂不支持 历史message， 默认取最近的message
        msg = messages[-1].content
        logger.warning(f"暂不支持对话历史，取最近一条对话记录：{msg}")
        return msg

    async def __chat_help(self, request: ChatCompletionRequest):
        prompt = self.convertOpenAIParams2Prompt(request)
        logger.info("prompt:{}".format(prompt))
        async with SydneyClient(self.style, self.cookie, self.proxy) as client:
            completion = await client.ask(prompt)
            return completion

    async def __chat_stream_help(self, request: ChatCompletionRequest):
        prompt = self.convertOpenAIParams2Prompt(request)
        logger.info("prompt:{}".format(prompt))
        async with SydneyClient(self.style, self.cookie, self.proxy) as client:
            return [
                response_token async for response_token in client.ask_stream(prompt)
            ]
