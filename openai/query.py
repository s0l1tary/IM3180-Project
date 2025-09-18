from openai import OpenAI

client = OpenAI(
  api_key="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"
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text);
# Note: store=True will save the response in your response history
# You can view your response history at https://platform.openai.com/response-history
# or retrieve it programmatically using the responses endpoint.