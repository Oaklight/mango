"""Unified LLM inference via OpenAI-compatible API.

Supports any model accessible through an OpenAI-compatible endpoint,
including Argonne-hosted models. Supports both the chat completions API
and the responses API.
"""

from __future__ import annotations

import logging
import os

import tiktoken
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential

from mango.inference.models._base import BaseModel

logger = logging.getLogger(__name__)


class OpenAIModel(BaseModel):
    """LLM client using the OpenAI SDK against any compatible endpoint.

    Args:
        model_name: Model identifier (e.g., "gpt-4o", "claude-sonnet-4-20250514").
        temperature: Sampling temperature.
        max_tokens: Maximum tokens to generate.
        base_url: API base URL. Defaults to OPENAI_BASE_URL env var.
        api_key: API key. Defaults to OPENAI_API_KEY env var.
        api_mode: "chat" for chat completions, "responses" for responses API.
        system_prompt: System prompt prepended to all requests.
        tokenizer_model: tiktoken model name for tokenization.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
        base_url: str | None = None,
        api_key: str | None = None,
        api_mode: str = "chat",
        system_prompt: str = "You are a helpful assistant.",
        tokenizer_model: str = "gpt-4o",
    ) -> None:
        super().__init__(model_name, temperature, max_tokens)
        self.api_mode = api_mode
        self.system_prompt = system_prompt
        self.client = OpenAI(
            base_url=base_url or os.getenv("OPENAI_BASE_URL"),
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
        )
        self.tokenizer = tiktoken.encoding_for_model(tokenizer_model)

    @retry(
        wait=wait_random_exponential(min=5, max=60),
        stop=stop_after_attempt(6),
    )
    def _query_chat(self, prompt: str) -> str:
        """Query using chat completions API."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""

    @retry(
        wait=wait_random_exponential(min=5, max=60),
        stop=stop_after_attempt(6),
    )
    def _query_responses(self, prompt: str) -> str:
        """Query using the responses API."""
        response = self.client.responses.create(
            model=self.model_name,
            input=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        return "".join(
            block.text
            for item in response.output
            if item.type == "message"
            for block in item.content
            if block.type == "output_text"
        )

    def query_model(self, prompt_list: list[str]) -> list[str]:
        """Send prompts to the model and return responses."""
        results = []
        query_fn = (
            self._query_chat if self.api_mode == "chat" else self._query_responses
        )
        for prompt in prompt_list:
            result = query_fn(prompt)
            results.append(result)
        return results

    def cutoff_input(
        self, text: str, max_token_num: int, max_step_num: int
    ) -> tuple[str, int]:
        """Truncate walkthrough text to fit token and step limits."""
        cut_off_step_num = float("inf")
        enc = self.tokenizer.encode(text)
        if len(enc) > max_token_num:
            cut_off_text = self.tokenizer.decode(enc[:max_token_num])
            cut_off_step_num = int(cut_off_text.split("NUM: ")[-2].split("\n")[0])
        if cut_off_step_num > max_step_num:
            cut_off_step_num = max_step_num
        cut_off_text = text.split(f"NUM: {cut_off_step_num + 1}")[0]
        cut_off_text = "\n".join(cut_off_text.split("\n")[:-1])
        return cut_off_text, int(cut_off_step_num)
