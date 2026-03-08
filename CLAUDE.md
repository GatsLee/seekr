# Seekr

AI 에이전트가 한국 비즈니스 도구를 사용할 수 있게 하는 도구 실행 인프라.
에이전트 프레임워크가 아닌 **도구 실행 레이어** (Layer 1). MCP 표준 프로토콜 사용.

## Commands

```bash
uv sync                    # Install dependencies
uv run pytest              # Run tests
uv run pytest -v           # Run tests (verbose)
uv run ruff check .        # Lint
uv run ruff format .       # Format
uv run mypy seekr/         # Type check
pre-commit run --all-files # Run all pre-commit hooks
```

## Structure

```
seekr/
├── core/          # Engine: registry, executor, guard, cache
├── tools/         # Tool implementations
│   ├── base.py    # ToolResult common type
│   └── dart/      # DART Open API client
├── auth/          # Authentication & credential management
├── mcp/           # MCP servers (dart_server.py, etc.)
├── api/           # FastAPI routes (future)
├── sdk/           # Python SDK (future)
└── models/        # DB models (future)
tests/             # Mirror structure of seekr/
docs/              # Planning & design docs
```

## Conventions

- Commit format: `[TYPE] short description` (FEAT, FIX, DOCS, REFACTOR, CHORE, TEST, STYLE, PERF, CI)
- Branch naming: `feat/`, `fix/`, `docs/`, `refactor/`
- Linter: ruff (line-length 88)
- Type checker: mypy
- Test framework: pytest + pytest-asyncio
- HTTP mock: respx
- Tool docstrings in Korean (used by AI agents as tool descriptions)
- All tool clients use httpx.AsyncClient
- ToolResult dataclass for all tool return values
