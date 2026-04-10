"""Abstract base class for MANGO LLM inference models."""

from __future__ import annotations

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseModel(abc.ABC):
    """Base class for all MANGO inference models.

    Subclasses must implement query_model() and cutoff_input().
    Prompt building for route_finding and desti_finding is shared.
    """

    def __init__(
        self,
        model_name: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abc.abstractmethod
    def query_model(self, prompt_list: list[str]) -> list[str]:
        """Send prompts to the model and return responses."""
        ...

    @abc.abstractmethod
    def cutoff_input(
        self, text: str, max_token_num: int, max_step_num: int
    ) -> tuple[str, int]:
        """Truncate input text to fit within token/step limits."""
        ...

    def process(
        self, samples: list[dict[str, Any]], task_type: str
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Route to the appropriate task handler."""
        if task_type == "route_finding":
            return self._route_finding(samples)
        elif task_type == "desti_finding":
            return self._desti_finding(samples)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

    def _build_context(self, sample: dict[str, Any]) -> str:
        """Build the shared context prefix from walkthrough and spaces."""
        walkthrough_text = sample["walkthrough_text"]
        prefix = f"!!! Here is a walkthrough of a text game:\n{walkthrough_text}"
        action_prompt = f"The allowed actions are: {sample['action_space_list']}."
        location_prompt = f"The list of locations are: {sample['location_space_list']}."
        return f"{prefix}\n\n{action_prompt}\n{location_prompt}"

    def _route_finding(
        self, samples: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Handle route finding task."""
        input_list = []
        for sample in samples:
            context = self._build_context(sample)
            question = (
                f'!!! Can you find a path from "{sample["src_node"]}" to '
                f'"{sample["dst_node"]}", and format the output as a python list '
                f"of python dictionary with keys 'location_before', 'action' and "
                f"'location_after'? Start your response with '['."
            )
            sample["question"] = question
            input_list.append(f"{context}\n{question}")

        try:
            raw_outputs = self.query_model(input_list)
        except Exception as e:
            logger.error("Model query failed: %s", e)
            raw_outputs = [f"Error: {e}"]

        return samples, raw_outputs

    def _desti_finding(
        self, samples: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Handle destination finding task."""
        input_list = []
        for sample in samples:
            context = self._build_context(sample)
            question = (
                f'!!! Starting from place "{sample["src_node"]}", perform a list '
                f"of action {sample['action_list']}, where are you now? Describe "
                f"the trajectory in a python list of python dictionary with keys "
                f"'location_before', 'action' and 'location_after'. Start your "
                f"response with '['."
            )
            sample["question"] = question
            input_list.append(f"{context}\n{question}")

        try:
            raw_outputs = self.query_model(input_list)
        except Exception as e:
            logger.error("Model query failed: %s", e)
            raw_outputs = [f"Error: {e}"]

        return samples, raw_outputs
