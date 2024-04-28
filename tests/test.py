import traceback
import openai
from openai import OpenAI

client = None
import sys
import json
import time
from loguru import logger


def single_message_test(**kwargs):
    print(f"----------single message test {kwargs}----------")
    try:
        completion = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "你好"}],
        **kwargs)
        if kwargs.get("stream"):
            for chunk in completion:
                print(chunk)
        else:
            print(completion)
    except openai.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except Exception as e:
        s = traceback.format_exc()
        print(s)
        logger.error(f"An unexpected error occurred: {e}")
        pass


def multiple_messages_test(**kwargs):
    print(f"----------multiple messages test {kwargs}----------")
    try:
        completion = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个旅行专家, 能够帮我们制定旅行计划"},
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好!很高兴认识你。"},
            {"role": "user", "content": "你是谁？"},
        ],
        **kwargs)
        if kwargs.get("stream"):
            for chunk in completion:
                print(chunk)
        else:
            print(completion)
    except Exception as e:
        s = traceback.format_exc()
        print(s)
        logger.error(f"Exception: {e}")


if __name__ == "__main__":
    api_key = sys.argv[1]
    client = OpenAI(api_key=api_key, base_url="http://localhost:8090/v1")
    # single_message_test()
    # time.sleep(2)
    # single_message_test(stream=True)
    # time.sleep(2)
    multiple_messages_test()
    time.sleep(2)
    multiple_messages_test(stream=True)
