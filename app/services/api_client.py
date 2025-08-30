import asyncio
import httpx
from pydantic import BaseModel, Field, HttpUrl
from app.core.config import settings


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class QueryResult(BaseModel):
    id: str
    status: str
    data: dict = {}


class APIClient:
    def __init__(
        self,
        base_url: HttpUrl,
        api_key: str | None,
        timeout: float = 10.0,
        retries: int = 2,
        backoff: float = 0.5,
    ):
        self.base_url = str(base_url)
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        headers = kwargs.pop("headers", {})
        if self.api_key:
            headers["authorization"] = f"Bearer {self.api_key}"
        last_exc = None
        for attempt in range(self.retries + 1):
            try:
                resp = await self._client.request(
                    method, url, headers=headers, **kwargs
                )
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError(
                        "retryable", request=resp.request, response=resp
                    )
                return resp
            except Exception as exc:  # retry
                last_exc = exc
                if attempt == self.retries:
                    raise
                await asyncio.sleep(self.backoff * (2**attempt))
        assert last_exc
        raise last_exc

    async def run_query(self, payload: QueryRequest) -> QueryResult:
        # Replace "/api/query" with your real backend endpoint if different
        resp = await self._request("POST", "/api/query", json=payload.model_dict())
        data = resp.json()
        return QueryResult(**data)


api_client = APIClient(settings.API_BASE_URL, settings.API_KEY)
