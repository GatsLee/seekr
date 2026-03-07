"""DART MCP Server — DART Open API tools for AI agents.

Usage:
    uv run python -m seekr.mcp.dart_server

Claude Code integration:
    claude mcp add seekr-dart -- uv run python -m seekr.mcp.dart_server
"""

from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP

from seekr.tools.dart.client import DartClient

mcp = FastMCP("seekr-dart")


def _get_client() -> DartClient:
    api_key = os.environ.get("DART_API_KEY", "")
    if not api_key:
        raise ValueError(
            "DART_API_KEY environment variable is required. "
            "Get your key at https://opendart.fss.or.kr/"
        )
    return DartClient(api_key=api_key)


def _to_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


@mcp.tool()
async def dart_company_search(corp_name: str) -> str:
    """DART에서 기업을 검색합니다. 기업의 고유번호(corp_code)를 반환합니다.

    Args:
        corp_name: 검색할 기업명 (예: "삼성전자", "카카오")
    """
    async with _get_client() as client:
        result = await client.search_company(corp_name)

    if not result.success:
        return f"오류: {result.error}"
    if not result.data:
        return f"'{corp_name}'에 해당하는 기업을 찾을 수 없습니다."
    return _to_json(result.data)


@mcp.tool()
async def dart_disclosures(
    corp_name: str,
    bgn_de: str | None = None,
    end_de: str | None = None,
) -> str:
    """한국 기업의 DART 공시 목록을 조회합니다.
    기업명으로 검색하여 자동으로 공시 목록을 반환합니다.

    Args:
        corp_name: 기업명 (예: "삼성전자")
        bgn_de: 검색 시작일 (YYYYMMDD 형식, 예: "20260101")
        end_de: 검색 종료일 (YYYYMMDD 형식, 예: "20260308")
    """
    async with _get_client() as client:
        # Step 1: Find corp_code from name
        search = await client.search_company(corp_name)
        if not search.success:
            return f"기업 검색 오류: {search.error}"
        if not search.data:
            return f"'{corp_name}'에 해당하는 기업을 찾을 수 없습니다."

        corp_code = search.data[0]["corp_code"]

        # Step 2: Get disclosures
        result = await client.get_disclosures(
            corp_code=corp_code,
            bgn_de=bgn_de,
            end_de=end_de,
        )

    if not result.success:
        return f"공시 조회 오류: {result.error}"
    if not result.data:
        return f"'{corp_name}'의 해당 기간 공시가 없습니다."

    return _to_json(
        {
            "corp_name": corp_name,
            "corp_code": corp_code,
            "total_count": result.metadata.get("total_count", 0),
            "disclosures": result.data,
        }
    )


@mcp.tool()
async def dart_disclosure_detail(rcept_no: str) -> str:
    """특정 공시의 상세 내용을 조회합니다.

    Args:
        rcept_no: DART 접수번호 (14자리, 예: "20260305000123")
    """
    async with _get_client() as client:
        result = await client.get_disclosure_detail(rcept_no)

    if not result.success:
        return f"공시 상세 조회 오류: {result.error}"
    return _to_json(result.data)


@mcp.tool()
async def dart_financials(
    corp_name: str,
    year: str,
    report_type: str = "annual",
) -> str:
    """기업의 재무제표를 조회합니다.
    기업명으로 검색하여 자동으로 재무제표를 반환합니다.

    Args:
        corp_name: 기업명 (예: "삼성전자")
        year: 사업연도 (YYYY 형식, 예: "2025")
        report_type: 보고서 유형
            "annual"=사업보고서, "q1"=1분기, "half"=반기, "q3"=3분기
    """
    reprt_code_map = {
        "annual": "11011",
        "q1": "11013",
        "half": "11012",
        "q3": "11014",
    }
    reprt_code = reprt_code_map.get(report_type, "11011")

    async with _get_client() as client:
        # Step 1: Find corp_code
        search = await client.search_company(corp_name)
        if not search.success:
            return f"기업 검색 오류: {search.error}"
        if not search.data:
            return f"'{corp_name}'에 해당하는 기업을 찾을 수 없습니다."

        corp_code = search.data[0]["corp_code"]

        # Step 2: Get financials
        result = await client.get_financials(
            corp_code=corp_code,
            bsns_year=year,
            reprt_code=reprt_code,
        )

    if not result.success:
        return f"재무제표 조회 오류: {result.error}"
    if not result.data:
        return f"'{corp_name}'의 {year}년 재무제표가 없습니다."

    return _to_json(
        {
            "corp_name": corp_name,
            "corp_code": corp_code,
            "year": year,
            "report_type": report_type,
            "financials": result.data,
        }
    )


if __name__ == "__main__":
    mcp.run()
