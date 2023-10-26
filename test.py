import openai
import sys
import json

openai.api_base = "http://localhost:8090/v1"


def single_message_test(**kwargs):
    print(f"----------single message test {kwargs}----------")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": "你好"}], **kwargs
    )
    if kwargs.get("stream"):
        for chunk in completion:
            print(json.dumps(chunk, ensure_ascii=False))
    else:
        print(json.dumps(completion, ensure_ascii=False))


def multiple_messages_test(**kwargs):
    print(f"----------multiple messages test {kwargs}----------")
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好!很高兴认识你。我是AI助手。请告诉我,我如何为您提供帮助?"},
            {"role": "user", "content": "你能有什么样的能力？"},
        ],
        **kwargs,
    )
    if kwargs.get("stream"):
        for chunk in completion:
            print(json.dumps(chunk, ensure_ascii=False))
    else:
        print(json.dumps(completion, ensure_ascii=False))


if __name__ == "__main__":
    api_key = sys.argv[1]
    openai.api_key = api_key
    # single_message_test()
    # single_message_test(stream=True)
    multiple_messages_test()
    multiple_messages_test(stream=True)
