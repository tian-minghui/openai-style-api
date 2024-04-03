import json
import time
from typing import Dict, Iterator, List
import uuid
from adapters.base import ModelAdapter, post
from adapters.protocol import ChatCompletionRequest, ChatCompletionResponse, ChatMessage
from utils.util import num_tokens_from_string

"""

https://ai.google.dev/tutorials/rest_quickstart



 curl -x http://127.0.0.1:7890 https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key= \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "contents": [
        {"role":"user",
         "parts":[{
           "text": "你好"}]},
        {"role": "model",
         "parts":[{
           "text": "你好"}]},
        {"role": "user",
         "parts":[{
           "text": "你是谁？"}]},
      ]
    }'


{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "In the tranquil village of Étoiles-sur-Mer, nestled amidst the rolling hills of 17th-century France, lived a young girl named Marie. She was known for her kind heart, inquisitive nature, and an extraordinary bond with a magical backpack she inherited from her grandmother."
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_HATE_SPEECH",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
          "probability": "NEGLIGIBLE"
        }
      ]
    }
  ],
  "promptFeedback": {
    "safetyRatings": [
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "probability": "NEGLIGIBLE"
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "probability": "NEGLIGIBLE"
      },
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "probability": "NEGLIGIBLE"
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "probability": "NEGLIGIBLE"
      }
    ]
  }
}
"""


class GeminiAdapter(ModelAdapter):
    def __init__(self, **kwargs):
        super().__init__()
        self.api_key = kwargs.pop("api_key", None)
        self.prompt = kwargs.pop(
            "prompt", "You need to follow the system settings:{system}"
        )
        self.proxies = kwargs.pop("proxies", None)
        self.model = "gemini-pro"
        self.config_args = kwargs

    def chat_completions(
        self, request: ChatCompletionRequest
    ) -> Iterator[ChatCompletionResponse]:
        method = "generateContent"
        headers = {"Content-Type": "application/json"}
        # if request.stream:
        #     method = "streamGenerateContent"
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:{method}?key="
            + self.api_key
        )
        params = self.convert_2_gemini_param(request)
        response = post(url, headers=headers, proxies=self.proxies, params=params)
        if request.stream:  # 假的stream
            openai_response = self.response_convert_stream(response)
        else:
            openai_response = self.response_convert(response)
        yield ChatCompletionResponse(**openai_response)

    def response_convert_stream(self, data):
        completion = data["candidates"][0]["content"]["parts"][0]["text"]
        return self.completion_to_openai_stream_response(completion, self.model)

    def response_convert(self, data):
        completion = data["candidates"][0]["content"]["parts"][0]["text"]
        return self.completion_to_openai_response(completion, self.model)

    """
    [
        {"role":"user",
         "parts":[{
           "text": "你好"}]},
        {"role": "model",
         "parts":[{
           "text": "你好"}]},
        {"role": "user",
         "parts":[{
           "text": "你是谁？"}]},
      ]
    """

    def convert_messages_to_prompt(
        self, messages: List[ChatMessage]
    ) -> List[Dict[str, str]]:
        prompt = []
        for message in messages:
            role = message.role
            if role in ["function"]:
                raise Exception(f"不支持的功能:{role}")
            if role == "system":  # 将system转为user
                role = "user"
                content = self.prompt.format(system=message.content)
                prompt.append({"role": role, "parts": [{"text": content}]})
                prompt.append({"role": "model", "parts": [{"text": "ok"}]})
            elif role == "assistant":
                prompt.append({"role": "model", "parts": [{"text": message.content}]})
            else:
                content = message.content
                prompt.append({"role": role, "parts": [{"text": content}]})
        return prompt

    def convert_2_gemini_param(self, request: ChatCompletionRequest):
        contents = self.convert_messages_to_prompt(request.messages)
        param = {"contents": contents}
        return param
