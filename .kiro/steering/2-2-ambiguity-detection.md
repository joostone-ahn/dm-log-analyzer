---
inclusion: manual
---
<!------------------------------------------------------------------------------------
# 2-2. 외주사 오해 가능성 포인트 사전 검출 프롬프트

> **SDLC 단계**: ② 외주 개발 의뢰
> **목적**: 요구사항 문서의 모호한 표현, 해석의 여지가 있는 부분 자동 탐지
> **산출물 파일명**: `{{PROJECT_NAME}}_ambiguity_analysis_{{DATE}}.md`
-------------------------------------------------------------------------------------> 

# 2-2. 외주사 오해 가능성 포인트 사전 검출 프롬프트

> **SDLC 단계**: ② 외주 개발 의뢰
> **목적**: 요구사항 문서의 모호한 표현, 해석의 여지가 있는 부분 자동 탐지
> **산출물 파일명**: `{{PROJECT_NAME}}_ambiguity_analysis_{{DATE}}.md`

---

## System Prompt

```
You are a Communication Gap Analyst specializing in cross-cultural and cross-timezone software development.

Your expertise:
- Identifying ambiguous language in technical specifications
- Detecting cultural/language-based misinterpretation risks
- Finding implicit assumptions that offshore teams might miss
- Recognizing domain-specific terminology that needs clarification

Analysis framework (4 perspectives):
1. LINGUISTIC: Words with multiple technical meanings
2. CONTEXTUAL: Information requiring domain knowledge
3. CULTURAL: Assumptions based on local business practices
4. TECHNICAL: Implementation details left to interpretation

Red flags to detect:
- Subjective terms: "user-friendly", "fast", "secure", "simple"
- Implicit references: "as usual", "like before", "standard way"
- Missing quantities: "several", "many", "some", "few"
- Undefined actors: "the system", "it", "they"
```

---

## User Prompt

```
<context>
프로젝트: {{PROJECT_NAME}}
외주사: {{VENDOR_NAME}}
외주사 위치: {{VENDOR_LOCATION}}
외주사 주 언어: {{VENDOR_LANGUAGE}}
도메인: {{BUSINESS_DOMAIN}}
타임존 차이: {{TIMEZONE_DIFF}}
</context>

<requirement_document>
{{REQUIREMENTS}}
</requirement_document>

<glossary>
{{EXISTING_GLOSSARY}}
</glossary>

<instructions>
**PHASE 1: 언어적 모호성 탐지 (Linguistic Ambiguity)**
다음 패턴의 표현을 찾으세요:

| 패턴 | 예시 | 문제 |
|------|------|------|
| 주관적 형용사 | "빠른", "간단한" | 정량 기준 없음 |
| 불명확한 수량사 | "여러", "일부" | 정확한 숫자 없음 |
| 암시적 참조 | "기존 방식대로" | 외부인은 모름 |
| 미정의 약어 | "CS", "PG" | 도메인 지식 필요 |

**PHASE 2: 맥락적 모호성 탐지 (Contextual Ambiguity)**
외주사가 알지 못할 수 있는 배경 지식:
- 내부 시스템 구조
- 기존 코드 패턴
- 비즈니스 규칙
- 회사 문화/프로세스

**PHASE 3: 문화적 모호성 탐지 (Cultural Ambiguity)**
{{VENDOR_LOCATION}} 기반 외주사가 다르게 해석할 수 있는 부분:
- 날짜/시간 형식
- 숫자 형식 (천 단위 구분자)
- 업무 시간 기준
- 승인/결재 프로세스

**PHASE 4: 기술적 모호성 탐지 (Technical Ambiguity)**
구현 방식이 해석에 따라 달라질 수 있는 부분:
- 에러 처리 방식
- 로깅 수준
- 성능 기준
- 보안 요구사항
</instructions>

<output_format>
# {{PROJECT_NAME}} 모호성 분석 보고서

## 메타데이터
- **산출물 파일명**: `{{PROJECT_NAME}}_ambiguity_analysis_{{DATE}}.md`
- **생성일**: {{DATE}}
- **분석 대상**: 개발 의뢰서 v{{VERSION}}
- **대상 외주사**: {{VENDOR_NAME}} ({{VENDOR_LOCATION}})
- **분석자**: Claude AI (Communication Gap Analyst)

---

## Executive Summary

| 항목 | 수치 |
|------|------|
| 분석된 요구사항 수 | {{X}} |
| 발견된 모호성 | {{Y}} |
| CRITICAL (즉시 해결) | {{Z}} |
| HIGH (의뢰 전 해결) | {{W}} |
| MEDIUM (FAQ로 대응) | {{V}} |

### 위험도 평가
```
🔴 CRITICAL: {{Z}}개 - 오해 발생 확률 매우 높음
🟠 HIGH: {{W}}개 - 오해 발생 확률 높음
🟡 MEDIUM: {{V}}개 - 질문 예상됨
```

---

## 1. 언어적 모호성 (Linguistic)

### AMB-L01: 주관적 표현 - "사용자 친화적인 UI"
**위치**: 요구사항 REQ-003, 2번째 문단
**원문**: "사용자 친화적인 UI로 구현해주세요"
**심각도**: 🔴 CRITICAL

**문제점**:
- "사용자 친화적"의 정의가 명시되지 않음
- 외주사의 해석에 따라 결과물이 크게 달라질 수 있음

**외주사가 할 수 있는 해석**:
| 해석 | 결과물 |
|------|--------|
| A: 미니멀한 디자인 | 기능 버튼 최소화 |
| B: 가이드 풍부 | 툴팁, 헬프 텍스트 다수 |
| C: 빠른 조작 | 키보드 단축키 중심 |

**권고 수정안**:
```diff
- "사용자 친화적인 UI로 구현해주세요"
+ "다음 UI 요구사항을 충족해주세요:
+   1. 모든 액션은 3클릭 이내에 완료 가능
+   2. 필수 입력 필드는 빨간 별표(*)로 표시
+   3. 에러 메시지는 입력 필드 바로 아래에 빨간색으로 표시
+   4. 로딩 상태는 스피너로 표시 (3초 이상 시 진행률 표시)
+   5. 참조 디자인: [Figma 링크]"
```

---

### AMB-L02: 불명확한 수량 - "여러 개의 파일"
**위치**: 요구사항 REQ-007
**원문**: "사용자는 여러 개의 파일을 업로드할 수 있어야 합니다"
**심각도**: 🟠 HIGH

**문제점**:
- "여러 개"의 정확한 숫자가 없음
- 파일당 크기 제한, 총 크기 제한 미정의

**외주사가 할 수 있는 해석**:
| 해석 | 구현 |
|------|------|
| A: 2-5개 | 간단한 multiple input |
| B: 10-50개 | 드래그앤드롭 + 큐 관리 |
| C: 무제한 | 청크 업로드 + 재시작 기능 |

**권고 수정안**:
```diff
- "사용자는 여러 개의 파일을 업로드할 수 있어야 합니다"
+ "파일 업로드 요구사항:
+   - 최대 파일 개수: 10개
+   - 파일당 최대 크기: 50MB
+   - 총 업로드 최대 크기: 200MB
+   - 허용 파일 형식: .pdf, .doc, .docx, .xlsx, .jpg, .png
+   - 업로드 방식: 드래그앤드롭 + 파일 선택 버튼"
```

---

## 2. 맥락적 모호성 (Contextual)

### AMB-C01: 내부 시스템 참조 - "기존 인증 방식"
**위치**: 요구사항 REQ-012
**원문**: "기존 인증 방식을 그대로 사용합니다"
**심각도**: 🔴 CRITICAL

**문제점**:
- 외주사는 "기존 인증 방식"을 알 수 없음
- 내부 문서에만 존재하는 정보

**필요한 추가 정보**:
```markdown
## 인증 방식 명세

### 토큰 기반 인증 (JWT)
- 발급 엔드포인트: POST /api/v1/auth/token
- 토큰 형식: JWT (RS256)
- 토큰 만료: Access Token 1시간, Refresh Token 7일
- 헤더 형식: `Authorization: Bearer {access_token}`

### 토큰 갱신
- 엔드포인트: POST /api/v1/auth/refresh
- 요청 본문: { "refresh_token": "..." }

### 참조 코드
- `src/middleware/auth.ts` - 인증 미들웨어
- `src/services/token.ts` - 토큰 생성/검증
```

---

### AMB-C02: 비즈니스 규칙 누락 - "유효성 검증"
**위치**: 요구사항 REQ-015
**원문**: "입력값에 대한 유효성 검증을 수행합니다"
**심각도**: 🟠 HIGH

**문제점**:
- 어떤 검증 규칙인지 명시되지 않음
- 도메인 특화 규칙이 있을 수 있음

**필요한 추가 정보**:
```markdown
## 유효성 검증 규칙

### 사용자 정보
| 필드 | 규칙 |
|------|------|
| 이메일 | RFC 5322 형식, 최대 254자 |
| 비밀번호 | 8-20자, 대/소문자/숫자/특수문자 각 1개 이상 |
| 전화번호 | 010-XXXX-XXXX 형식 (하이픈 포함) |
| 생년월일 | YYYY-MM-DD, 14세 이상만 가입 가능 |

### 결제 정보
| 필드 | 규칙 |
|------|------|
| 카드번호 | Luhn 알고리즘 검증 |
| 유효기간 | MM/YY, 현재 날짜 이후 |
| CVC | 3-4자리 숫자 |
```

---

## 3. 문화적 모호성 (Cultural)

### AMB-CU01: 날짜 형식 미정의
**위치**: 전체 문서
**심각도**: 🟡 MEDIUM

**문제점**:
- 날짜 형식이 명시되지 않음
- {{VENDOR_LOCATION}} 기준: {{VENDOR_DATE_FORMAT}}
- 한국 기준: YYYY-MM-DD 또는 YYYY년 MM월 DD일

**권고 명세 추가**:
```markdown
## 날짜/시간 형식 표준

| 항목 | 형식 | 예시 |
|------|------|------|
| 날짜 (저장) | ISO 8601 | 2024-01-15 |
| 날짜 (표시) | YYYY년 MM월 DD일 | 2024년 01월 15일 |
| 시간 (저장) | ISO 8601 | 2024-01-15T09:30:00+09:00 |
| 시간 (표시) | 오전/오후 HH:MM | 오전 09:30 |
| 타임존 | Asia/Seoul (KST, UTC+9) | - |
```

---

### AMB-CU02: 업무 시간 기준 미정의
**위치**: SLA 관련 요구사항
**심각도**: 🟡 MEDIUM

**문제점**:
- "업무 시간 내 응답"의 기준이 다를 수 있음
- 한국: 09:00-18:00 KST
- {{VENDOR_LOCATION}}: {{VENDOR_BUSINESS_HOURS}}

**권고 명세 추가**:
```markdown
## 업무 시간 정의

| 항목 | 기준 |
|------|------|
| 업무 시간 | 09:00-18:00 KST (UTC+9) |
| 업무일 | 월-금 (한국 공휴일 제외) |
| 긴급 대응 | 24/7 (P1 장애 시) |
```

---

## 4. 기술적 모호성 (Technical)

### AMB-T01: 에러 처리 방식 미정의
**위치**: 전체 API 명세
**심각도**: 🟠 HIGH

**문제점**:
- API 에러 응답 형식이 정의되지 않음
- 에러 코드 체계가 없음

**권고 명세 추가**:
```markdown
## 에러 응답 형식

### 표준 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "PAYMENT_LIMIT_EXCEEDED",
    "message": "결제 금액이 한도를 초과했습니다",
    "details": {
      "requested_amount": 100000,
      "limit_amount": 50000
    }
  },
  "timestamp": "2024-01-15T09:30:00+09:00",
  "request_id": "req_abc123"
}
```

### HTTP 상태 코드
| 코드 | 용도 |
|------|------|
| 400 | 잘못된 요청 (유효성 검증 실패) |
| 401 | 인증 실패 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 409 | 충돌 (중복 등) |
| 422 | 비즈니스 규칙 위반 |
| 500 | 서버 내부 오류 |
```

---

## 5. 용어 사전 (권고 추가 항목)

외주사에게 제공할 용어 사전:

| 용어 | 정의 | 예시 |
|------|------|------|
| CS | Customer Service (고객 서비스) | CS 문의 = 고객 문의 |
| PG | Payment Gateway (결제 대행사) | 이니시스, KG이니시스 등 |
| 정산 | Settlement (판매자에게 대금 지급) | 매출 정산, 수수료 정산 |
| 어드민 | Admin (관리자 시스템) | 백오피스와 동의어 |

---

## 조치 권고 요약

### 🔴 즉시 수정 필요 (의뢰 전)
| ID | 항목 | 담당 | 기한 |
|----|------|------|------|
| AMB-L01 | "사용자 친화적" 정량화 | PM | {{DATE}} |
| AMB-C01 | 인증 방식 명세 추가 | Tech Lead | {{DATE}} |

### 🟠 의뢰서에 추가 필요
| ID | 항목 | 담당 | 기한 |
|----|------|------|------|
| AMB-L02 | 파일 업로드 상세 스펙 | PM | {{DATE}} |
| AMB-C02 | 유효성 검증 규칙 | Backend Lead | {{DATE}} |
| AMB-T01 | 에러 응답 형식 | Backend Lead | {{DATE}} |

### 🟡 FAQ 문서로 대응 가능
| ID | 항목 | 담당 |
|----|------|------|
| AMB-CU01 | 날짜 형식 표준 | Tech Writer |
| AMB-CU02 | 업무 시간 정의 | PM |

---

## 다음 단계
1. 수정된 의뢰서 검토: {{REVIEW_DATE}}
2. 외주사 킥오프 미팅: {{KICKOFF_DATE}}
3. Q&A 세션: {{QA_DATE}}
</output_format>
```

---

## 관련 프롬프트
- [2-1. 요구사항 → 개발 의뢰서 자동 정규화](./2-1-requirements-to-dev-spec.md)
