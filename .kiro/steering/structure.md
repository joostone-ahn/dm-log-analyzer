# 프로젝트 구조

## 디렉토리 구조

```
.
├── app.py                      # Flask 웹 서버 (라우트만)
├── converters.py               # 파일 변환 로직 (scat, tshark)
├── parsers.py                  # 프로토콜 파싱 로직 (RRC/NAS)
├── message_types.py            # 3GPP 메시지 타입 매핑
├── utils.py                    # 유틸리티 함수
├── rtcp_analyze.py             # RTCP 품질 분석 스크립트
├── sa_session_analyze.py       # SA 세션 분석 스크립트
├── requirements.txt            # Python 의존성
├── templates/
│   └── index.html             # 프론트엔드 UI (단일 페이지)
├── debug/                     # 디버그 및 테스트 스크립트
│   ├── check_frame237.py
│   ├── check_vonr_frame237.py
│   ├── debug_nr_rrc.py
│   ├── debug_nr_rrc2.py
│   ├── test_parse.py
│   └── test_parse_vonr.py
├── uploads/                   # 업로드된 로그 파일 저장 (HDF/SDM/QMDL/PCAP)
├── pcaps/                     # 변환된 PCAP 파일 저장
├── jsons/                     # 파싱된 JSON 파일 저장
└── specs/                     # 3GPP 표준 문서 (참고용)
```

## 핵심 파일 설명

### app.py

Flask 웹 서버 (모듈화된 구조):

- **라우트**:
  - `/`: 메인 페이지
  - `/upload`: 파일 업로드 및 처리 (POST)

- **임포트**:
  - `converters`: 파일 변환 함수
  - `parsers`: 프로토콜 파싱 함수

### converters.py

파일 변환 관련 함수:

- `check_dependencies()`: scat/tshark 설치 확인
- `convert_to_pcap()`: HDF/SDM/QMDL → PCAP 변환 (scat 사용)
- `convert_pcap_to_json()`: PCAP → JSON 파싱 (tshark 사용)

### parsers.py

프로토콜 파싱 관련 함수:

- `extract_message_info()`: RRC/NAS 메시지 정보 추출 (GSMTAPv3 배열 형식 지원)
- `determine_direction_and_nodes()`: 메시지 방향 및 노드 판단
- `extract_nested_nas_message()`: RRC 내부의 중첩된 NAS 메시지 추출
- `extract_nested_nr_rrc_message()`: LTE RRC 내부의 중첩된 NR RRC 메시지 추출
- `extract_nested_nas_from_transport()`: UL/DL NAS Transport 내부 메시지 추출
- `extract_sib_info()`: SystemInformation 메시지의 SIB 타입 추출
- `parse_call_flow()`: JSON → Call Flow 데이터 파싱

### message_types.py

3GPP 표준 기반 메시지 타입 매핑:

- `get_nas_5gs_message_name()`: NAS 5GS 메시지 타입 변환 (3GPP TS 24.501)
- `get_nas_eps_message_name()`: NAS EPS 메시지 타입 변환 (3GPP TS 24.301)

### utils.py

유틸리티 함수:

- `parse_json_with_duplicate_keys()`: 중복 키를 배열로 변환하는 JSON 파서
- `format_timestamp()`: 타임스탬프 포맷 변경 (hh:mm:ss.ms)
- `enhance_pco_fields()`: Protocol Configuration Options 필드 향상

### templates/index.html

단일 페이지 웹 애플리케이션:

- **UI 컴포넌트**:
  - 파일 업로드 버튼
  - 로딩 스피너
  - Call Flow 다이어그램 (5개 노드 + 화살표)
  - 상세 정보 패널 (슬라이드 인)

- **JavaScript 함수**:
  - `handleFileUpload()`: 파일 업로드 처리
  - `displayCallFlow()`: Call Flow 다이어그램 렌더링
  - `showDetails()`: 메시지 상세 정보 표시
  - `renderTree()`: IE 트리 구조 렌더링

### 분석 스크립트

- **rtcp_analyze.py**: VoNR RTCP 품질 분석 (MOS, Jitter, Loss Rate)
- **sa_session_analyze.py**: 5G SA 세션 분석 (PDU Session, QoS Flow)

### 디버그 스크립트 (debug/)

개발 및 디버깅 목적의 스크립트:

- **check_frame237.py**: 특정 프레임 파싱 검증
- **check_vonr_frame237.py**: VoNR 특정 프레임 검증
- **debug_nr_rrc.py**: NR RRC 메시지 디버깅
- **debug_nr_rrc2.py**: NR RRC 메시지 디버깅 (v2)
- **test_parse.py**: 파싱 로직 테스트
- **test_parse_vonr.py**: VoNR 파싱 테스트

## 모듈 구조

프로젝트는 기능별로 모듈화되어 있습니다:

```
app.py (Flask 라우트)
  ├─ converters.py (파일 변환)
  │   └─ utils.py (유틸리티)
  └─ parsers.py (프로토콜 파싱)
      ├─ message_types.py (메시지 타입 매핑)
      └─ utils.py (유틸리티)
```

## 데이터 흐름

1. 사용자가 HDF/SDM/QMDL/PCAP 파일 업로드
2. `converters.convert_to_pcap()`: scat으로 PCAP 변환 (PCAP인 경우 스킵)
3. `converters.convert_pcap_to_json()`: tshark로 JSON 파싱 (RRC/NAS 추출)
4. `parsers.parse_call_flow()`: JSON 파싱하여 Call Flow 데이터 생성
5. 프론트엔드에서 시각화

## 코딩 규칙

- 함수 및 변수명: snake_case
- 주석: 한글 사용
- 디버그 정보: `*_debug.txt`, `*_parse_debug.json` 파일로 저장
- 에러 처리: try-except로 감싸고 상세 에러 메시지 반환
- 모듈화: 기능별로 별도 파일로 분리하고 import 사용
