from __future__ import annotations

import httpx

from seekr.tools.base import ToolResult

BASE_URL = "https://opendart.fss.or.kr/api"

# DART API status codes
STATUS_OK = "000"
STATUS_NO_DATA = "013"


class DartClient:
    """DART Open API client.

    DART (Data Analysis, Retrieval and Transfer System) is the Korean
    financial disclosure system operated by FSS (Financial Supervisory Service).

    API docs: https://opendart.fss.or.kr/guide/main.do
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=BASE_URL,
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> DartClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def _request(
        self, endpoint: str, params: dict[str, str]
    ) -> ToolResult:
        params["crtfc_key"] = self._api_key
        try:
            resp = await self._client.get(endpoint, params=params)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            return ToolResult(
                success=False,
                error=f"HTTP {e.response.status_code}: {e.response.text}",
            )
        except httpx.RequestError as e:
            return ToolResult(success=False, error=f"Request failed: {e}")

        data = resp.json()
        status = data.get("status", "")

        if status == STATUS_NO_DATA:
            return ToolResult(success=True, data=[], metadata={"status": status})

        if status != STATUS_OK:
            message = data.get("message", "Unknown DART API error")
            return ToolResult(
                success=False,
                error=f"DART API error ({status}): {message}",
                metadata={"status": status},
            )

        return ToolResult(success=True, data=data, metadata={"status": status})

    async def search_company(self, corp_name: str) -> ToolResult:
        """Search for a company by name and return its corp_code.

        Args:
            corp_name: Company name in Korean (e.g. "삼성전자")
        """
        # DART corpCode API returns an XML zip file, so we use the
        # disclosure search and extract corp_code from results instead.
        # Alternative: use the company search endpoint.
        result = await self._request(
            "/list.json",
            {
                "corp_name": corp_name,
                "page_count": "5",
                "page_no": "1",
            },
        )
        if not result.success:
            return result

        if not isinstance(result.data, dict):
            return ToolResult(
                success=True,
                data=[],
                metadata={"message": f"No company found for '{corp_name}'"},
            )

        items = result.data.get("list", [])
        if not items:
            return ToolResult(
                success=True,
                data=[],
                metadata={"message": f"No company found for '{corp_name}'"},
            )

        seen: set[str] = set()
        companies = []
        for item in items:
            code = item.get("corp_code", "")
            if code and code not in seen:
                seen.add(code)
                companies.append(
                    {
                        "corp_code": code,
                        "corp_name": item.get("corp_name", ""),
                        "stock_code": item.get("stock_code", ""),
                    }
                )

        return ToolResult(success=True, data=companies)

    async def get_disclosures(
        self,
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
        page_count: int = 10,
    ) -> ToolResult:
        """Get disclosure list for a company.

        Args:
            corp_code: DART company code (8 digits)
            bgn_de: Start date (YYYYMMDD)
            end_de: End date (YYYYMMDD)
            page_count: Number of results per page (max 100)
        """
        params: dict[str, str] = {
            "corp_code": corp_code,
            "page_count": str(min(page_count, 100)),
        }
        if bgn_de:
            params["bgn_de"] = bgn_de
        if end_de:
            params["end_de"] = end_de

        result = await self._request("/list.json", params)
        if not result.success:
            return result

        items = result.data.get("list", [])
        disclosures = [
            {
                "rcept_no": item.get("rcept_no", ""),
                "corp_name": item.get("corp_name", ""),
                "report_nm": item.get("report_nm", ""),
                "rcept_dt": item.get("rcept_dt", ""),
                "flr_nm": item.get("flr_nm", ""),
            }
            for item in items
        ]

        return ToolResult(
            success=True,
            data=disclosures,
            metadata={"total_count": result.data.get("total_count", 0)},
        )

    async def get_disclosure_detail(self, rcept_no: str) -> ToolResult:
        """Get detailed information about a specific disclosure.

        Args:
            rcept_no: DART receipt number (14 digits)
        """
        return await self._request(
            "/document.json",
            {"rcept_no": rcept_no},
        )

    async def get_financials(
        self,
        corp_code: str,
        bsns_year: str,
        reprt_code: str = "11011",
    ) -> ToolResult:
        """Get financial statements for a company.

        Args:
            corp_code: DART company code (8 digits)
            bsns_year: Business year (YYYY)
            reprt_code: Report type code
                - "11013": 1Q report
                - "11012": Half-year report
                - "11014": 3Q report
                - "11011": Annual report (default)
        """
        result = await self._request(
            "/fnlttSinglAcntAll.json",
            {
                "corp_code": corp_code,
                "bsns_year": bsns_year,
                "reprt_code": reprt_code,
                "fs_div": "CFS",  # Consolidated financial statements
            },
        )
        if not result.success:
            return result

        items = result.data.get("list", [])
        financials = [
            {
                "account_nm": item.get("account_nm", ""),
                "thstrm_amount": item.get("thstrm_amount", ""),
                "frmtrm_amount": item.get("frmtrm_amount", ""),
                "bfefrmtrm_amount": item.get("bfefrmtrm_amount", ""),
                "sj_nm": item.get("sj_nm", ""),
            }
            for item in items
        ]

        return ToolResult(success=True, data=financials)
