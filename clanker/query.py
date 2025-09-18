import requests

# Set up the API endpoint and headers
url = "https://api.perplexity.ai/chat/completions"
headers = {
    "Authorization": "Bearer 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",  # Replace with your actual API key
    "Content-Type": "application/json"
}

# Define the request payload with streaming enabled
payload = {
    "model": "sonar-pro",
    "messages": [
        {"role": "user", "content": "What are the 7 colors of the rainbow?"}
    ],
    "stream": False  # Enable streaming for real-time responses
}

response = requests.post(url, headers=headers, json=payload, stream=True)
data = response.json()
print(data["choices"][0]["message"]["content"])
