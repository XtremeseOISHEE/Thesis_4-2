from groq import Groq

client = Groq(api_key=open("E:/Oishee/Thesis/groq_key.txt").read().strip())

response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[
        {"role": "user", "content": "What are the main diagnostic criteria for sepsis? Answer in 3 bullet points."}
    ]
)

print(response.choices[0].message.content)