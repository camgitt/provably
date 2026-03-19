"""Generic HTTP endpoint provider — test any deployed agent via its URL."""

from __future__ import annotations

import json
import urllib.request
import urllib.error

from proofagent.providers.base import Provider
from proofagent.result import LLMResult, ToolCall


class EndpointProvider(Provider):
    """Send prompts to any HTTP endpoint and parse the response.

    Supports OpenAI-compatible chat format and a simpler prompt format.
    Works with urllib so there are zero extra dependencies.
    """

    def __init__(
        self,
        url: str,
        headers: dict | None = None,
        format: str = "openai",
        timeout: int = 120,
    ):
        self.url = url.rstrip("/")
        self.format = format  # "openai" or "simple"
        self.timeout = timeout
        self._headers = headers or {}
        # Always set Content-Type if not provided
        if "Content-Type" not in self._headers:
            self._headers["Content-Type"] = "application/json"

    def name(self) -> str:
        return "endpoint"

    def complete(
        self,
        messages: list[dict],
        model: str | None = None,
        tools: list[dict] | None = None,
        **kwargs,
    ) -> LLMResult:
        start = self._time()

        # Build request body based on format
        if self.format == "simple":
            # Extract the last user message as the prompt
            prompt_text = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    prompt_text = msg.get("content", "")
                    break
            body = {"prompt": prompt_text}
        else:
            # OpenAI-compatible chat format
            body = {"messages": messages}
            if model and model != "endpoint":
                body["model"] = model

        if tools:
            body["tools"] = tools

        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=data,
            headers=self._headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode("utf-8")[:200]
            except Exception:
                pass
            raise RuntimeError(
                f"Endpoint returned HTTP {e.code}: {body_text}"
            ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Could not connect to endpoint {self.url}: {e.reason}"
            ) from e

        latency = self._time() - start

        # Parse response — try multiple formats
        text = ""
        tool_calls: list[ToolCall] = []

        try:
            resp_data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            # Not JSON — treat the entire response body as text
            return LLMResult(
                text=raw.strip(),
                cost=0.0,
                latency=latency,
                model=model or "endpoint",
                provider="endpoint",
            )

        # Try OpenAI format: response.choices[0].message.content
        if isinstance(resp_data, dict) and "choices" in resp_data:
            choices = resp_data["choices"]
            if choices and isinstance(choices, list):
                message = choices[0].get("message", {})
                text = message.get("content", "")

                # Parse tool calls if present
                for tc in message.get("tool_calls", []):
                    func = tc.get("function", {})
                    args = func.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except (json.JSONDecodeError, ValueError):
                            args = {"raw": args}
                    tool_calls.append(
                        ToolCall(name=func.get("name", ""), args=args)
                    )

                # Extract token usage if present
                usage = resp_data.get("usage", {})
                return LLMResult(
                    text=text,
                    tool_calls=tool_calls,
                    cost=0.0,
                    latency=latency,
                    model=resp_data.get("model", model or "endpoint"),
                    provider="endpoint",
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                )

        # Try simple format: response.text / response.content / response.output
        for key in ("text", "content", "output", "response", "result", "answer"):
            if isinstance(resp_data, dict) and key in resp_data:
                val = resp_data[key]
                if isinstance(val, str):
                    text = val
                    break
                elif isinstance(val, dict) and "content" in val:
                    text = val["content"]
                    break

        # If still empty, try to get something useful
        if not text and isinstance(resp_data, dict):
            # Try message.content (some APIs wrap in message)
            if "message" in resp_data and isinstance(resp_data["message"], dict):
                text = resp_data["message"].get("content", "")

        # Last resort: dump the whole response
        if not text:
            text = json.dumps(resp_data) if isinstance(resp_data, dict) else str(resp_data)

        return LLMResult(
            text=text,
            tool_calls=tool_calls,
            cost=0.0,
            latency=latency,
            model=model or "endpoint",
            provider="endpoint",
        )
