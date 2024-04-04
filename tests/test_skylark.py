import traceback
import openai
import sys
import json
from loguru import logger


def single_message_test(**kwargs):
    print(f"----------single message test {kwargs}----------")
    try:
        completion = openai.ChatCompletion.create(
            model="Skylark2-pro-32k",
            messages=[{"role": "user", "content": "what is the capital of China？"}],
            **kwargs,
        )
        if kwargs.get("stream"):
            for chunk in completion:
                print(json.dumps(chunk, ensure_ascii=False))
        else:
            print(json.dumps(completion, ensure_ascii=False))
    except openai.APIError as e:
        # Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except Exception as e:
        s = traceback.format_exc()
        print(s)
        logger.error(f"An unexpected error occurred: {e}")
        pass


if __name__ == "__main__":
    api_key = sys.argv[1]
    openai.api_base = "http://localhost:8090/v1"
    openai.api_key = api_key
    # single_message_test()
    single_message_test(stream=True)
