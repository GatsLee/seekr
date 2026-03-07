from __future__ import annotations

import httpx
import pytest
import respx

from seekr.tools.dart.client import BASE_URL, DartClient


@pytest.fixture
def client() -> DartClient:
    return DartClient(api_key="test_api_key")


def _url(path: str) -> str:
    return f"{BASE_URL}{path}"


class TestSearchCompany:
    @respx.mock
    async def test_found(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "000",
                    "message": "정상",
                    "total_count": 1,
                    "list": [
                        {
                            "corp_code": "00126380",
                            "corp_name": "삼성전자",
                            "stock_code": "005930",
                            "report_nm": "사업보고서",
                            "rcept_no": "20260305000123",
                            "rcept_dt": "20260305",
                        }
                    ],
                },
            )
        )

        result = await client.search_company("삼성전자")

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["corp_code"] == "00126380"
        assert result.data[0]["corp_name"] == "삼성전자"

    @respx.mock
    async def test_no_results(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(
                200,
                json={"status": "013", "message": "조회된 데이터가 없습니다."},
            )
        )

        result = await client.search_company("존재하지않는기업")

        assert result.success is True
        assert result.data == []

    @respx.mock
    async def test_api_error(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(
                200,
                json={"status": "010", "message": "등록되지 않은 인증키입니다."},
            )
        )

        result = await client.search_company("삼성전자")

        assert result.success is False
        assert "010" in (result.error or "")

    @respx.mock
    async def test_deduplicates_companies(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "000",
                    "message": "정상",
                    "list": [
                        {
                            "corp_code": "00126380",
                            "corp_name": "삼성전자",
                            "stock_code": "005930",
                        },
                        {
                            "corp_code": "00126380",
                            "corp_name": "삼성전자",
                            "stock_code": "005930",
                        },
                    ],
                },
            )
        )

        result = await client.search_company("삼성전자")

        assert result.success is True
        assert len(result.data) == 1


class TestGetDisclosures:
    @respx.mock
    async def test_success(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "000",
                    "message": "정상",
                    "total_count": 1,
                    "list": [
                        {
                            "rcept_no": "20260305000123",
                            "corp_name": "삼성전자",
                            "report_nm": "사업보고서 (2025.12)",
                            "rcept_dt": "20260305",
                            "flr_nm": "삼성전자",
                        }
                    ],
                },
            )
        )

        result = await client.get_disclosures("00126380")

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["rcept_no"] == "20260305000123"
        assert result.data[0]["report_nm"] == "사업보고서 (2025.12)"
        assert result.metadata["total_count"] == 1

    @respx.mock
    async def test_with_date_range(self, client: DartClient) -> None:
        route = respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(
                200,
                json={"status": "000", "message": "정상", "total_count": 0, "list": []},
            )
        )

        await client.get_disclosures("00126380", bgn_de="20260101", end_de="20260308")

        assert route.called
        request = route.calls[0].request
        assert "bgn_de=20260101" in str(request.url)
        assert "end_de=20260308" in str(request.url)


class TestGetDisclosureDetail:
    @respx.mock
    async def test_success(self, client: DartClient) -> None:
        respx.get(_url("/document.json")).mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "000",
                    "message": "정상",
                    "document": "<html>공시 내용</html>",
                },
            )
        )

        result = await client.get_disclosure_detail("20260305000123")

        assert result.success is True
        assert "document" in result.data


class TestGetFinancials:
    @respx.mock
    async def test_success(self, client: DartClient) -> None:
        respx.get(_url("/fnlttSinglAcntAll.json")).mock(
            return_value=httpx.Response(
                200,
                json={
                    "status": "000",
                    "message": "정상",
                    "list": [
                        {
                            "account_nm": "매출액",
                            "thstrm_amount": "300,000,000,000",
                            "frmtrm_amount": "280,000,000,000",
                            "bfefrmtrm_amount": "260,000,000,000",
                            "sj_nm": "손익계산서",
                        }
                    ],
                },
            )
        )

        result = await client.get_financials("00126380", "2025")

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]["account_nm"] == "매출액"
        assert result.data[0]["sj_nm"] == "손익계산서"

    @respx.mock
    async def test_quarterly_report(self, client: DartClient) -> None:
        route = respx.get(_url("/fnlttSinglAcntAll.json")).mock(
            return_value=httpx.Response(
                200,
                json={"status": "000", "message": "정상", "list": []},
            )
        )

        await client.get_financials("00126380", "2025", reprt_code="11013")

        request = route.calls[0].request
        assert "reprt_code=11013" in str(request.url)


class TestConnectionErrors:
    @respx.mock
    async def test_http_error(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        result = await client.search_company("삼성전자")

        assert result.success is False
        assert "500" in (result.error or "")

    @respx.mock
    async def test_network_error(self, client: DartClient) -> None:
        respx.get(_url("/list.json")).mock(side_effect=httpx.ConnectError("timeout"))

        result = await client.search_company("삼성전자")

        assert result.success is False
        assert "Request failed" in (result.error or "")
