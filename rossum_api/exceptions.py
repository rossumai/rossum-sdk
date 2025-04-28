from __future__ import annotations


class APIClientError(Exception):
    def __init__(self, method, url, status_code, error):
        self.method = method
        self.url = url
        self.status_code = status_code
        self.error = error

    def __str__(self):
        return f"[{self.method}] {self.url} - HTTP {self.status_code} - {self.error}"
