<p align="right">
   <a href="./README.md">中文</a> | <strong>English</strong> 
</p>

# openai-style-api

## Purpose
Shield the differences between different large model APIs and use large models in a unified openai API standard format; Manage different large model call parameters in a configurable way, so that you only need to care about api-key and messages when using large models.

## Features

- Support multiple large models, currently supported
  - [x] openai
  - [x] azure open ai
  - [x] claude-api 【api application is on the waiting list, not tested yet】
  - [x] claude-web (encapsulate web functions into openai api)
  - [x] 智谱ai
- Support stream mode calling
- Support third-party proxy services for open ai, such as openai-sb

## TODO

- [ ] Configuration update interface
- [ ] Support more large models
  - [ ] bingchat
  - [x] 智谱ai
  - [ ] 百度文心一言
  - [ ] 讯飞星火
  - [ ] ...
  
## Quick start

1. Clone the project
2. `cp model-config.template model-config.json` and modify the configuration file model-config.json as needed

        {
          "token": "f2b7295fc440db7f",
          "type": "azure",
          "config": {
              "api_base": "https://xxxx.openai.azure.com/",
              "deployment_id": "xxxx",
              "api_version": "2023-05-15",
              "api_key": "xxxx",
              "temperature": 0.8
          }
        }
        
3. For local deployment, run `pip install -r requirements.txt` and then run `python open-api.py`. For docker deployment, execute `docker compose up -d` in the directory.
4. With api-base: localhost:8090 and api-key: f2b7295fc440db7f, you can start using it. Here are some examples:

## Usage

### curl

    curl http://localhost:8090/v1/chat/completions \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer f2b7295fc440db7f" \
          -d '{
            "messages": [
              {
                "role": "system",
                "content": "You are a helpful assistant."
              },
              {
                "role": "user",
                "content": "Hello!"
              }
            ]
          }'

### Call with openai library

    import openai

    openai.api_key = "f2b7295fc440db7f"
    openai.api_base = "http://localhost:8090/v1"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
    print(completion.choices[0].message.content)

### Third party applications 

[ChatGPT Next Web](https://github.com/Yidadaa/ChatGPT-Next-Web)
![Alt text](img/image.png)


## config example
    [
    {
        "token": "f2b7295fc440db7f",
        "type": "azure",
        "config": {
            "api_base": "https://xxxx.openai.azure.com/",
            "deployment_id": "gpt-35-turbo",
            "api_version": "2023-05-15",
            "api_key": "xxxxxx",
            "temperature": 0.8
        }
    },
    {
        "token": "GxqT3BlbkFJj",
        "type": "openai",
        "config": {
            "api_base": "https://api.openai.com/v1/",
            "api_key": "sk-xxxxxx",
            "model": "gpt-3.5-turbo"
        }
    },
    {
        "token": "sb-ede1529390cc",
        "type": "proxy",
        "config": {
            "api_base": "https://api.openai-sb.com/v1/",
            "api_key": "sb-xxxxxx",
            "model": "gpt-3.5-turbo"
        }
    },
    {
        "token": "c115c8f5082",
        "type": "claude-web",
        "config": {
            "cookie": "xxxxxx",
            "proxies": {
                "https": "http://localhost:7890"
            },
            "conversation_id": "xxxxxx",
            "prompt": "The information in [] is the context of the conversation. Please ignore the JSON format of the context during the conversation and answer the user's latest conversation: {newMessage} \n {history}",
            "single_conversation": true
        }
    },
    {
        "token": "7c7aa4a3549f5",
        "type": "zhipu-api",
        "config": {
            "api_key": "xxxxxx",
            "model": "chatglm_lite",
            "temperature": 0.8,
            "top_p": 0.7
        }
    }
]