"""
llm_connector.py
Handles all communication with the LLM.
Currently uses OpenRouter (OpenAI-compatible) with GPT-OSS 120B -- no daily
token limit. The previous Groq implementation is kept commented as a fallback.
"""
import time

from openai import (
    OpenAI,
    APIConnectionError,
    APITimeoutError,
    RateLimitError,
    InternalServerError,
)
# from groq import Groq  # (fallback) previous provider


class LLMConnector:
    def __init__(self, key_path="E:/Oishee/Thesis/openrouter_key.txt",
                 model="openai/gpt-oss-120b"):
        with open(key_path, "r") as f:
            api_key = f.read().strip()
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        # --- Groq fallback (previous provider) ---
        # from groq import Groq
        # with open("E:/Oishee/Thesis/groq_key.txt", "r") as f:
        #     api_key = f.read().strip()
        # self.client = Groq(api_key=api_key)
        # self.model = model

    def ask(self, prompt, system_prompt=None, temperature=0.2):
        """Send a prompt to the LLM and return the text response.

        Guards against the model returning None content (empty completion):
        retries, then returns "" so a stray empty response cannot crash the
        pipeline (e.g. check_hop's .split or ChromaDB's retrieve, which reject
        None). Also retries on transient network/API errors (connection drop,
        timeout, rate limit, server error) with a 5s pause -- resilience for
        unstable internet. Up to 3 attempts total; then returns "" (safe
        sentinel). Non-transient errors (auth, bad request) are NOT retried so
        real config problems surface instead of being masked.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        retryable = (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError)
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=800,
                )
            except retryable:
                # Transient network/API error -- wait and retry.
                if attempt < 2:
                    time.sleep(5)
                    continue
                return ""  # retries exhausted -- safe fallback
            content = response.choices[0].message.content
            if content is not None:
                return content
            # None content: retry within the same 3-attempt budget (no wait).

        return ""  # 3 attempts exhausted (errors or None content) -- safe fallback


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
