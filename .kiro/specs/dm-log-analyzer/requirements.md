# DM Log Call Flow Analyzer - 요구사항 명세서

## 1. 프로젝트 개요

### 1.1 목적
DM(Diagnostic Monitor) 로그 파일을 파싱하여 LTE/NR RRC 및 EPS/5GS NAS 메시지의 Call Flow를 시각화하는 웹 애플리케이션

### 1.2 핵심 가치
- 다양한 DM 로그 포맷(HDF, SDM, QMDL, PCAP) 통합 지원
- 자동 변환 파이프라인 (DM 로그 → PCAP → JSON → Call Flow)
- 5개 네트워크 노드(UE, eNB, gNB, MME, AMF) 간 메시지 흐름 시각화
- 메시지별 상세 Information Element(IE) 트리 구조 표시

### 1.3 사용자
- 5G/LTE 네트워크 엔지니어
- 프로토콜 분석가
- 통신 시스템 디버거

---

## 2. 기능 요구사항

### 2.1 파일 업로드 및 변환

#### 2.1.1 다양한 로그 포맷 지원
**사용자 스토리**: 엔지니어로서 다양한 DM 로그 포맷을 하나의 도구로 분석하고 싶다

**인수 기준**:
- [ ] HDF, SDM, QMDL, PCAP 파일 업로드 지원
- [ ] 파일 확장자 자동 감지
- [ ] 최대 2GB 파일 크기 지원
- [ ] 업로드 진행 상태 표시

#### 2.1.2 자동 변환 파이프라인
**사용자 스토리**: 엔지니어로서 수동 변환 없이 자동으로 Call Flow를 확인하고 싶다

**인수 기준**:
- [ ] scat을 사용한 DM 로그 → PCAP 변환
- [ ] tshark를 사용한 PCAP → JSON 파싱
- [ ] PCAP 파일 직접 업로드 시 scat 변환 스킵
- [ ] 변환 실패 시 명확한 에러 메시지 표시
- [ ] 큰 파일(100MB+) 처리 시 경고 메시지 표시

#### 2.1.3 의존성 체크
**사용자 스토리**: 시스템 관리자로서 필수 도구 설치 여부를 확인하고 싶다

**인수 기준**:
- [ ] scat 설치 확인
- [ ] tshark 설치 확인
- [ ] 미설치 시 명확한 에러 메시지

---

### 2.2 프로토콜 파싱

#### 2.2.1 LTE RRC 메시지 파싱
**사용자 스토리**: 엔지니어로서 LTE RRC 메시지를 정확하게 파싱하고 싶다

**인수 기준**:
- [x] PCCH, UL_CCCH, UL_DCCH, DL_CCCH, DL_DCCH, BCCH 채널 지원
- [x] SystemInformation 메시지에서 SIB 타입 추출 (SIB2, SIB3 등)
- [x] RRC 메시지 내 중첩된 NAS 메시지 추출
- [x] RRC 메시지 내 중첩된 NR RRC 메시지 추출 (EN-DC)
- [x] GSMTAPv3 배열 형식 자동 처리 (v1.1.0)
- [x] 메시지 방향(UL/DL) 자동 판단

#### 2.2.2 NR RRC 메시지 파싱
**사용자 스토리**: 엔지니어로서 5G NR RRC 메시지를 정확하게 파싱하고 싶다

**인수 기준**:
- [x] UL_CCCH, UL_DCCH, DL_CCCH, DL_DCCH, BCCH, PCCH 채널 지원
- [x] MIB, SystemInformationBlockType1 등 시스템 정보 파싱
- [x] RRCSetup, RRCReconfiguration 등 주요 메시지 파싱
- [x] GSMTAP 포맷 지원
- [x] GSMTAPv3 배열 형식 자동 처리 (v1.1.0)
  - tshark JSON 출력에서 `nr-rrc`가 배열로 나오는 경우 자동 감지
  - 배열의 첫 번째 요소(문자열)와 두 번째 요소(딕셔너리) 구분
  - 실제 메시지 데이터를 두 번째 요소에서 추출
- [x] 메시지 방향(UL/DL) 자동 판단

#### 2.2.3 NAS 5GS 메시지 파싱
**사용자 스토리**: 엔지니어로서 5G NAS 메시지를 정확하게 파싱하고 싶다

**인수 기준**:
- [ ] 5GMM 메시지 타입 변환 (3GPP TS 24.501 Table 9.7.1)
- [ ] 5GSM 메시지 타입 변환 (3GPP TS 24.501 Table 9.7.2)
- [ ] Registration, Service Request, PDU Session 관련 메시지 지원
- [ ] Security Protected NAS 메시지 감지
- [ ] UL/DL NAS Transport 내 중첩 메시지 추출
- [ ] 메시지 방향(UL/DL) 자동 판단

#### 2.2.4 NAS EPS 메시지 파싱
**사용자 스토리**: 엔지니어로서 LTE NAS 메시지를 정확하게 파싱하고 싶다

**인수 기준**:
- [ ] EMM 메시지 타입 변환 (3GPP TS 24.301 Table 9.8.1)
- [ ] ESM 메시지 타입 변환 (3GPP TS 24.301 Table 9.8.2)
- [ ] Attach, TAU, PDN Connectivity 관련 메시지 지원
- [ ] Security Protected NAS 메시지 감지
- [ ] 메시지 방향(UL/DL) 자동 판단

#### 2.2.5 Protocol Configuration Options (PCO) 향상
**사용자 스토리**: 엔지니어로서 PCO 필드를 사람이 읽기 쉬운 형태로 확인하고 싶다

**인수 기준**:
- [ ] PCO Protocol ID를 이름으로 변환 (3GPP TS 24.008)
- [ ] P-CSCF, DNS Server 주소 추출
- [ ] IPv4/IPv6 주소 표시
- [ ] 원본 데이터와 향상된 데이터 모두 제공

---

### 2.3 Call Flow 시각화

#### 2.3.1 노드 및 화살표 표시
**사용자 스토리**: 엔지니어로서 메시지 흐름을 직관적으로 확인하고 싶다

**인수 기준**:
- [ ] 5개 노드 표시: UE, eNB, gNB, MME, AMF
- [ ] 노드별 색상 구분
- [ ] 노드 간 세로선 표시
- [ ] 메시지 방향에 따른 화살표 표시 (UL: 파란색, DL: 빨간색)
- [ ] 화살표 위치 자동 계산

#### 2.3.2 메시지 정보 표시
**사용자 스토리**: 엔지니어로서 각 메시지의 핵심 정보를 한눈에 확인하고 싶다

**인수 기준**:
- [ ] 타임스탬프 표시 (hh:mm:ss.ms 형식)
- [ ] 메시지 이름 표시
- [ ] 중첩 메시지 표시 (예: "RRCSetup (Registration Request)")
- [ ] Source → Destination 표시
- [ ] 총 메시지 개수 표시

#### 2.3.3 인터랙션
**사용자 스토리**: 엔지니어로서 메시지를 클릭하여 상세 정보를 확인하고 싶다

**인수 기준**:
- [ ] 메시지 클릭 시 상세 패널 표시
- [ ] 마우스 호버 시 시각적 피드백
- [ ] ESC 키 또는 × 버튼으로 패널 닫기

---

### 2.4 상세 정보 패널

#### 2.4.1 기본 정보 표시
**사용자 스토리**: 엔지니어로서 메시지의 기본 정보를 확인하고 싶다

**인수 기준**:
- [ ] Frame Number 표시
- [ ] Timestamp 표시
- [ ] Protocol 표시
- [ ] Message 이름 표시
- [ ] Direction (UL/DL) 표시
- [ ] Source/Destination 노드 표시

#### 2.4.2 IE 트리 구조 표시
**사용자 스토리**: 엔지니어로서 메시지의 모든 Information Element를 트리 구조로 확인하고 싶다

**인수 기준**:
- [ ] JSON 구조를 트리 형태로 렌더링
- [ ] 키, 값, 타입별 색상 구분
- [ ] 중첩 구조 들여쓰기 표시
- [ ] 배열 요소 인덱스 표시
- [ ] 문자열이 인덱스로 분리된 경우 재구성
- [ ] PCO 향상 데이터 우선 표시

---

### 2.5 추가 분석 스크립트

#### 2.5.1 RTCP 품질 분석
**사용자 스토리**: 엔지니어로서 VoNR 통화 품질을 분석하고 싶다

**인수 기준**:
- [ ] NAS TFT Rule에서 UE/Server 포트 추출
- [ ] RTCP SR/RR 메시지 파싱
- [ ] Loss Rate, Jitter, MOS 계산
- [ ] DL/UL Stream 구분
- [ ] CSV 파일로 결과 저장

#### 2.5.2 SA 세션 분석
**사용자 스토리**: 엔지니어로서 5G SA PDU Session 정보를 분석하고 싶다

**인수 기준**:
- [ ] PDU Session Establishment Accept 메시지 파싱
- [ ] DNN, SST, SD, AMBR 정보 추출
- [ ] QoS Flow (QFI, 5QI, Rule ID) 정보 추출
- [ ] Default Flow 표시
- [ ] PNG 이미지로 시각화

---

## 3. 비기능 요구사항

### 3.1 성능
- 100MB PCAP 파일을 5분 이내에 처리
- 2GB 파일 지원 (타임아웃 없음)
- 1000개 이상 메시지 표시 가능

### 3.2 사용성
- 웹 브라우저에서 즉시 사용 가능
- 별도 설치 없이 파일 업로드만으로 분석 시작
- 직관적인 UI/UX

### 3.3 호환성
- macOS, Linux 지원
- Chrome, Firefox, Safari 브라우저 지원
- Python 3.8 이상

### 3.4 확장성
- 새로운 프로토콜 추가 용이
- 새로운 메시지 타입 추가 용이
- 플러그인 구조 (Lua 스크립트)

### 3.5 디버깅
- 변환 과정별 중간 파일 저장
- 디버그 정보 파일 생성 (*_debug.txt, *_parse_debug.json)
- PDML 포맷 추가 저장 (enum 값 확인용)

---

## 4. 제약사항

### 4.1 외부 도구 의존성
- scat: DM 로그 변환 필수
- tshark: PCAP 파싱 필수
- Wireshark Lua 플러그인 (선택사항)

### 4.2 프로토콜 제한
- RRC/NAS 메시지만 지원
- IP, TCP, UDP 레이어는 표시하지 않음

### 4.3 보안
- 로컬 서버에서만 실행 (0.0.0.0:8080)
- 업로드된 파일은 서버에 저장됨

---

## 5. 최근 업데이트

### v1.2.2 (2026-01-29)
**Docker 환경 NR RRC 파싱 문제 해결 및 GitHub Container Registry 배포**

**문제**: Docker 환경에서 NR RRC 메시지가 파싱되지 않는 문제 발견
- 로컬 환경: 302개 메시지 파싱
- Docker 환경: 254개 메시지 파싱 (48개 누락)
- 원인: scat Lua 플러그인이 임시 디렉토리에서 로드되지 않음

**해결**:
- Lua 플러그인을 Wireshark 전역 디렉토리에 설치 (`/usr/lib/x86_64-linux-gnu/wireshark/plugins/`)
- `converters.py`에서 전역 플러그인 경로 사용하도록 수정
- AMD64 단일 플랫폼 빌드로 변경 (멀티플랫폼 빌드 시간 문제 해결)
- `docker-compose.yml` 제거 (사용자에게 불필요)
- README 사용자 중심으로 재구성 (개발자 가이드 제거)

**GitHub Container Registry 배포**:
- `ghcr.io/joostone-ahn/dm-log-analyzer:latest` 이미지 제공
- 사용자가 직접 빌드 없이 이미지 pull하여 즉시 사용 가능
- Apple Silicon에서 `--platform linux/amd64` 옵션으로 실행 (Rosetta 2 에뮬레이션)

**영향**:
- Docker 환경에서 302개 메시지 정상 파싱 (로컬과 동일)
- 사용자 배포 간소화 (docker run 명령어 하나로 실행)
- 크로스 플랫폼 지원 (Windows x64, macOS Intel/Apple Silicon, Linux)

### v1.2.0 (2026-01-28)
**모듈화 리팩토링 및 Docker 배포**

**문제**: app.py 파일이 1120줄로 비대해져 유지보수가 어려움
- 파일 변환, 프로토콜 파싱, 메시지 타입 매핑, 유틸리티 함수가 모두 한 파일에 존재
- 코드 가독성 저하 및 테스트 어려움

**해결**:
- 기능별로 모듈 분리 (src 폴더로 이동)
  - `src/converters.py`: 파일 변환 로직 (scat, tshark)
  - `src/parsers.py`: 프로토콜 파싱 로직 (RRC/NAS)
  - `src/message_types.py`: 3GPP 메시지 타입 매핑
  - `src/utils.py`: 유틸리티 함수
  - `src/app.py`: Flask 라우트만 (90줄)
  - `src/rtcp_analyze.py`: RTCP 품질 분석 스크립트
  - `src/sa_session_analyze.py`: SA 세션 분석 스크립트
- 각 모듈에서 필요한 함수만 import
- debug 폴더 생성하여 디버그/테스트 스크립트 분리

**Docker 배포 추가**:
- Windows, macOS, Linux 크로스 플랫폼 지원
- `Dockerfile`: Ubuntu 22.04 베이스, Python 3, tshark, scat 설치
- `.dockerignore`: 불필요한 파일 제외
- **주요 특징**:
  - Docker 컨테이너는 Linux 환경이므로 Linux용 scat이 Windows에서도 작동
  - scat 없이도 PCAP 파일 직접 업로드 가능
  - 데이터 영구 저장 (볼륨 마운트)

**영향**:
- 코드 가독성 향상
- 모듈별 독립적인 테스트 가능
- 새로운 기능 추가 용이
- 유지보수성 대폭 개선
- 팀원들에게 쉽게 배포 가능

### v1.1.0 (2026-01-28)
**GSMTAPv3 배열 형식 지원 추가**

**문제**: VoNR 등 실제 로그에서 일부 NR RRC 메시지가 파싱되지 않는 문제 발견
- tshark JSON 출력에서 `nr-rrc`, `lte-rrc` 레이어가 배열 형식으로 나오는 경우 처리 불가
- 예: `"nr-rrc": ["NR Radio Resource Control (RRC) protocol", {...}]`

**해결**:
- `extract_message_info()` 함수에 배열 형식 자동 감지 로직 추가
- 배열의 첫 번째 요소(문자열)는 프로토콜 이름, 두 번째 요소(딕셔너리)가 실제 데이터
- 두 번째 요소에서 메시지 정보 추출하도록 수정
- None 체크 강화로 예외 처리 개선

**영향**:
- VoNR Service Request 시나리오의 RRC Setup Request/Setup/Setup Complete 메시지 정상 파싱
- GSMTAPv3 형식의 모든 RRC 메시지 지원
- 파싱 성공률 향상 (254개 → 302개 메시지)

---

## 6. 향후 개선 사항

- [ ] 실시간 로그 스트리밍
- [ ] 메시지 필터링 기능
- [ ] 타임라인 뷰 추가
- [ ] 다중 파일 비교 기능
- [ ] 통계 및 분석 기능
- [ ] RTCP 품질 분석 통합
- [ ] PDU Session/QoS Flow 분석 통합
- [ ] 메시지 검색 기능
- [ ] 북마크 기능
- [ ] 보고서 생성 (PDF/Excel)
