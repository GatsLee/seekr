# Contributing to Seekr

Seekr에 기여해주셔서 감사합니다!

## 개발 환경 셋업

```bash
git clone https://github.com/GatsLee/seekr.git
cd seekr
uv sync
pre-commit install
```

## 브랜치 네이밍

```
main              ← 안정, 배포 가능
feat/description  ← 새 기능
fix/description   ← 버그 수정
docs/description  ← 문서
refactor/description ← 리팩토링
```

## 커밋 컨벤션

```
[TYPE] short description in lowercase
```

| Type | 사용 시점 |
|---|---|
| `[FEAT]` | 새 기능 |
| `[FIX]` | 버그 수정 |
| `[DOCS]` | 문서 변경 |
| `[REFACTOR]` | 동작 변경 없는 코드 구조 개선 |
| `[CHORE]` | 의존성, 설정, 빌드 |
| `[TEST]` | 테스트 추가/수정 |
| `[STYLE]` | 포맷팅, 공백 (로직 변경 없음) |
| `[PERF]` | 성능 개선 |
| `[CI]` | CI/CD 변경 |

예시: `[FEAT] add kakao talk mcp server`

## PR 프로세스

1. `feat/your-feature` 브랜치 생성
2. 변경 사항 구현 + 테스트 추가
3. 아래 검증 통과 확인:
   ```bash
   uv run ruff check .
   uv run mypy seekr/
   uv run pytest
   ```
4. PR 생성 → 리뷰 → 머지

## 코드 스타일

- **Linter:** ruff (line-length 88)
- **Type checker:** mypy
- **Formatter:** ruff format
- 모든 공개 함수에 타입 힌트 필수
- 도구(tool)의 docstring은 한국어로 작성 (AI 에이전트가 도구 설명으로 사용)

## 테스트

- `tests/` 디렉토리에 미러 구조로 작성
- 외부 API 호출은 `respx`로 mock
- 새 도구 추가 시 단위 테스트 필수

## 새 서비스 통합 추가하기

1. `seekr/tools/{service_name}/` 디렉토리 생성
2. `client.py`에 API 클라이언트 구현 (httpx.AsyncClient 기반)
3. `seekr/mcp/{service_name}_server.py`에 MCP 서버 구현
4. `tests/tools/test_{service_name}_client.py`에 테스트 작성
5. README.md의 Available Tools 테이블 업데이트
