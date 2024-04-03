
# openai-style-api


 ***欢迎有兴趣的大佬提PR***

## 用途
屏蔽不同大模型API的差异，统一用openai api标准格式使用大模型, 也可以用来做api-key的二次分发管理; 配置化管理不同大模型调用参数，让你在使用大模型的时候只需关注 api-key 和 messages

## 功能

- [x] 支持多种大模型，当前已支持
  - [x] openai
  - [x] azure open ai
  - [x] claude-api 【api申请在等待列表，暂未测试】
  - [x] claude-web (将web端功能封装成openai api)
  - [x] 智谱ai
  - [x] bingchat(copilot)
  - [ ] 百度文心一言
  - [x] 讯飞星火
  - [x] gemini
  - [x] 通义千问
  - [ ] ...
- [x] 支持stream方式调用
- [x] 支持open ai的第三方代理服务，比如openai-sb等
- [x] 支持在线更新配置 `http://0.0.0.0:8090/`（这个前端页面和交互完全是用gpt写的 哈哈）
- [x] 支持负载均衡，一个key可轮训/随机/并行等访问多个模型
- [x] 支持按照model_name进行路由

**更新日志**

2024-04-03
- 支持通义千问
- 优化异常处理


## 快速开始

1. `git clone https://github.com/tian-minghui/openai-style-api.git` 拉取项目代码
2. `cp model-config.template model-config.json`  并按需修改配置文件model-config.json
 
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

4. 本地化部署直接 `pip install -r  requirements.txt` 后，运行 `python open-api.py`,  docker部署在目录下执行 `docker compose up -d`
5. 有了api-base: localhost:8090 和 api-key:f2b7295fc440db7f 可以使用了，下边列举了几种使用方式

## 使用方式

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

### openai库调用

    import openai

    openai.api_key = "f2b7295fc440db7f"
    openai.api_base = "http://localhost:8090/v1"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
    print(completion.choices[0].message.content)

### 第三方应用

[ChatGPT Next Web](https://github.com/Yidadaa/ChatGPT-Next-Web)
![Alt text](img/image.png)

## 配置示例
    [
    {
        "token": "f2b7295fc440db7f",
        "type": "azure",  // azure openai 模型
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
        "type": "openai", // openai 模型
        "config": {
            "api_base": "https://api.openai.com/v1/",
            "api_key": "sk-xxxxxx",
            "model": "gpt-3.5-turbo"
        }
    },
    {
        "token": "sb-ede1529390cc",
        "type": "proxy",  // openai 代理 
        "config": {
            "api_base": "https://api.openai-sb.com/v1/",
            "api_key": "sb-xxxxxx",
            "model": "gpt-3.5-turbo"
        }
    },
    {
        "token": "c115c8f5082",
        "type": "claude-web",  // claude-web 
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
        "type": "zhipu-api",  // 智谱API
        "config": {
            "api_key": "xxxxxx",
            "model": "chatglm_lite",
            "temperature": 0.8,
            "top_p": 0.7
        }
    },
    {
        "token": "7c7aa4a3549f11",
        "type": "xunfei-spark-api", // 讯飞星火API
        "config": {
            "app_id": "xxxx",
            "api_key": "xxxx",
            "api_secret": "xxxxxx",
            "api_model_version": "v2.0",
            "top_k": 5
        }
    },
    {
        "token": "7c7aa4a3549f12",
        "type": "router", // 路由  可以包含多个模型进行负载均衡
        "config": {
            "router_strategy": "round-robin", // 路由策略  round-robin 轮询   random 随机
            "token_pool": [   // 路由的token池
                "7c7aa4a3549f11",
                "7c7aa4a3549f5"
            ]
        }
    },
    {
        "token": "7c7aa4a3549f13",
        "type": "model-name-router", //根据req中的modelname进行路由, 可以方便的结合ChatGPT-Next-Web
        "config": {
            "model-2-token": {   // 路由的token池
                "spark-api-v2.0":"7c7aa4a3549f11",
                "chatglm_lite": "7c7aa4a3549f5",
                "router-round-robin": "7c7aa4a3549f12"
            }
        }
    },
    {
        "token": "gemini-7c7aa4a3549f5",
        "type": "gemini",
        "config": {
            "api_key": "xxxxx",
            "proxies": {
                "https": "http://localhost:7890"
            }
        }
    },
    {
        "token": "bing-7c7aa4a3549f5",
        "type": "bing-sydney",
        "config": {
            "cookie": "xxxxx",
            "style": "balanced"
        }
    },
    {
        "token":"qwen-111111xxxx",
        "type":"qwen",
        "config":{
            "api_key":"sk-xxxxxxxx",
            "model":"qwen-turbo"
        }
    }
    ]


## 项目部分代码来自于以下开源项目，感谢🙏
 - https://github.com/vsakkas/sydney.py
 - https://github.com/suqingdong/sparkapi