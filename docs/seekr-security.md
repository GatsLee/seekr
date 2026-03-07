# Seekr 보안 아키텍처

> 작성일: 2026-03-08
> 관련 문서: [seekr-dev-spec.md](seekr-dev-spec.md) | [seekr-unified-plan.md](seekr-unified-plan.md)

---

## 1. 보안 원칙

| # | 원칙 | 설명 |
|---|---|---|
| P1 | **코드 실행 없음** | Seekr는 도구 실행 인프라이지 에이전트 프레임워크가 아님. 사용자 코드를 실행하지 않아 RCE 공격 벡터를 구조적으로 제거 |
| P2 | **자격증명은 사용자 인프라에** | 셀프호스팅 우선 설계. 클라우드에서도 자격증명은 KMS 봉투 암호화로 격리. Hybrid 모드에서는 자격증명이 클라우드를 통과하지 않음 |
| P3 | **감사 추적 Day 1** | 보안은 사후 대응이 아닌 설계 시점부터. 모든 도구 실행은 감사 로그에 기록, 변조 불가 |

---

## 2. 배포 시나리오별 보안 아키텍처

### A. Self-Hosted (온프레미스)

**대상:** 금융, 의료, 정부기관 등 PIPA 규제 기업

#### 인증 & 인가

| 구성요소 | 설계 |
|---|---|
| API Key | `sk_seekr_` 접두사, argon2id 해시 저장 (PostgreSQL), 만료일 설정 가능 |
| JWT | RS256 알고리즘, 15분 만료, Refresh Token 로테이션 |
| SSO | 선택적 LDAP/AD 연동 (`python-ldap`), 기존 기업 ID 체계와 통합 |
| RBAC | 4개 기본 역할: `admin`, `developer`, `viewer`, `service_account` |
| 권한 | `tool:execute`, `connection:create`, `connection:delete`, `audit:read`, `admin:*` |

#### 자격증명 관리

```
┌─────────────────────────────────────────────┐
│ 자격증명 저장 흐름                            │
│                                             │
│ 평문 API Key                                │
│   ↓ AES-256-GCM 암호화                      │
│   ↓ 마스터키: SEEKR_MASTER_KEY (환경변수)      │
│   ↓ 키 유도: PBKDF2 (100,000 iterations)    │
│   ↓ 키 버전 헤더 포함                         │
│ Connection.encrypted_credentials (bytea)     │
│                                             │
│ [선택] HashiCorp Vault 연동 → 마스터키 외부화  │
└─────────────────────────────────────────────┘
```

- **키 로테이션:** 다중 활성 암호화 키 지원, credential blob 헤더에 키 버전 포함
- **메모리 캐시:** 복호화된 자격증명은 프로세스 로컬 메모리에 5분 TTL 캐싱 (Redis가 아닌 프로세스 메모리 — 네트워크 노출 방지)
- **Vault 연동:** `hvac` 클라이언트로 HashiCorp Vault KV v2 시크릿 엔진 연동 옵션

#### 네트워크 보안

```python
# SafeHttpClient 핵심 로직
class SafeHttpClient:
    BLOCKED_NETWORKS = [
        "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16",
        "169.254.0.0/16", "127.0.0.0/8", "::1/128"
    ]

    # 도구별 도메인 화이트리스트
    DOMAIN_WHITELIST = {
        "dart": ["opendart.fss.or.kr"],
        "kakao": ["kapi.kakao.com", "kauth.kakao.com"],
        "naver_works": ["www.worksapis.com"],
        "toss": ["api.tosspayments.com"],
        "coupang": ["api-gateway.coupang.com"],
        "github": ["api.github.com"],
        "gmail": ["gmail.googleapis.com", "oauth2.googleapis.com"],
    }

    async def request(self, tool_id: str, url: str, ...):
        # 1. URL 파싱 → 호스트네임 추출
        # 2. DNS 사전 해석 → IP 획득
        # 3. IP가 사설 대역에 속하는지 검증 (SSRF 차단)
        # 4. 호스트네임이 tool_id 화이트리스트에 포함되는지 검증
        # 5. DNS 리바인딩 방지: 해석된 IP로 직접 연결
        ...
```

- TLS 1.2+ 강제 (모든 외부 통신)
- Docker 네트워크 격리: 백엔드는 내부 네트워크, 리버스 프록시만 외부 노출
- 인바운드 포트: 443 (리버스 프록시)만 개방

#### 데이터 보호 (PIPA)

| 항목 | 구현 |
|---|---|
| 암호화 at rest | PostgreSQL `pgcrypto` 컬럼 레벨 암호화, 디스크 암호화 권장 |
| 암호화 in transit | TLS 종단 (nginx/Caddy 리버스 프록시) |
| PII 처리 | 감사 로그 파라미터 SHA-256 해싱, 원본 미저장 |
| 데이터 레지던시 | 자체 인프라 → 자동 충족 |
| 삭제권 | `DELETE /v1/users/{id}` → connections, executions, audit 캐스케이드 (보유기간 내 감사로그 예외 설정 가능) |
| 보유기간 | 기본 2년 (PIPA 요건), 설정 가능 |
| 가명처리 | 감사 로그 user_id → 가명 식별자 치환 옵션 |

---

### B. Cloud (SaaS 멀티테넌트)

**대상:** 스타트업, 개인 개발자, 소규모 팀

#### 인증 & 인가

| 구성요소 | 설계 |
|---|---|
| API Key | `sk_seekr_` 접두사, 조직(org) 단위 스코프 |
| Dashboard SSO | OAuth2 로그인 (Google, GitHub) via `authlib` |
| 조직 RBAC | `owner`, `admin`, `member`, `readonly` |
| 테넌트 격리 | 모든 DB 쿼리에 `WHERE org_id = ?` 강제 (SQLAlchemy 이벤트 훅) |
| 방어 심층 | PostgreSQL Row-Level Security (RLS) 추가 적용 |

#### 자격증명 관리 (봉투 암호화)

```
┌─────────────────────────────────────────────┐
│  봉투 암호화 (Envelope Encryption)            │
│                                             │
│  AWS KMS                                    │
│    └── Master Key (CMK)                     │
│          ├── Org A의 DEK (Data Encryption Key) │
│          ├── Org B의 DEK                     │
│          └── Org C의 DEK                     │
│                                             │
│  각 조직은 고유 DEK를 보유                     │
│  DEK는 KMS CMK로 래핑되어 DB에 저장            │
│  자격증명 암호화: DEK로 AES-256-GCM            │
│                                             │
│  → 한 조직이 침해되어도 다른 조직 자격증명 안전  │
└─────────────────────────────────────────────┘
```

- 자격증명 로테이션 리마인더: `token_expires_at` 추적, 웹훅 알림
- 조직 간 자격증명 완전 격리 (DB 침해 시에도 교차 접근 불가)

#### 네트워크 보안

| 계층 | 구현 |
|---|---|
| Edge | WAF (AWS WAF / Cloudflare) + CDN DDoS 보호 |
| Application | `SafeHttpClient` (Self-hosted와 동일) |
| Network | VPC: 공개 서브넷 (ALB만) + 비공개 서브넷 (API, DB, Redis) |
| Rate Limiting | API 게이트웨이 (글로벌) + 애플리케이션 (사용자/도구별 Redis 슬라이딩 윈도우) |

#### 멀티테넌트 보안

| 위협 | 대응 |
|---|---|
| 크로스테넌트 데이터 접근 | PostgreSQL RLS + SQLAlchemy `org_id` 필터 훅 + 조직별 암호화 키 |
| Noisy Neighbor | 조직별 레이트 리밋 + 리소스 쿼터 |
| 과금 격리 | `tool_execution` 테이블 조직별 사용량 추적 |
| 데이터 이식성 | `GET /v1/org/export` 전체 데이터 덤프 |

#### 인프라

- **리전:** 서울 (ap-northeast-2) — 한국 데이터 레지던시
- **DB 암호화:** RDS AES-256 암호화 at rest
- **백업:** RDS 자동 백업 + KMS 암호화
- **서비스 간 통신:** VPC 내 TLS (선택적 mTLS)

---

### C. Hybrid (Credential Proxy)

**대상:** 관리형 인프라를 원하지만 자격증명은 온프레미스에 유지하려는 기업

#### 아키텍처

```
┌──────────────────────────┐     ┌──────────────────────────┐
│  Seekr Cloud              │     │  고객 온프레미스           │
│                          │     │                          │
│  API Server              │     │  Credential Proxy (~50MB) │
│  Tool Registry           │ ←──→│  /credentials/{svc}/decrypt│
│  Redis Cache             │ mTLS│  /health                  │
│  Dashboard               │     │  /rotate                  │
│                          │     │                          │
│  보유: 실행 메타데이터     │     │  보유: 마스터키 + 자격증명  │
│  미보유: 자격증명, PII    │     │  로컬 감사 로그            │
└──────────────────────────┘     └──────────────────────────┘
```

#### 실행 흐름

1. AI 에이전트 → SDK → Seekr Cloud API에 도구 실행 요청
2. Cloud API → 고객 Credential Proxy에 자격증명 복호화 요청 (mTLS)
3. Credential Proxy → 복호화된 자격증명 반환
4. Cloud API → 외부 서비스 API 호출 (또는 Execution Proxy 모드: 고객 측에서 직접 호출)
5. 결과 반환 → 캐시 (옵트인) → 응답

#### 보안 경계

| 구분 | Cloud가 보는 것 | Cloud가 못 보는 것 |
|---|---|---|
| 자격증명 | X | 원본 자격증명, 암호화 키 |
| 메타데이터 | 도구 스키마, 실행 시간, 상태 | — |
| PII | X (해싱 후 전송) | 원본 파라미터 |
| 감사 로그 | 실행 메타데이터 | 고객 Proxy 접근 로그 |

#### Credential Proxy 사양

- **컨테이너:** FastAPI, ~50MB 이미지
- **엔드포인트:** 3개 (`/credentials/{service}/decrypt`, `/health`, `/rotate`)
- **인증:** Seekr Cloud와 mTLS (클라이언트 인증서 피닝)
- **네트워크:** 고객 VPN/사설 네트워크 내 배치
- **로깅:** 모든 접근을 로컬에 기록 (고객 감사 추적)

---

## 3. 위협 모델 (Top 10)

| # | 위협 | STRIDE | 영향도 | 대응 | Phase |
|---|---|---|---|---|---|
| T1 | **DB에서 자격증명 탈취** — DB 접근 후 암호화된 자격증명 추출 | 정보 노출 | Critical | AES-256-GCM 암호화, 마스터키 환경변수/KMS 분리, 키 로테이션, 조직별 DEK | Phase 0 (W3) |
| T2 | **SSRF** — 도구 파라미터에 내부 URL 주입 (`http://169.254.169.254/...`) | 변조 | Critical | `SafeHttpClient`: 사설 IP 차단, DNS 사전 해석, 도구별 도메인 화이트리스트 | Phase 2 (W7) |
| T3 | **API 키 유출** — 공개 저장소에 커밋 | 정보 노출 | High | `sk_seekr_` 접두사 (GitHub 시크릿 스캐닝 호환), 키 로테이션 API, 레이트 리밋 | Phase 0 (W3) |
| T4 | **크로스테넌트 접근** — 쿼리 버그로 다른 조직 데이터 노출 | 권한 상승 | Critical | PostgreSQL RLS + SQLAlchemy `org_id` 이벤트 훅 + 조직별 암호화 키 | Phase 2 (W7) |
| T5 | **프롬프트 인젝션** — 외부 API 결과에 악성 콘텐츠 삽입 | 변조 | High | 구조적 완화 (LLM 미호출), `ResultSanitizer` (제어 문자 제거, 의심 패턴 경고) | Phase 2 (W7) |
| T6 | **레이트 리밋 우회** — 다수 API 키 생성 또는 분산 IP 사용 | 서비스 거부 | Medium | Redis 슬라이딩 윈도우 3계층 (사용자 100/min + 조직 1K/min + 글로벌 10K/min), 키 생성 이상 탐지 | Phase 2 (W7) |
| T7 | **감사 로그 변조** — 내부자가 로그 수정/삭제 | 부인 | High | append-only 테이블, PostgreSQL 트리거로 UPDATE/DELETE 차단, HMAC 체인 (각 레코드에 이전 해시 포함) | Phase 2 (W7) |
| T8 | **의존성 공급망 공격** — 악성 PyPI 패키지 | 변조 | Critical | `uv.lock` 재현 가능 빌드, GitHub Dependabot, Trivy 컨테이너 스캔, 최소 의존성 정책, 정확한 버전 고정 | Phase 2 (W8) |
| T9 | **OAuth2 토큰 탈취** — 콜백 중 MITM | 정보 노출 | High | HTTPS 전용 콜백, PKCE (Proof Key for Code Exchange), `state` CSRF 토큰, 짧은 수명 인가 코드 | Phase 1 (W5) |
| T10 | **에러/로그에서 자격증명 노출** — 스택 트레이스에 비밀값 포함 | 정보 노출 | High | Pydantic `SecretStr`, 커스텀 예외 핸들러 (민감 필드 무결성), 구조화 로깅 민감 필드 필터 | Phase 0 (W3) |

---

## 4. 보안 기능 Phase별 매핑

### Phase 0 (W1-3): 보안 기반

| Week | 기능 | 구현 상세 |
|---|---|---|
| W1 | 의존성 고정 + pre-commit | `uv.lock`, ruff 보안 규칙, `.pre-commit-config.yaml`에 `bandit` |
| W1 | `.env` 보안 | `.env.example` (더미값), `.gitignore`에 `.env`, Pydantic `SecretStr` 설정 |
| W3 | API Key 인증 | argon2id 해시, `X-API-Key` 헤더 미들웨어, `sk_seekr_` 접두사 |
| W3 | CredentialStore v1 | Fernet 암호화 (Phase 2에서 AES-256-GCM 업그레이드), 마스터키 환경변수 |
| W3 | Pydantic 입력 검증 | 모든 도구 파라미터 strict 스키마 — 예상 외 필드 주입 차단 |
| W3 | 에러 무결성 | 커스텀 FastAPI 예외 핸들러, 응답에서 자격증명 제거 |
| W3 | Docker 보안 | Dockerfile `USER nonroot`, 읽기 전용 파일시스템, `--privileged` 금지 |

### Phase 1 (W4-6): 인증 확장

| Week | 기능 | 구현 상세 |
|---|---|---|
| W4 | SDK 자격증명 처리 | `SecretStr` API 키, 자격증명 로깅 금지, 보안 기본 헤더 |
| W5 | OAuth2 엔진 | PKCE, `state` CSRF 토큰, HTTPS 전용 콜백, 자동 토큰 리프레시 |
| W5 | 토큰 저장 | `Connection` 테이블에 암호화 리프레시 토큰, `token_expires_at` 추적 |
| W6 | 한국 서비스 인증 | HMAC 서명 (쿠팡), Basic Auth (토스), JWT 서비스 인증 (네이버웍스) — 각각 격리 모듈 |
| W6 | 연결 보안 | 자격증명 생성 시 테스트 API 호출로 유효성 검증, 유효하지 않으면 조기 거부 |

### Phase 2 (W7-8): 프로덕션 강화

| Week | 기능 | 구현 상세 |
|---|---|---|
| W7 | `SafeHttpClient` | SSRF 방지 (사설 IP 차단, DNS 사전 해석, 도구별 도메인 화이트리스트) |
| W7 | RBAC | Permission 모델, Role 미들웨어, 4개 기본 역할 |
| W7 | 레이트 리밋 | Redis 슬라이딩 윈도우: 사용자 (100 req/min), 도구별 (설정 가능), 글로벌 (10K req/min) |
| W7 | 감사 로그 | 불변 append-only 테이블, 파라미터 해싱, HMAC 체인, UPDATE/DELETE 트리거 차단 |
| W7 | ExecutionGuard | 연속 호출 감지 (기본: 60초 내 동일 도구 5회 = 차단), 도구별 설정 가능 |
| W7 | OpenTelemetry | 분산 트레이싱, 보안 span 속성 (auth method, user_id), 자격증명 데이터 span 미포함 |
| W8 | 암호화 업그레이드 | Fernet → AES-256-GCM, 키 버전 관리로 기존 자격증명 마이그레이션 |
| W8 | 보안 테스트 | CI에 `bandit`, `pip-audit`, OWASP ZAP 기본 스캔 |
| W8 | 컨테이너 스캔 | GitHub Actions에서 Trivy 스캔, CRITICAL/HIGH CVE 시 빌드 실패 |
| W8 | 보안 문서 | 셀프호스팅 보안 체크리스트, 자격증명 관리 가이드 |

### Phase 3 (W9-10): 마무리 & 준수

| Week | 기능 | 구현 상세 |
|---|---|---|
| W9 | Playground UI 보안 | CSRF 보호, CSP 헤더, 결과 표시 XSS 방지 |
| W9 | PIPA 준수 체크리스트 | 문서화: 데이터 인벤토리, 처리 목적, 보유 정책, 삭제 절차 |
| W10 | 보안 리뷰 | OWASP Top 10 자체 평가, 알려진 제한사항 문서화 |
| W10 | 인시던트 대응 절차서 | 자격증명 유출, 데이터 침해, 의존성 CVE 대응 문서 |

---

## 5. 인시던트 대응 절차

### 시나리오: API 키 또는 저장된 자격증명 유출

#### 즉시 대응 (0-15분)

1. **탐지:** GitHub 시크릿 스캐닝 알림, 사용자 신고, 비정상 사용 패턴
2. **무효화:** `POST /v1/api-keys/{id}/revoke` — 즉시 키 비활성화
3. **차단:** 공격 진행 중이면 소스 IP 임시 차단

#### 단기 대응 (15분-4시간)

1. **로테이션:** 영향받은 사용자에 새 API 키 발급
2. **알림:** 이메일/웹훅으로 사용자에게 상세 내용 통보
3. **감사:** 침해 키의 마지막 안전 사용 이후 모든 `audit_log` 엔트리 풀
4. **평가:** 제3자 자격증명 접근 여부 확인, 해당 시 `Connection` 자격증명 로테이션

#### 장기 대응 (4-48시간)

1. **포스트모템:** 유출 경위 문서화
2. **개선:** 탐지 규칙 업데이트, 재발 방지 가드레일 추가
3. **PIPA 신고:** PII 노출 가능성 시 — PIPC에 72시간 내 신고, 영향받은 개인에게 지체없이 통보

---

## 6. PIPA 준수 체크리스트

| # | 요건 | Seekr 대응 | 배포 모드 |
|---|---|---|---|
| 1 | 개인정보 수집 최소화 | 도구 실행에 필요한 파라미터만 수집, 감사로그 해싱 | 전체 |
| 2 | 목적 외 이용 금지 | RBAC으로 권한 제어, 감사 로그로 추적 | 전체 |
| 3 | 안전성 확보 조치 | AES-256-GCM 암호화, TLS, 접근 통제, 감사 로그 | 전체 |
| 4 | 보유기간 준수 | 기본 2년, 설정 가능, 자동 삭제 스케줄러 | 전체 |
| 5 | 파기 | `DELETE /v1/users/{id}` 캐스케이드 삭제 | 전체 |
| 6 | 침해 통지 | 인시던트 대응 절차서 (72시간 PIPC, 즉시 개인) | 전체 |
| 7 | 국외 이전 | Self-hosted: 해당 없음, Cloud: 서울 리전, Hybrid: 자격증명 국내 유지 | 시나리오별 |
| 8 | 가명처리 | 감사 로그 가명 식별자 옵션 | 전체 |
