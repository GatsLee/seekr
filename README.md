# Seekr

**AI Agent Tool Execution Infrastructure for Korea**

> Korean Composio + Self-hosting | Apache 2.0

AI 에이전트가 한국 비즈니스 도구(DART, 카카오톡, 네이버웍스, 토스, 쿠팡)를 사용할 수 있게 하는 오픈소스 도구 실행 인프라입니다.

## Quick Start

### 1. Install

```bash
git clone https://github.com/gatslee/seekr.git
cd seekr
uv sync
```

### 2. Set API Key

```bash
export DART_API_KEY="your-dart-api-key"
# Get your key at https://opendart.fss.or.kr/
```

### 3. Run DART MCP Server

```bash
uv run python -m seekr.mcp.dart_server
```

### 4. Connect to Claude Code

```bash
claude mcp add seekr-dart -- uv run python -m seekr.mcp.dart_server
```

Then in Claude Code:

```
You: "삼성전자 최근 공시 보여줘"
Claude: [dart_disclosures 도구 사용] 삼성전자의 최근 공시 목록입니다...
```

## Available Tools

| Tool | Description |
|---|---|
| `dart_company_search` | DART에서 기업 검색 (고유번호 반환) |
| `dart_disclosures` | 기업의 공시 목록 조회 |
| `dart_disclosure_detail` | 특정 공시 상세 내용 조회 |
| `dart_financials` | 기업 재무제표 조회 |

## Development

```bash
uv sync                    # Install dependencies
uv run pytest              # Run tests
uv run ruff check .        # Lint
uv run mypy seekr/         # Type check
```

## License

Apache 2.0
