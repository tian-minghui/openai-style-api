import openai

openai.api_key = "f2b7295fc440db7f"
openai.api_base = "http://localhost:8090/v1"

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
print(completion.choices[0].message.content)
