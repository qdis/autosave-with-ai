# ABOUTME: HTTP client for OpenAI-compatible Chat Completions and Responses APIs
# ABOUTME: Pure stdlib implementation (http.client, json, urllib.parse) compatible with Python 3.3+

import http.client
import json
from urllib.parse import urlparse


class OpenAIHTTPError(Exception):
    """Exception raised for HTTP errors when calling OpenAI-compatible APIs"""
    pass


def _post_json(base_url, path, body, headers, timeout=30):
    """
    Send a JSON POST to base_url + path using only the stdlib and return parsed JSON.
    Raises OpenAIHTTPError on HTTP >= 400 or invalid JSON.

    Args:
        base_url: Base URL like "https://api.openai.com/v1"
        path: Relative path like "/chat/completions" or "/responses"
        body: Dict to send as JSON body
        headers: Dict of HTTP headers
        timeout: Timeout in seconds (default 30)

    Returns:
        Parsed JSON response as dict
    """
    # Build full URL
    if not base_url:
        raise ValueError("base_url must not be empty")

    base_url = base_url.rstrip("/")
    if not path.startswith("/"):
        path = "/" + path

    full_url = base_url + path
    parsed = urlparse(full_url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Unsupported URL scheme: {}".format(parsed.scheme))

    conn_cls = http.client.HTTPSConnection if parsed.scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(parsed.netloc, timeout=timeout)

    # Ensure headers
    headers = dict(headers or {})
    headers.setdefault("Content-Type", "application/json")

    body_bytes = json.dumps(body).encode("utf-8")
    request_path = parsed.path or "/"
    if parsed.query:
        request_path += "?" + parsed.query

    conn.request("POST", request_path, body=body_bytes, headers=headers)
    resp = conn.getresponse()
    resp_bytes = resp.read()
    conn.close()

    text = resp_bytes.decode("utf-8", errors="replace")

    if resp.status >= 400:
        # Try to parse error JSON for debugging
        try:
            error_json = json.loads(text)
        except Exception:
            error_json = None
        error_msg = text if not error_json else str(error_json)
        raise OpenAIHTTPError(
            "HTTP {} from {}: {}".format(resp.status, request_path, error_msg)
        )

    try:
        return json.loads(text)
    except Exception as e:
        raise OpenAIHTTPError("Failed to parse JSON response: {}; raw={}".format(e, repr(text)))


def chat_completion(base_url, api_key, model, messages, max_tokens=None, temperature=None,
                   auth_header_name="Authorization", auth_header_prefix="Bearer "):
    """
    Call /v1/chat/completions on an OpenAI-compatible server.

    Args:
        base_url: Base URL like "https://api.openai.com/v1"
        api_key: API key for authentication
        model: Model name (e.g. "gpt-4o", "gpt-4.1-mini")
        messages: List of message dicts with "role" and "content"
        max_tokens: Optional max tokens for response
        temperature: Optional temperature for sampling
        auth_header_name: Header name for auth (default "Authorization")
        auth_header_prefix: Prefix for auth value (default "Bearer ")

    Returns:
        Full JSON response as dict. Use extract_chat_content() to get text.
    """
    headers = {
        auth_header_name: "{}{}".format(auth_header_prefix, api_key),
    }

    body = {
        "model": model,
        "messages": messages,
    }

    # Only add optional params if explicitly set
    if max_tokens is not None:
        body["max_tokens"] = max_tokens
    if temperature is not None:
        body["temperature"] = temperature

    return _post_json(base_url, "/chat/completions", body, headers)


def extract_chat_content(response):
    """
    Extracts choices[0].message.content from a Chat Completions response.

    Args:
        response: Response dict from chat_completion()

    Returns:
        Assistant's message content as string
    """
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise OpenAIHTTPError(
            "Unexpected chat completion response format: {}; response={}".format(e, repr(response))
        )


def responses_create(base_url, api_key, model, input_value, max_output_tokens=None, temperature=None,
                    auth_header_name="Authorization", auth_header_prefix="Bearer "):
    """
    Call /v1/responses on an OpenAI-compatible server.

    Args:
        base_url: Base URL like "https://api.openai.com/v1"
        api_key: API key for authentication
        model: Model name (e.g. "gpt-4o")
        input_value: Either a string or a list of message dicts with "type", "role", "content"
        max_output_tokens: Optional max tokens for response
        temperature: Optional temperature for sampling
        auth_header_name: Header name for auth (default "Authorization")
        auth_header_prefix: Prefix for auth value (default "Bearer ")

    Returns:
        Full JSON response as dict. Use extract_response_text() to get text.
    """
    headers = {
        auth_header_name: "{}{}".format(auth_header_prefix, api_key),
    }

    body = {
        "model": model,
        "input": input_value,
    }

    if max_output_tokens is not None:
        body["max_output_tokens"] = max_output_tokens
    if temperature is not None:
        body["temperature"] = temperature

    return _post_json(base_url, "/responses", body, headers)


def extract_response_text(response):
    """
    Extracts the main text from a Responses API response.

    Priority:
      1) top-level 'output_text' if present
      2) first 'output[0].content[0].text'

    Args:
        response: Response dict from responses_create()

    Returns:
        Assistant's response text as string
    """
    # 1) Prefer `output_text` if available
    text = response.get("output_text")
    if isinstance(text, str) and text.strip():
        return text

    # 2) Fallback to first message content
    try:
        return response["output"][0]["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise OpenAIHTTPError(
            "Unexpected Responses API format: {}; response={}".format(e, repr(response))
        )
