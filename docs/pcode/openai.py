import requests
import json

# 替换为您的 OpenAI API 密钥
openai_api_key = "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"

# API 端点 URL
url = "https://api.openai.com/v1/images/generations"

# 请求头部信息
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}"
}

# 请求参数
data = {
    "prompt": "Steven Jobs has a trip in  disney park.",
    "n": 2,
    "size": "1024x1024"
}

# 发送 POST 请求
response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)

# 输出响应结果
print(response.json())














# import os
# import openai
# openai.organization = "org-GYUrBjscrA3TTultt5cCU78o"
# openai.api_key = "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"
# openai.Model.list()

# import os
# import openai

# openai.api_key = "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"

# response = openai.Completion.create(
#   model="text-davinci-003",
#   prompt="Translate this into 1. French, 2. Spanish and 3. Japanese:\n\nWhat rooms do you have available?\n\n1.",
#   temperature=0.3,
#   max_tokens=100,
#   top_p=1,
#   frequency_penalty=0,
#   presence_penalty=0
# )