"""
llm_connector.py
Handles all communication with the Groq API (Llama 4 Scout).
"""
from groq import Groq


class LLMConnector:
    def __init__(self, key_path="E:/Oishee/Thesis/groq_key.txt",
        
                 model="openai/gpt-oss-120b"):
        with open(key_path, "r") as f:
            api_key = f.read().strip()
        self.client = Groq(api_key=api_key)
        self.model = model

    def ask(self, prompt, system_prompt=None, temperature=0.2):
        """Send a prompt to the LLM and return the text response."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=800,
        )
        return response.choices[0].message.content


# Quick test when run directly
if __name__ == "__main__":
    llm = LLMConnector()
    print("Testing LLM connection...\n")

    answer = llm.ask(
        prompt="A patient has a respiratory rate of 24, systolic BP of 95, and confusion. "
               "Based on qSOFA, briefly assess sepsis risk in 2 sentences.",
        system_prompt="You are a clinical reasoning assistant. Be concise and precise."
    )
    print("LLM RESPONSE:")
    print(answer)