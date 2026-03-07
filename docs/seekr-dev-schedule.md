# Seekr 개발 일정

> 주 40시간 투입 기준 (월-금 8h/일)
> 총 10주, 4 Phase
> 기술 상세 설계: 00-synthesis.md 및 seekr-unified-plan.md 참조

---

## Phase 0: MCP 서버 + 코어 엔진 (Week 1-3, 120h)

### Week 1 — DART MCP 서버 + 프로젝트 셋업 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | 모노레포 초기화 | |
| | 2h | GitHub 레포 생성 (Apache 2.0, .gitignore, pre-commit) | 레포 push 완료 |
| | 3h | 디렉토리 구조 설계 | `seekr/core/`, `seekr/tools/`, `seekr/auth/`, `seekr/mcp/` |
| | 3h | 개발 환경 셋업 (uv, ruff, mypy, pytest) | `uv run pytest` 통과 |
| **화** | 8h | DART API 연동 | |
| | 2h | DART Open API 문서 분석 + 엔드포인트 매핑 | 호출 가능한 API 목록 정리 |
| | 3h | DART 클라이언트 구현 (기업 검색, 공시 목록) | 단위 테스트 통과 |
| | 3h | DART 클라이언트 구현 (공시 상세, 재무제표) | 단위 테스트 통과 |
| **수** | 8h | DART MCP 서버 | |
| | 2h | MCP 프로토콜 학습 + mcp Python SDK 설치 | 예제 서버 구동 확인 |
| | 4h | DART MCP 서버 구현 (4개 도구) | `mcp dev` 로 테스트 통과 |
| | 2h | Pydantic 입력 스키마 정의 (DartDisclosureParams 등) | 타입 검증 동작 |
| **목** | 8h | 테스트 + 연동 검증 | |
| | 3h | DART MCP 단위/통합 테스트 작성 | pytest 통과 |
| | 3h | Claude Code에서 MCP 연동 테스트 | "삼성전자 공시" 쿼리 성공 |
| | 2h | Cursor MCP 연동 테스트 | 동일 쿼리 성공 |
| **금** | 8h | 문서 + 마무리 | |
| | 3h | README.md 작성 (한국어 + 영어, 설치법, 퀵스타트) | |
| | 2h | DART MCP 사용 가이드 (docs/guides/dart.md) | |
| | 2h | Week 1 회고 + Week 2 계획 조정 | |
| | 1h | 코드 리뷰 + 리팩토링 | |

**Week 1 산출물:** DART MCP 서버 (4개 도구), Claude Code/Cursor 연동 확인

---

### Week 2 — 카카오톡 + 네이버웍스 MCP 서버 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | 카카오톡 API 연동 | |
| | 2h | 카카오 REST API 문서 분석 (나에게 보내기, 친구 목록) | 엔드포인트 매핑 |
| | 3h | 카카오 클라이언트 구현 (나에게 보내기, 친구 목록) | 단위 테스트 통과 |
| | 3h | 카카오 MCP 서버 구현 | `mcp dev` 테스트 통과 |
| **화** | 8h | 카카오톡 고도화 + 테스트 | |
| | 3h | 카카오 메시지 전송 (텍스트, 리스트, 피드 템플릿) | 메시지 유형별 테스트 |
| | 3h | 카카오 MCP 통합 테스트 | Claude Code에서 "나에게 보내기" 성공 |
| | 2h | 카카오 API 에러 핸들링 (토큰 만료, 권한 부족) | 에러 케이스 테스트 |
| **수** | 8h | 네이버웍스 API 연동 | |
| | 2h | 네이버웍스 API 문서 분석 (Bot, Calendar) | 엔드포인트 매핑 |
| | 3h | 네이버웍스 JWT 서비스 인증 구현 | 토큰 발급 성공 |
| | 3h | 네이버웍스 클라이언트 (메시지 전송, 일정 조회) | 단위 테스트 통과 |
| **목** | 8h | 네이버웍스 MCP + 테스트 | |
| | 3h | 네이버웍스 MCP 서버 구현 (메시지, 일정 생성, 캘린더) | `mcp dev` 테스트 통과 |
| | 3h | 일정 생성 도구 구현 (날짜 파싱, 시간대 처리) | KST 기준 동작 확인 |
| | 2h | 네이버웍스 MCP 통합 테스트 | Claude Code 연동 성공 |
| **금** | 8h | 3개 MCP 통합 + 정리 | |
| | 3h | 도구 추상화 레이어 (`BaseTool`, `ToolDefinition`) | 3개 서비스 공통 인터페이스 |
| | 2h | 3개 MCP 서버 동시 구동 테스트 | |
| | 2h | 각 MCP 사용 가이드 작성 | docs/guides/kakao.md, naver-works.md |
| | 1h | Week 2 회고 | |

**Week 2 산출물:** 카카오톡 MCP (3개 도구), 네이버웍스 MCP (4개 도구)

---

### Week 3 — 코어 엔진 + 인증 + Docker (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | FastAPI 서버 기반 | |
| | 3h | FastAPI 프로젝트 구조 (라우터, 미들웨어, 의존성 주입) | `/health` 응답 |
| | 3h | PostgreSQL 스키마 설계 + Alembic 마이그레이션 | users, credentials, tool_executions 테이블 |
| | 2h | Redis 연결 + 기본 설정 | ping 성공 |
| **화** | 8h | 인증 엔진 | |
| | 3h | API Key 생성/검증 미들웨어 | 인증 실패 시 401 |
| | 3h | CredentialStore (Fernet 암호화 저장/조회) | 암호화/복호화 테스트 |
| | 2h | 인증 엔진 단위 테스트 | |
| **수** | 8h | 도구 레지스트리 + 실행 엔진 | |
| | 3h | ToolRegistry (도구 등록/조회, 스키마 내보내기) | `/v1/tools` 엔드포인트 |
| | 3h | 실행 엔진 (`/v1/tools/{id}/execute`) | DART 도구 HTTP로 실행 성공 |
| | 2h | ExecutionGuard (연속 호출 감지) | 6회 연속 호출 시 차단 확인 |
| **목** | 8h | Docker + 통합 | |
| | 3h | Docker Compose 작성 (FastAPI + PostgreSQL + Redis) | `docker compose up` 성공 |
| | 2h | Dockerfile 최적화 (멀티스테이지 빌드) | 이미지 크기 < 200MB |
| | 3h | 3개 MCP 도구를 레지스트리에 등록 + 통합 테스트 | HTTP API로 3개 서비스 실행 |
| **금** | 8h | 통합 MCP 서버 + 정리 | |
| | 4h | 통합 MCP 서버 (3개 서비스 도구를 하나의 MCP로) | 단일 MCP에서 11개 도구 |
| | 2h | 환경 변수 설정 가이드 (.env.example) | |
| | 1h | Phase 0 통합 테스트 | Docker + MCP + HTTP 모두 동작 |
| | 1h | Phase 0 회고 + Phase 1 계획 | |

**Week 3 산출물:** FastAPI 서버, 인증 엔진, Docker Compose, 통합 MCP 서버

---

## Phase 1: SDK + 서비스 확장 (Week 4-6, 120h)

### Week 4 — Python SDK + PyPI 배포 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | SDK 설계 + 핵심 구현 | |
| | 3h | SDK 인터페이스 설계 (Seekr, SeekrTool, SeekrResult) | API 문서 초안 |
| | 5h | SDK 핵심 구현: 초기화, 인증, 도구 목록 조회 | `Seekr(api_key=...)` 동작 |
| **화** | 8h | SDK 도구 실행 + 에러 | |
| | 4h | 도구 실행: `seekr.tools.execute("dart_disclosure", {...})` | 실행 성공 |
| | 4h | SeekrError 계층 (AuthError, ToolError, RateLimitError) | 에러 타입별 핸들링 |
| **수** | 8h | 프레임워크 어댑터 | |
| | 4h | LangChain 어댑터: `seekr.to_langchain_tools()` | LangChain 에이전트에서 실행 |
| | 4h | PydanticAI 어댑터: `seekr.to_pydanticai_tools()` | PydanticAI 에이전트에서 실행 |
| **목** | 8h | 패키징 + 배포 | |
| | 3h | pyproject.toml, 빌드 설정, 버전 관리 | `uv build` 성공 |
| | 2h | PyPI 테스트 배포 (TestPyPI) | `pip install -i testpypi seekr` |
| | 3h | SDK 단위/통합 테스트 | 커버리지 70%+ |
| **금** | 8h | 문서 + 배포 | |
| | 3h | SDK 퀵스타트 가이드 (한국어) | 5줄 코드 예제 |
| | 2h | PyPI 정식 배포 (seekr 0.1.0) | `pip install seekr` 동작 |
| | 2h | CHANGELOG.md 작성 | |
| | 1h | Week 4 회고 | |

**Week 4 산출물:** seekr 0.1.0 (PyPI), LangChain/PydanticAI 어댑터

---

### Week 5 — OAuth2 + GitHub/Gmail (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | OAuth2 인증 흐름 | |
| | 4h | OAuth2 엔진: 인가 URL 생성, 콜백 핸들러, 토큰 저장 | |
| | 4h | 자동 토큰 갱신 (refresh_token) + 만료 관리 | 갱신 테스트 통과 |
| **화** | 8h | GitHub 도구 | |
| | 3h | GitHub 클라이언트 (이슈 CRUD, PR 조회, 레포 검색) | 단위 테스트 |
| | 3h | GitHub MCP 도구 + 레지스트리 등록 | |
| | 2h | GitHub OAuth 플로우 e2e 테스트 | 연결 → 이슈 조회 성공 |
| **수** | 8h | Gmail 도구 | |
| | 3h | Gmail 클라이언트 (메일 목록, 메일 상세, 메일 전송) | 단위 테스트 |
| | 3h | Gmail MCP 도구 + 레지스트리 등록 | |
| | 2h | Gmail OAuth 플로우 e2e 테스트 | 연결 → 메일 조회 성공 |
| **목** | 8h | 연결 관리 UI | |
| | 4h | React 최소 UI: 연결 목록, OAuth 연결 버튼, 상태 표시 | |
| | 4h | API 연동: 연결 생성/삭제/상태 확인 | UI에서 GitHub 연결 성공 |
| **금** | 8h | 통합 + 테스트 | |
| | 3h | OAuth2 통합 테스트 (GitHub + Gmail) | |
| | 2h | SDK 업데이트: OAuth 연결 지원 | seekr 0.2.0 |
| | 2h | 통합 MCP 서버에 GitHub/Gmail 추가 | 5개 서비스, 20+ 도구 |
| | 1h | Week 5 회고 | |

**Week 5 산출물:** OAuth2 엔진, GitHub/Gmail 도구, 연결 관리 UI

---

### Week 6 — 토스페이먼츠 + 쿠팡 + 공공데이터 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | 토스페이먼츠 | |
| | 2h | 토스페이먼츠 API 분석 (결제 조회, 취소, 정산) | |
| | 3h | 토스페이먼츠 클라이언트 + Basic Auth 구현 | 단위 테스트 |
| | 3h | 토스페이먼츠 MCP 도구 + 레지스트리 등록 | |
| **화** | 8h | 쿠팡 셀러 | |
| | 2h | 쿠팡 셀러 API 분석 (HMAC 인증, 상품/주문) | |
| | 3h | 쿠팡 클라이언트 + HMAC 서명 구현 | 단위 테스트 |
| | 3h | 쿠팡 MCP 도구 + 레지스트리 등록 | |
| **수** | 8h | 공공데이터 + 테스트 | |
| | 3h | 공공데이터 포털 인기 API 1-2개 도구화 | |
| | 3h | 토스/쿠팡/공공데이터 통합 테스트 | Claude Code에서 실행 |
| | 2h | 한국 서비스 인증 통합 (KoreanAuthProvider) | |
| **목** | 8h | SDK 업데이트 + 문서 | |
| | 3h | SDK 0.3.0: 새 도구 반영, 타입 힌트 보강 | PyPI 배포 |
| | 3h | 각 서비스 사용 가이드 (토스, 쿠팡) | |
| | 2h | 통합 MCP 서버 업데이트 (7개 서비스, 30+ 도구) | |
| **금** | 8h | Phase 1 마무리 | |
| | 4h | Phase 1 전체 통합 테스트 | 7개 서비스 모두 동작 |
| | 2h | 코드 정리 + 리팩토링 | |
| | 1h | Phase 1 회고 | |
| | 1h | Phase 2 상세 계획 | |

**Week 6 산출물:** 토스/쿠팡/공공데이터 도구, SDK 0.3.0, 7개 서비스 통합

---

## Phase 2: 프로덕션 강화 (Week 7-8, 80h)

### Week 7 — 캐싱 + 감사로그 + RBAC + 관측성 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | 결과 캐싱 + 결과 압축 | |
| | 4h | ToolResultCache (Redis, TTL 정책, 캐시 키 생성) | 캐시 히트 테스트 |
| | 4h | ResultCompressor (리스트 요약, 메타데이터 제거) | 압축 전후 비교 |
| **화** | 8h | 감사 로그 + 비용 추적 | |
| | 4h | AuditLogger (불변 기록, 파라미터 해시) | DB 기록 확인 |
| | 4h | CostTracker (API 호출/토큰 추적, 세션 요약) | 세션 비용 조회 |
| **수** | 8h | RBAC + 속도 제한 | |
| | 4h | RBAC (Permission, Role, 미들웨어) | viewer 도구 실행 차단 확인 |
| | 4h | 속도 제한 (사용자별, 도구별, Redis 슬라이딩 윈도우) | 제한 초과 시 429 |
| **목** | 8h | 관측성 + 재시도 | |
| | 4h | OpenTelemetry 통합 (트레이서, 메트릭, 스팬) | Jaeger에서 트레이스 확인 |
| | 2h | 재시도 로직 (지수 백오프, 최대 3회) | |
| | 2h | 헬스체크 엔드포인트 (`/health`, `/ready`) | DB/Redis 연결 확인 |
| **금** | 8h | 통합 + SafeHttpClient | |
| | 4h | SafeHttpClient (SSRF 차단, 도메인 화이트리스트) | 내부 IP 차단 테스트 |
| | 2h | 실행 파이프라인 전체 통합 테스트 | 캐싱→가드→인증→실행→압축→감사 |
| | 1h | 보안 셀프 리뷰 (OWASP 체크리스트) | |
| | 1h | Week 7 회고 | |

**Week 7 산출물:** 캐싱, 감사로그, RBAC, 속도제한, OpenTelemetry, SSRF 방어

---

### Week 8 — 테스트 + CI/CD + 문서 사이트 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | 단위 테스트 강화 | |
| | 4h | 코어 모듈 테스트 (cache, guard, audit, cost, rbac) | 커버리지 80%+ |
| | 4h | 인증 모듈 테스트 (credential_store, korean_auth, oauth) | |
| **화** | 8h | 통합 테스트 + Mock | |
| | 4h | 외부 API Mock 서버 구축 (DART, 카카오, 네이버웍스) | |
| | 4h | e2e 테스트: SDK → API → Mock → 결과 검증 | |
| **수** | 8h | CI/CD | |
| | 3h | GitHub Actions: 린트(ruff) + 타입체크(mypy) + 테스트(pytest) | PR마다 자동 실행 |
| | 2h | GitHub Actions: PyPI 자동 배포 (태그 트리거) | 태그 push → PyPI |
| | 3h | Docker 이미지 빌드 + GitHub Container Registry 푸시 | |
| **목** | 8h | 문서 사이트 | |
| | 3h | MkDocs Material 셋업 (한국어 + 영어 전환) | |
| | 3h | API 레퍼런스 (FastAPI OpenAPI → 자동 생성) | |
| | 2h | 아키텍처 가이드 (다이어그램 포함) | |
| **금** | 8h | v1.0.0-beta + 마무리 | |
| | 2h | SDK v1.0.0-beta 태깅 + PyPI 배포 | |
| | 2h | Docker 이미지 v1.0.0-beta 태깅 | |
| | 2h | CHANGELOG, CONTRIBUTING.md | |
| | 1h | Phase 2 회고 | |
| | 1h | Phase 3 상세 계획 | |

**Week 8 산출물:** 테스트 80%+, CI/CD, 문서 사이트, v1.0.0-beta

---

## Phase 3: 예제 + 런칭 (Week 9-10, 80h)

### Week 9 — 예제 프로젝트 + 플레이그라운드 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | 퀵스타트 + 예제 1 | |
| | 3h | 퀵스타트 가이드: "5분 만에 DART 에이전트 만들기" | |
| | 5h | 예제 1: LangChain + Seekr 한국 주식 분석 에이전트 | 실행 가능한 노트북 |
| **화** | 8h | 예제 2 + 3 | |
| | 4h | 예제 2: PydanticAI + Seekr 업무 자동화 에이전트 | 실행 가능한 스크립트 |
| | 4h | 예제 3: Claude Code + Seekr MCP 비즈니스 어시스턴트 | MCP 설정 가이드 |
| **수** | 8h | 플레이그라운드 UI | |
| | 4h | React UI: 도구 목록 → 파라미터 입력 → 실행 → 결과 표시 | |
| | 4h | API 키 입력, 도구 선택, JSON 결과 뷰어 | |
| **목** | 8h | 플레이그라운드 완성 + 배포 | |
| | 4h | 플레이그라운드 스타일링 + 에러 표시 + 로딩 | |
| | 2h | Docker Compose에 플레이그라운드 포함 | |
| | 2h | 문서 사이트에 예제 페이지 추가 | |
| **금** | 8h | 전체 검증 + 마무리 | |
| | 3h | 비개발자 사용성 테스트 (퀵스타트 10분 이내 완료?) | |
| | 3h | 문서 최종 검토 + 오탈자 수정 | |
| | 2h | Week 9 회고 | |

**Week 9 산출물:** 예제 3개, 플레이그라운드 UI, 문서 사이트 완성

---

### Week 10 — v1.0.0 릴리스 + 런칭 지원 (40h)

| 요일 | 시간 | 작업 | 완료 기준 |
|---|---|---|---|
| **월** | 8h | v1.0.0 준비 | |
| | 3h | 전체 테스트 실행 + 크리티컬 버그 수정 | CI 전체 그린 |
| | 3h | API 안정성 검토 (breaking change 없는지) | |
| | 2h | v1.0.0 릴리스 노트 작성 | |
| **화** | 8h | v1.0.0 릴리스 | |
| | 2h | SDK v1.0.0 PyPI 배포 | `pip install seekr==1.0.0` |
| | 2h | Docker v1.0.0 이미지 배포 | `docker pull seekr:1.0.0` |
| | 2h | GitHub Release 생성 (릴리스 노트 + 에셋) | |
| | 2h | 문서 사이트 v1.0.0 반영 + 배포 | |
| **수** | 8h | 런칭 기술 지원 | |
| | 4h | PM 데모 영상 촬영 기술 지원 (환경 셋업, 시나리오 실행) | |
| | 4h | 블로그 기술 내용 검수 + 코드 예제 검증 | |
| **목** | 8h | 런칭 후 대응 | |
| | 8h | GitHub Issues 모니터링 + 크리티컬 버그 핫픽스 | |
| **금** | 8h | 회고 + Phase 4 계획 | |
| | 3h | 피드백 기반 버그 수정 (1-2건) | v1.0.1 패치 |
| | 2h | 10주 전체 회고 (기술 부채, 아키텍처 개선점) | |
| | 3h | Phase 4 로드맵 초안 (TypeScript SDK, 추가 서비스, Enterprise) | |

**Week 10 산출물:** v1.0.0 릴리스, 런칭 지원, Phase 4 로드맵

---

## 시간 배분 요약

| Phase | 주 | 총 시간 | 비중 | 핵심 |
|---|---|---|---|---|
| Phase 0 | W1-3 | 120h | 30% | MCP 서버 3개 + 코어 엔진 + Docker |
| Phase 1 | W4-6 | 120h | 30% | SDK + PyPI + OAuth2 + 서비스 확장 |
| Phase 2 | W7-8 | 80h | 20% | 캐싱/보안/RBAC + 테스트/CI + 문서 |
| Phase 3 | W9-10 | 80h | 20% | 예제 + 플레이그라운드 + v1.0.0 |
| **합계** | **10주** | **400h** | **100%** | |

## 코드 품질 기준

| 기준 | 목표 |
|---|---|
| 테스트 커버리지 | Phase 2 완료 시 80%+ |
| 린트 | ruff (zero warnings) |
| 타입 체크 | mypy strict |
| 커밋 | `[TYPE] description` (프로젝트 컨벤션) |
| 브랜치 | `main`, `feat/...`, `fix/...` |
| CI | PR마다 린트 + 타입 + 테스트 자동 실행 |
