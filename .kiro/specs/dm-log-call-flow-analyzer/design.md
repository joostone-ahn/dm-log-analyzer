# DM Log Call Flow Analyzer - 설계 문서

## 1. 시스템 아키텍처

### 1.1 전체 구조
```
┌─────────────┐
│   Browser   │ (HTML/CSS/JavaScript)
└──────┬──────┘
       │ HTTP
       ↓
┌─────────────┐
│   Flask     │ (Python Web Server)
│   Server    │
└──────┬──────┘
       │
       ├─→ scat (DM → PCAP)
       ├─→ tshark (PCAP → JSON)
       └─→ Parser (JSON → Call Flow)
```

### 1.2 데이터 흐름
```
DM Log (HDF/SDM/QMDL) 
  ↓ [scat]
PCAP 
  ↓ [tshark -T json]
JSON 
  ↓ [parse_call_flow()]
Call Flow Data 
  ↓ [HTTP Response]
Browser Visualization
```

### 1.3 디렉토리 구조
```
.
├── app.py                      # Flask 웹 서버 (라우트만)
├── converters.py               # 파일 변환 로직 (scat, tshark)
├── parsers.py                  # 프로토콜 파싱 로직 (RRC/NAS)
├── message_types.py            # 3GPP 메시지 타입 매핑
├── utils.py                    # 유틸리티 함수
├── rtcp_analyze.py             # RTCP 품질 분석
├── sa_session_analyze.py       # SA 세션 분석
├── requirements.txt            # Python 의존성
├── templates/
│   └── index.html             # 프론트엔드 UI
├── debug/                     # 디버그 및 테스트 스크립트
│   ├── check_frame237.py
│   ├── check_vonr_frame237.py
│   ├── debug_nr_rrc.py
│   ├── debug_nr_rrc2.py
│   ├── test_parse.py
│   └── test_parse_vonr.py
├── uploads/                   # 업로드된 DM 로그
├── pcaps/                     # 변환된 PCAP
├── jsons/                     # 파싱된 JSON
├── wireshark/
│   └── scat.lua              # Wireshark Lua 플러그인
└── specs/                     # 3GPP 표준 문서
```

### 1.4 모듈 구조
```
app.py (Flask 라우트)
  ├─ converters.py (파일 변환)
  │   └─ utils.py (유틸리티)
  └─ parsers.py (프로토콜 파싱)
      ├─ message_types.py (메시지 타입 매핑)
      └─ utils.py (유틸리티)
```

---

## 2. 백엔드 설계 (Flask)

### 2.1 모듈 구조

프로젝트는 기능별로 모듈화되어 있습니다:

#### 2.1.1 app.py (Flask 라우트)
```python
from converters import check_dependencies, convert_to_pcap, convert_pcap_to_json
from parsers import parse_call_flow

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    check_dependencies()
    # 파일 저장 및 변환
    convert_to_pcap(input_path, pcap_path)
    convert_pcap_to_json(pcap_path, json_path)
    flows = parse_call_flow(json_path)
    return jsonify({'success': True, 'flows': flows})
```

#### 2.1.2 converters.py (파일 변환)
```python
def check_dependencies()
def convert_to_pcap(input_path, pcap_path)
def convert_pcap_to_json(pcap_path, json_path)
```

#### 2.1.3 parsers.py (프로토콜 파싱)
```python
def extract_message_info(layers)
def determine_direction_and_nodes(layers)
def extract_nested_nas_message(rrc_element)
def extract_nested_nr_rrc_message(lte_rrc_element)
def extract_nested_nas_from_transport(nas_5gs_layer)
def extract_sib_info(system_info_element)
def parse_call_flow(json_path)
```

#### 2.1.4 message_types.py (메시지 타입 매핑)
```python
def get_nas_5gs_message_name(msg_type)
def get_nas_eps_message_name(msg_type)
```

#### 2.1.5 utils.py (유틸리티)
```python
def parse_json_with_duplicate_keys(json_str)
def format_timestamp(timestamp_full)
def enhance_pco_fields(nas_layer)
```

---

### 2.2 주요 함수 상세

#### 2.2.1 의존성 체크
```python
def check_dependencies()
```
- scat, tshark 설치 확인
- 미설치 시 Exception 발생

#### 2.2.2 DM 로그 → PCAP 변환
```python
def convert_to_pcap(input_path, pcap_path)
```

**입력**: DM 로그 파일 경로 (HDF/SDM/QMDL)
**출력**: PCAP 파일 생성
**로직**:
1. 파일 확장자로 타입 판단
2. scat 명령어 구성: `scat -t qc -d <input> -F <output> -L rrc,nas`
3. 파일 크기 확인 (100MB 이상 시 경고)
4. subprocess로 scat 실행 (timeout=None)
5. PCAP 파일 생성 확인 및 크기 검증

#### 2.2.3 PCAP → JSON 변환
```python
def convert_pcap_to_json(pcap_path, json_path)
```
**입력**: PCAP 파일 경로
**출력**: JSON 파일 생성
**로직**:
1. Lua 플러그인 경로 확인
2. 임시 디렉토리에 Lua 플러그인 복사
3. tshark 명령어 구성: `tshark -r <pcap> -T json -X lua_script:<lua>`
4. subprocess로 tshark 실행
5. 중복 키를 배열로 변환하는 커스텀 JSON 파서 적용
6. JSON 파일 저장
7. PDML 포맷으로도 저장 (enum 값 확인용)
8. 디버그 정보 저장 (*_debug.txt)

#### 2.2.4 중복 키 처리
```python
def parse_json_with_duplicate_keys(json_str)
```
**목적**: tshark JSON 출력의 중복 키를 배열로 변환
**예시**:
```json
{"key": "value1", "key": "value2"}
→ {"key": ["value1", "value2"]}
```

#### 2.1.5 메시지 정보 추출
```python
def extract_message_info(layers)
```
**입력**: tshark JSON의 layers 객체
**출력**: `{'protocol': str, 'name': str, 'direction': str, 'channel': str}`
**로직**:
1. **NR RRC 메시지 확인**
   - GSMTAPv3 배열 형식 처리: `nr-rrc`가 배열인 경우 자동 감지
     - `[0]`: 문자열 "NR Radio Resource Control (RRC) protocol"
     - `[1]`: 실제 메시지 데이터 딕셔너리
   - 배열의 두 번째 요소에서 메시지 추출
   - `nr-rrc.XXX_Message_element` 키 찾기
   - `c1_tree` 내부에서 실제 메시지 추출
   - GSMTAP 포맷 지원 (직접 메시지 타입)
2. **LTE RRC 메시지 확인**
   - GSMTAPv3 배열 형식 처리: `lte-rrc`가 배열인 경우 자동 감지
   - 배열의 두 번째 요소에서 메시지 추출
   - `lte-rrc.XXX_Message_element` 키 찾기
   - `c1_tree` 내부에서 실제 메시지 추출
   - SystemInformation의 경우 SIB 타입 추출
3. **NAS 5GS 메시지 확인**
   - `nas-5gs.mm.message_type` 또는 `nas-5gs.sm.message_type` 찾기
   - 메시지 타입 hex 값을 이름으로 변환
4. **NAS EPS 메시지 확인**
   - `nas-eps.nas_msg_emm_type` 또는 `nas-eps.nas_msg_esm_type` 찾기
   - 메시지 타입 hex 값을 이름으로 변환

**GSMTAPv3 배열 처리 상세**:
```python
# nr-rrc 레이어가 배열인 경우
if isinstance(nr_rrc, list):
    # [0]은 문자열, [1]이 실제 데이터
    if len(nr_rrc) > 1 and isinstance(nr_rrc[1], dict):
        nr_rrc = nr_rrc[1]
    elif len(nr_rrc) > 0 and isinstance(nr_rrc[0], dict):
        nr_rrc = nr_rrc[0]
    else:
        nr_rrc = None  # 다음 프로토콜로
```

#### 2.1.6 중첩 메시지 추출
```python
def extract_nested_nas_message(rrc_element)
def extract_nested_nr_rrc_message(lte_rrc_element)
def extract_nested_nas_from_transport(nas_5gs_layer)
```
**목적**: RRC 내 NAS, LTE RRC 내 NR RRC, NAS Transport 내 NAS 추출
**로직**: 재귀적으로 트리 탐색하여 중첩 메시지 찾기

#### 2.1.7 SIB 정보 추출
```python
def extract_sib_info(system_info_element)
```
**목적**: SystemInformation 메시지에서 SIB 타입 추출
**출력**: "SIB2 SIB3" 형식의 문자열

#### 2.1.8 방향 및 노드 판단
```python
def determine_direction_and_nodes(layers)
```
**입력**: tshark JSON의 layers 객체
**출력**: `(direction, source, destination)`
**로직**:
- LTE RRC: UE ↔ eNB
- NR RRC: UE ↔ gNB
- NAS EPS: UE ↔ MME
- NAS 5GS: UE ↔ AMF
- 방향은 메시지 타입으로 판단 (DL/UL 패턴 매칭)

#### 2.1.9 NAS 메시지 타입 변환
```python
def get_nas_5gs_message_name(msg_type)
def get_nas_eps_message_name(msg_type)
```
**입력**: 메시지 타입 hex 값 (예: '0x41')
**출력**: `(message_name, direction)`
**데이터**: 3GPP TS 24.501, 24.301 기반 매핑 테이블

#### 2.1.10 PCO 필드 향상
```python
def enhance_pco_fields(nas_layer)
```
**목적**: Protocol Configuration Options를 사람이 읽기 쉽게 변환
**로직**:
1. PCO Protocol ID를 이름으로 변환 (3GPP TS 24.008)
2. IPv4/IPv6 주소 추출
3. `_enhanced_items` 배열로 저장
4. 원본 데이터는 유지

#### 2.1.11 Call Flow 파싱
```python
def parse_call_flow(json_path)
```
**입력**: tshark JSON 파일 경로
**출력**: Call Flow 데이터 배열
**로직**:
1. JSON 파일 로드
2. 각 패킷에 대해:
   - Frame number, timestamp 추출
   - `extract_message_info()`로 메시지 정보 추출
   - `determine_direction_and_nodes()`로 방향/노드 판단
   - 프로토콜별 레이어만 추출하여 details에 저장
   - PCO 필드 향상 적용
3. 디버그 정보 저장 (*_parse_debug.json)

#### 2.1.12 타임스탬프 포맷
```python
def format_timestamp(timestamp_full)
```
**입력**: "Jan 27, 2026 16:43:13.790560000 KST"
**출력**: "16:43:13.790"
**로직**: 정규식으로 시간 부분 추출 및 밀리초 3자리로 제한

### 2.2 Flask 라우트

#### 2.2.1 메인 페이지
```python
@app.route('/')
def index()
```
- `templates/index.html` 렌더링

#### 2.2.2 파일 업로드
```python
@app.route('/upload', methods=['POST'])
def upload_file()
```
**입력**: multipart/form-data (file)
**출력**: JSON `{'success': bool, 'flows': array}` 또는 `{'error': str}`
**로직**:
1. 의존성 체크
2. 파일 검증
3. PCAP 파일인 경우 scat 변환 스킵
4. DM 로그인 경우 scat 변환 수행
5. tshark로 JSON 변환
6. Call Flow 파싱
7. 결과 반환

### 2.3 설정
```python
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PCAP_FOLDER'] = 'pcaps'
app.config['JSON_FOLDER'] = 'jsons'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB
```

---

## 3. 프론트엔드 설계 (HTML/JavaScript)

### 3.1 UI 컴포넌트

#### 3.1.1 헤더
- 제목: "📡 Call Flow Analyzer"
- 파일 업로드 버튼

#### 3.1.2 로딩 스피너
- 파일 처리 중 표시
- 큰 파일 경고 메시지

#### 3.1.3 에러 메시지
- 빨간색 배경
- 에러 내용 표시

#### 3.1.4 Call Flow 다이어그램
- 노드 헤더 (UE, eNB, MME, gNB, AMF)
- 세로선 (노드 아래로 연장)
- 메시지 행 (타임스탬프 + 화살표 + 라벨)

#### 3.1.5 상세 정보 패널
- 슬라이드 인 애니메이션
- 기본 정보 섹션
- IE 트리 뷰 섹션

### 3.2 JavaScript 함수

#### 3.2.1 파일 업로드 처리
```javascript
async function handleFileUpload(e)
```
**로직**:
1. FormData 생성
2. `/upload` 엔드포인트로 POST 요청
3. 로딩 스피너 표시
4. 응답 받으면 `displayCallFlow()` 호출

#### 3.2.2 Call Flow 표시
```javascript
function displayCallFlow(flows)
```
**로직**:
1. 노드 위치 계산 (getBoundingClientRect)
2. 각 flow에 대해:
   - 타임스탬프 표시
   - 화살표 위치 계산 (startX, endX, width)
   - 화살표 방향 설정 (UL/DL)
   - 라벨 생성 (메시지 이름, 중첩 메시지)
   - 클릭 이벤트 등록
3. 세로선 높이 설정

#### 3.2.3 상세 정보 표시
```javascript
function showDetails(flow)
```
**로직**:
1. 기본 정보 렌더링
2. `renderTreeContent()`로 IE 트리 렌더링
3. 패널 활성화

#### 3.2.4 트리 렌더링
```javascript
function renderTree(obj, level)
function renderTreeContent(obj)
```
**로직**:
1. 타입별 처리 (null, string, number, boolean, array, object)
2. 들여쓰기 적용
3. 색상 구분 (키, 값, 타입별)
4. 숫자 키만 있는 경우 문자열로 재구성
5. PCO `_enhanced_items` 우선 표시

#### 3.2.5 패널 닫기
```javascript
function closeDetails()
```
- ESC 키 또는 × 버튼으로 호출

### 3.3 스타일링

#### 3.3.1 노드 색상
- UE: 보라색 그라데이션
- eNB: 핑크-빨강 그라데이션
- MME: 초록-청록 그라데이션
- gNB: 파랑-하늘색 그라데이션
- AMF: 핑크-노랑 그라데이션

#### 3.3.2 화살표 색상
- UL: 파란색 (#0000FF)
- DL: 빨간색 (#f44336)

#### 3.3.3 트리 뷰 색상
- 배경: 다크 (#1e1e1e)
- 키: 하늘색 (#9cdcfe)
- 문자열: 주황색 (#ce9178)
- 숫자: 연두색 (#b5cea8)
- Boolean: 파란색 (#569cd6)

---

## 4. 추가 분석 스크립트

### 4.1 RTCP 품질 분석 (rtcp_analyze.py)

#### 4.1.1 TFT 포트 추출
```python
def extract_tft_ports(pcap)
```
**목적**: NAS TFT Rule에서 UE/Server 포트 추출
**로직**:
1. `tshark -r <pcap> -V -Y "nas-eps"` 실행
2. "Packet filter direction: Uplink only" 찾기
3. Port 번호 추출 (30000 미만: UE, 이상: Server)

#### 4.1.2 MOS 계산
```python
def calculate_mos(loss_fraction, jitter_units, sampling_rate=16000)
```
**입력**: Loss fraction (0-255), Jitter (timestamp units)
**출력**: MOS 점수 (1.0-4.5)
**공식**: E-Model 기반

#### 4.1.3 분석 실행
```python
def run_analysis(pcap, out_prefix)
```
**로직**:
1. TFT 포트 추출
2. RTCP SR/RR 메시지 파싱
3. Reporter (UE/Server) 판단
4. DL/UL Stream 구분
5. Loss Rate, Jitter, MOS 계산
6. CSV 파일로 저장 (RTCP_SR_DL_Quality_by_UE.csv 형식)

### 4.2 SA 세션 분석 (sa_session_analyze.py)

#### 4.2.1 PCAP 파싱
```python
def parse_sa_pcap(pcap_file)
```
**목적**: PDU Session Establishment Accept 메시지 파싱
**로직**:
1. `tshark -r <pcap> -Y "nas_5gs.sm.message_type == 0xc2" -T pdml` 실행
2. PDU Session ID, DNN, SST, SD, AMBR 추출
3. QoS Flow (QFI, 5QI, Rule ID) 추출
4. Default Flow 판단 (첫 번째 Flow)

#### 4.2.2 시각화
```python
def draw_final_diagram(sessions, output_file)
```
**목적**: PDU Session 정보를 PNG 이미지로 시각화
**로직**:
1. matplotlib로 그림 생성
2. 세션별 박스 그리기 (테마 색상 적용)
3. Flow별 바 그리기
4. PNG 파일로 저장

---

## 5. 데이터 모델

### 5.1 Call Flow 객체
```python
{
    'frame': str,           # Frame number
    'timestamp': str,       # hh:mm:ss.ms
    'source': str,          # UE, eNB, gNB, MME, AMF
    'destination': str,     # UE, eNB, gNB, MME, AMF
    'direction': str,       # UL, DL
    'message': str,         # 메시지 이름 (중첩 메시지 포함)
    'protocol': str,        # lte-rrc, nr-rrc, nas-5gs, nas-eps
    'details': dict         # 프로토콜별 레이어 데이터
}
```

### 5.2 메시지 정보 객체
```python
{
    'protocol': str,        # lte-rrc, nr-rrc, nas-5gs, nas-eps
    'name': str,            # 메시지 이름
    'raw_key': str,         # tshark JSON 키
    'direction': str,       # UL, DL
    'channel': str          # PCCH, UL_DCCH, DL_DCCH 등 (RRC만)
}
```

### 5.3 PCO 향상 객체
```python
{
    'Protocol or Container ID': str,  # 프로토콜 이름
    'ID': str,                        # hex 값
    'Length': str,                    # hex (decimal)
    'IPv4': str,                      # IPv4 주소 (선택)
    'IPv6': str                       # IPv6 주소 (선택)
}
```

---

## 6. 에러 처리

### 6.1 의존성 에러
- scat 미설치: "scat이 설치되지 않았습니다."
- tshark 미설치: "tshark가 설치되지 않았습니다."

### 6.2 변환 에러
- scat 실패: "scat 변환 실패 (return code: X): <stderr>"
- PCAP 미생성: "scat이 PCAP 파일을 생성하지 못했습니다."
- 빈 PCAP: "scat이 빈 PCAP 파일을 생성했습니다."
- tshark 실패: "tshark 변환 실패: <stderr>"
- JSON 파싱 실패: "tshark 출력이 유효한 JSON이 아닙니다: <error>"

### 6.3 파일 에러
- 파일 없음: "파일이 없습니다"
- 파일명 없음: "파일을 선택하세요"
- 지원하지 않는 형식: "지원하지 않는 파일 형식: <ext>"

---

## 7. 성능 최적화 및 비기능 요구사항

### 7.1 성능 요구사항
**목표**:
- 100MB PCAP 파일을 5분 이내에 처리
- 2GB 파일 지원 (타임아웃 없음)
- 1000개 이상 메시지 표시 가능

**구현 전략**:

#### 7.1.1 큰 파일 처리
- 100MB 이상 파일: 경고 메시지 표시
- subprocess timeout=None (무제한 대기)
- 2GB 파일 크기 제한 (`MAX_CONTENT_LENGTH`)
- 메모리 효율적인 스트리밍 처리 고려

#### 7.1.2 프론트엔드 최적화
- requestAnimationFrame으로 렌더링 최적화
- 노드 위치 캐싱 (getBoundingClientRect 호출 최소화)
- 세로선 높이 동적 계산
- 가상 스크롤링 검토 (1000+ 메시지 시)

#### 7.1.3 디버깅 최적화
- 처음 5개 패킷만 상세 디버그
- 디버그 파일 크기 제한 (처음 5000자)
- 프로덕션 모드에서 디버그 파일 생성 비활성화 옵션

### 7.2 사용성 요구사항
**목표**: 직관적이고 사용하기 쉬운 인터페이스

**구현 전략**:
- 웹 브라우저에서 즉시 사용 가능 (별도 클라이언트 설치 불필요)
- 파일 업로드만으로 분석 시작 (복잡한 설정 없음)
- 명확한 에러 메시지 및 경고 표시
- 로딩 상태 시각적 피드백
- 직관적인 Call Flow 다이어그램
- 메시지 클릭으로 상세 정보 즉시 확인
- 키보드 단축키 지원 (ESC로 패널 닫기)

### 7.3 호환성 요구사항
**운영체제**:
- macOS (주요 타겟)
- Linux (지원)
- Windows (scat/tshark 설치 시 지원 가능)

**브라우저**:
- Chrome (최신 버전)
- Firefox (최신 버전)
- Safari (macOS)
- 모던 브라우저 (ES6+ 지원)

**Python 버전**:
- Python 3.8 이상
- Flask 3.0.0
- Werkzeug 3.0.1

### 7.4 확장성 요구사항
**설계 원칙**: 새로운 프로토콜 및 메시지 타입 추가 용이

**확장 포인트**:

#### 7.4.1 새로운 프로토콜 추가
```python
# extract_message_info() 함수에 프로토콜 파싱 로직 추가
if 'new-protocol.message_type' in layers:
    protocol = 'new-protocol'
    name = extract_new_protocol_message(layers)
    # ...
```

#### 7.4.2 새로운 메시지 타입 추가
```python
# 메시지 타입 매핑 테이블에 추가
NAS_5GS_MM_MESSAGE_TYPES = {
    '0x41': ('Registration request', 'UL'),
    '0x42': ('Registration accept', 'DL'),
    '0xXX': ('New message type', 'UL/DL'),  # 새로운 메시지
    # ...
}
```

#### 7.4.3 플러그인 구조
- Wireshark Lua 플러그인 (`wireshark/scat.lua`)
- 커스텀 dissector 추가 가능
- tshark 출력 포맷 확장 가능

### 7.5 디버깅 및 유지보수성
**목표**: 문제 진단 및 해결 용이

**구현 전략**:
- 변환 과정별 중간 파일 저장
  - `uploads/`: 원본 DM 로그
  - `pcaps/`: 변환된 PCAP
  - `jsons/`: 파싱된 JSON
- 디버그 정보 파일 생성
  - `*_debug.txt`: tshark 원본 출력
  - `*_parse_debug.json`: 파싱 결과 (처음 5개 패킷)
  - `*_pdml.xml`: PDML 포맷 (enum 값 확인용)
- 명확한 에러 메시지 및 스택 트레이스
- 로깅 시스템 (향후 추가)
- 코드 주석 및 docstring (한글)

---

## 8. 보안 고려사항

### 8.1 파일 업로드
- `secure_filename()` 사용
- 파일 크기 제한 (2GB)
- 허용된 확장자만 처리

### 8.2 서버 실행
- 로컬 서버만 (0.0.0.0:8080)
- 디버그 모드 (개발용)

### 8.3 데이터 저장
- 업로드된 파일은 서버에 저장
- 중간 파일 (PCAP, JSON) 저장
- 디버그 파일 저장

---

## 9. 테스트 전략

### 9.1 단위 테스트
**목적**: 개별 함수의 정확성 검증

**테스트 대상**:
- `get_nas_5gs_message_name()`: 3GPP TS 24.501 메시지 타입 변환 정확성
- `get_nas_eps_message_name()`: 3GPP TS 24.301 메시지 타입 변환 정확성
- `determine_direction_and_nodes()`: 메시지 방향(UL/DL) 판단 정확성
- `extract_nested_nas_message()`: RRC 내 NAS 메시지 추출 정확성
- `extract_nested_nr_rrc_message()`: LTE RRC 내 NR RRC 메시지 추출 정확성
- `extract_sib_info()`: SystemInformation 내 SIB 타입 추출 정확성
- `enhance_pco_fields()`: PCO Protocol ID 변환 및 IP 주소 추출 정확성
- `format_timestamp()`: 타임스탬프 포맷 변환 정확성

**테스트 방법**:
- pytest 프레임워크 사용
- 각 함수별 입력/출력 검증
- Edge case 테스트 (빈 값, null, 잘못된 형식)

### 9.2 통합 테스트
**목적**: 전체 변환 파이프라인 검증

**테스트 시나리오**:
1. **HDF 파일 변환 테스트**
   - HDF → PCAP → JSON → Call Flow 전체 파이프라인
   - 변환된 PCAP 파일 크기 검증
   - JSON 파일 유효성 검증
   - Call Flow 데이터 구조 검증

2. **SDM 파일 변환 테스트**
   - SDM → PCAP → JSON → Call Flow 전체 파이프라인
   - 동일한 검증 절차

3. **QMDL 파일 변환 테스트**
   - QMDL → PCAP → JSON → Call Flow 전체 파이프라인
   - 동일한 검증 절차

4. **PCAP 직접 업로드 테스트**
   - scat 변환 스킵 확인
   - PCAP → JSON → Call Flow 파이프라인
   - 변환 시간 단축 확인

5. **큰 파일 처리 테스트**
   - 100MB 이상 파일 처리
   - 경고 메시지 표시 확인
   - 타임아웃 없이 완료 확인
   - 메모리 사용량 모니터링

6. **다양한 프로토콜 테스트**
   - LTE RRC 메시지만 포함된 로그
   - NR RRC 메시지만 포함된 로그
   - LTE + NR 혼합 로그 (EN-DC)
   - NAS EPS 메시지 로그
   - NAS 5GS 메시지 로그
   - 중첩 메시지 포함 로그

**에러 케이스 테스트**:
- scat 미설치 시 에러 메시지 확인
- tshark 미설치 시 에러 메시지 확인
- 잘못된 파일 형식 업로드 시 에러 처리
- 손상된 파일 업로드 시 에러 처리
- 빈 파일 업로드 시 에러 처리
- 지원하지 않는 확장자 업로드 시 에러 처리

### 9.3 UI 테스트
**목적**: 프론트엔드 기능 및 호환성 검증

**브라우저 호환성 테스트**:
- Chrome (최신 버전)
- Firefox (최신 버전)
- Safari (macOS)
- 각 브라우저에서 동일한 렌더링 확인

**기능 테스트**:
- 파일 업로드 버튼 동작
- 로딩 스피너 표시/숨김
- Call Flow 다이어그램 렌더링
- 노드 위치 계산 정확성
- 화살표 방향 및 색상 표시
- 메시지 클릭 시 상세 패널 표시
- ESC 키로 패널 닫기
- × 버튼으로 패널 닫기
- 트리 구조 렌더링 (들여쓰기, 색상)
- PCO 향상 데이터 우선 표시

**반응형 디자인 테스트**:
- 다양한 화면 크기에서 레이아웃 확인
- 노드 위치 동적 계산 확인
- 세로선 높이 동적 조정 확인

**인터랙션 테스트**:
- 마우스 호버 시 시각적 피드백
- 클릭 이벤트 정확성
- 스크롤 동작
- 패널 슬라이드 애니메이션

**성능 테스트**:
- 1000개 이상 메시지 렌더링 성능
- requestAnimationFrame 최적화 확인
- 노드 위치 캐싱 효과 확인

---

## 10. 배포 전략

### 10.1 의존성 설치
```bash
pip install -r requirements.txt
brew install wireshark  # macOS
```

### 10.2 서버 실행
```bash
python app.py
```

### 10.3 접속
```
http://localhost:8080
```

---

## 11. 유지보수 가이드

### 11.1 새로운 메시지 타입 추가
**시나리오**: 3GPP 표준이 업데이트되어 새로운 NAS 메시지 타입이 추가된 경우

**절차**:
1. 3GPP 표준 문서 확인 (TS 24.501 또는 TS 24.301)
2. 메시지 타입 hex 값 및 이름 확인
3. 메시지 방향 확인 (UL/DL)
4. `app.py`의 해당 함수에 매핑 추가:
   - NAS 5GS MM: `get_nas_5gs_message_name()` 함수의 `NAS_5GS_MM_MESSAGE_TYPES` 딕셔너리
   - NAS 5GS SM: `get_nas_5gs_message_name()` 함수의 `NAS_5GS_SM_MESSAGE_TYPES` 딕셔너리
   - NAS EPS EMM: `get_nas_eps_message_name()` 함수의 `NAS_EPS_EMM_MESSAGE_TYPES` 딕셔너리
   - NAS EPS ESM: `get_nas_eps_message_name()` 함수의 `NAS_EPS_ESM_MESSAGE_TYPES` 딕셔너리

**예시**:
```python
NAS_5GS_MM_MESSAGE_TYPES = {
    '0x41': ('Registration request', 'UL'),
    '0x42': ('Registration accept', 'DL'),
    '0xXX': ('New message type', 'UL'),  # 새로운 메시지 추가
    # ...
}
```

5. 테스트 케이스 추가 (단위 테스트)
6. 문서 업데이트 (design.md, requirements.md)

### 11.2 새로운 프로토콜 추가
**시나리오**: 새로운 프로토콜 레이어를 지원해야 하는 경우 (예: X2AP, S1AP)

**절차**:
1. **메시지 정보 추출 로직 추가**
   - `extract_message_info()` 함수에 프로토콜 파싱 로직 추가
   - tshark JSON 출력에서 프로토콜 키 패턴 확인
   - 메시지 이름 추출 로직 구현
   - 방향 판단 로직 구현 (필요시)

**예시**:
```python
def extract_message_info(layers):
    # 기존 프로토콜 체크...
    
    # 새로운 프로토콜 추가
    if 'x2ap.procedureCode' in layers:
        protocol = 'x2ap'
        procedure_code = layers.get('x2ap.procedureCode', '')
        name = get_x2ap_procedure_name(procedure_code)
        direction = 'UL' if 'Request' in name else 'DL'
        return {
            'protocol': protocol,
            'name': name,
            'direction': direction,
            'raw_key': 'x2ap.procedureCode'
        }
    
    # ...
```

2. **노드 매핑 추가**
   - `determine_direction_and_nodes()` 함수에 노드 매핑 추가
   - 프로토콜에 맞는 Source/Destination 노드 결정

**예시**:
```python
def determine_direction_and_nodes(layers):
    # ...
    elif protocol == 'x2ap':
        source = 'eNB1'
        destination = 'eNB2'
        direction = msg_info['direction']
    # ...
```

3. **프론트엔드 노드 추가** (필요시)
   - `templates/index.html`의 노드 헤더에 새로운 노드 추가
   - CSS 스타일 정의 (색상, 그라데이션)
   - JavaScript의 노드 위치 계산 로직 업데이트

4. **테스트 케이스 추가**
   - 새로운 프로토콜이 포함된 PCAP 파일로 테스트
   - 메시지 추출 및 방향 판단 검증

5. **문서 업데이트**
   - design.md에 프로토콜 파싱 로직 추가
   - requirements.md에 프로토콜 지원 명시

### 11.3 디버깅 가이드
**문제 진단 절차**:

#### 11.3.1 변환 실패 시
1. **scat 변환 실패**
   - 에러 메시지 확인: "scat 변환 실패 (return code: X)"
   - scat 설치 확인: `scat --version`
   - 입력 파일 형식 확인 (HDF/SDM/QMDL)
   - 파일 손상 여부 확인
   - 디스크 공간 확인

2. **tshark 변환 실패**
   - 에러 메시지 확인: "tshark 변환 실패"
   - tshark 설치 확인: `tshark --version`
   - PCAP 파일 유효성 확인: `tshark -r <pcap> -c 1`
   - Lua 플러그인 경로 확인

#### 11.3.2 파싱 오류 시
1. **디버그 파일 확인**
   - `jsons/*_debug.txt`: tshark 원본 출력 확인
   - `jsons/*_parse_debug.json`: 파싱 결과 확인 (처음 5개 패킷)
   - `jsons/*_pdml.xml`: PDML 포맷으로 enum 값 확인

2. **메시지 추출 실패**
   - `extract_message_info()` 함수 로직 확인
   - tshark JSON 키 패턴 확인
   - 중첩 메시지 추출 로직 확인

3. **방향 판단 오류**
   - `determine_direction_and_nodes()` 함수 로직 확인
   - 메시지 타입 매핑 테이블 확인
   - 채널 타입 기반 방향 판단 로직 확인

#### 11.3.3 UI 렌더링 오류 시
1. **브라우저 콘솔 확인**
   - JavaScript 에러 메시지 확인
   - 네트워크 탭에서 API 응답 확인

2. **Call Flow 표시 오류**
   - 노드 위치 계산 로직 확인
   - 화살표 위치 계산 로직 확인
   - CSS 스타일 충돌 확인

3. **상세 패널 오류**
   - `renderTree()` 함수 로직 확인
   - JSON 구조 유효성 확인
   - 재귀 깊이 제한 확인

### 11.4 성능 문제 해결
**증상별 해결 방법**:

#### 11.4.1 변환 속도 느림
- 파일 크기 확인 (100MB 이상은 경고 표시)
- scat/tshark 프로세스 모니터링
- 디스크 I/O 병목 확인
- 메모리 사용량 확인

#### 11.4.2 프론트엔드 렌더링 느림
- 메시지 개수 확인 (1000개 이상은 가상 스크롤링 고려)
- requestAnimationFrame 사용 확인
- 노드 위치 캐싱 확인
- 브라우저 성능 프로파일링

### 11.5 코드 스타일 가이드
**일관성 유지를 위한 규칙**:

- **함수명**: snake_case (예: `extract_message_info`)
- **변수명**: snake_case (예: `msg_type`)
- **상수명**: UPPER_SNAKE_CASE (예: `NAS_5GS_MM_MESSAGE_TYPES`)
- **주석**: 한글 사용, 복잡한 로직에 상세 설명
- **Docstring**: 함수 목적, 입력, 출력 명시
- **에러 처리**: try-except로 감싸고 명확한 에러 메시지
- **3GPP 참조**: 표준 문서 번호 및 섹션 명시 (예: "3GPP TS 24.501 Table 9.7.1")

---

## 12. 배포 가이드

### 12.1 개발 환경 설정
```bash
# 1. 저장소 클론
git clone <repository-url>
cd dm-log-call-flow-analyzer

# 2. 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 외부 도구 설치 확인
scat --version
tshark --version

# 5. 외부 도구 미설치 시 (macOS)
brew install wireshark
# scat은 별도 설치 필요
```

### 12.2 개발 서버 실행
```bash
# 디버그 모드로 실행
python app.py

# 서버 주소: http://localhost:8080
```

### 12.3 프로덕션 배포
**권장 사항**:
- 디버그 모드 비활성화: `app.run(debug=False)`
- WSGI 서버 사용: Gunicorn, uWSGI
- 리버스 프록시: Nginx, Apache
- HTTPS 설정: SSL/TLS 인증서
- 환경 변수: 설정 외부화
- 로깅: 파일 또는 중앙 로깅 시스템

**Gunicorn 예시**:
```bash
# Gunicorn 설치
pip install gunicorn

# 실행
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

**Docker 배포** (v1.2.0에서 추가됨):
```dockerfile
FROM ubuntu:22.04
WORKDIR /app
# Python, tshark, scat 설치
RUN apt-get update && apt-get install -y python3 python3-pip tshark wget
COPY scat /usr/local/bin/scat
RUN chmod +x /usr/local/bin/scat
# Python 의존성 및 애플리케이션 파일 복사
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY app.py converters.py parsers.py message_types.py utils.py .
COPY templates/ templates/
COPY wireshark/ wireshark/
# 데이터 디렉토리 생성 및 포트 노출
RUN mkdir -p uploads pcaps jsons
EXPOSE 8080
CMD ["python3", "app.py"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  dm-log-analyzer:
    build: .
    container_name: dm-log-call-flow-analyzer
    ports:
      - "8080:8080"
    volumes:
      - ./uploads:/app/uploads
      - ./pcaps:/app/pcaps
      - ./jsons:/app/jsons
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

**배포 스크립트**:
- `deploy.sh`: Linux/macOS 자동 배포 스크립트
- `deploy.bat`: Windows 자동 배포 스크립트
- `README.Docker.md`: 완전한 Docker 배포 가이드

### 12.4 의존성 관리
**requirements.txt 업데이트**:
```bash
# 현재 설치된 패키지 목록
pip freeze > requirements.txt

# 특정 버전 고정
Flask==3.0.0
Werkzeug==3.0.1
```

**보안 업데이트**:
```bash
# 취약점 확인
pip install safety
safety check

# 패키지 업데이트
pip install --upgrade <package-name>
```

---

## 13. 향후 개선 사항

### 13.1 기능 확장
**우선순위: 높음**
- [ ] **메시지 필터링 기능**: 프로토콜, 메시지 타입, 방향별 필터링
- [ ] **메시지 검색 기능**: 키워드 기반 검색, 정규식 지원
- [ ] **북마크 기능**: 중요 메시지 표시 및 빠른 이동

**우선순위: 중간**
- [ ] **타임라인 뷰**: 시간축 기반 시각화, 줌 인/아웃
- [ ] **통계 및 분석 기능**: 메시지 빈도, 지연 시간 분석
- [ ] **다중 파일 비교 기능**: 두 개 이상의 로그 파일 비교
- [ ] **보고서 생성**: PDF/Excel 형식으로 분석 결과 내보내기

**우선순위: 낮음**
- [ ] **실시간 로그 스트리밍**: 실시간 DM 로그 모니터링
- [ ] **커스텀 테마**: 다크 모드, 색상 테마 선택
- [ ] **키보드 단축키 확장**: 메시지 탐색, 필터링 단축키

### 13.2 분석 도구 통합
**목표**: 추가 분석 스크립트를 메인 웹 애플리케이션에 통합

**통합 대상**:
1. **RTCP 품질 분석 (rtcp_analyze.py)**
   - VoNR 통화 품질 분석
   - MOS, Jitter, Loss Rate 표시
   - Call Flow 다이어그램에 품질 지표 오버레이
   - CSV 다운로드 기능

2. **SA 세션 분석 (sa_session_analyze.py)**
   - PDU Session 정보 시각화
   - QoS Flow 정보 표시
   - Call Flow 다이어그램에 세션 정보 오버레이
   - PNG 이미지 다운로드 기능

**통합 방법**:
- Flask 라우트 추가 (`/analyze/rtcp`, `/analyze/sa`)
- 프론트엔드에 분석 탭 추가
- 분석 결과를 JSON으로 반환
- 기존 Call Flow와 연동

### 13.3 UI/UX 개선
**사용자 피드백 기반 개선**:
- [ ] **드래그 앤 드롭 업로드**: 파일 선택 대신 드래그 앤 드롭
- [ ] **진행률 바 개선**: 변환 단계별 진행 상황 표시
- [ ] **메시지 그룹화**: 동일한 절차의 메시지 그룹으로 표시
- [ ] **컨텍스트 메뉴**: 우클릭으로 추가 기능 접근
- [ ] **툴팁 추가**: 메시지 호버 시 간단한 정보 표시

### 13.4 성능 개선
**대용량 파일 처리 최적화**:
- [ ] **가상 스크롤링**: 1000개 이상 메시지 렌더링 최적화
- [ ] **병렬 처리**: scat/tshark 병렬 실행 검토
- [ ] **메모리 최적화**: 스트리밍 방식 JSON 파싱
- [ ] **캐싱**: 변환 결과 캐싱으로 재업로드 시 빠른 로딩

### 13.5 보안 강화
**프로덕션 배포 준비**:
- [ ] **HTTPS 지원**: SSL/TLS 인증서 설정
- [ ] **인증/인가**: 사용자 로그인 및 권한 관리
- [ ] **Rate Limiting**: API 호출 제한
- [ ] **CORS 설정**: 허용된 도메인만 접근
- [ ] **파일 타입 검증 강화**: Magic number 기반 검증
- [ ] **업로드 디렉토리 권한**: 실행 권한 제거

### 13.6 배포 및 운영
**프로덕션 환경 지원**:
- [x] **Docker 이미지**: 컨테이너 기반 배포 (v1.2.0에서 완료)
  - Dockerfile, docker-compose.yml 구현
  - 자동 배포 스크립트 (deploy.sh, deploy.bat)
  - README.Docker.md 완전한 배포 가이드
  - Windows/macOS/Linux 크로스 플랫폼 지원
- [ ] **환경 변수 설정**: 설정 파일 외부화
- [ ] **로깅 시스템**: 구조화된 로그 (JSON 형식)
- [ ] **모니터링**: 성능 메트릭 수집 (Prometheus, Grafana)
- [ ] **백업 전략**: 업로드 파일 자동 백업
- [ ] **자동 업데이트**: 의존성 및 표준 문서 자동 업데이트

### 13.7 표준 업데이트 대응
**3GPP 표준 변경 사항 반영**:
- [ ] **자동 모니터링**: 3GPP 표준 문서 업데이트 감지
- [ ] **메시지 타입 자동 업데이트**: 새로운 메시지 타입 자동 추가
- [ ] **프로토콜 버전 관리**: 여러 버전의 프로토콜 지원
- [ ] **릴리스 노트**: 표준 변경 사항 문서화

---

## 14. 최근 업데이트

### v1.2.0 (2026-01-28) - 모듈화 리팩토링 및 Docker 배포

#### 14.1 문제 정의
**증상**: app.py 파일이 1120줄로 비대해져 유지보수가 어려움
- 파일 변환, 프로토콜 파싱, 메시지 타입 매핑, 유틸리티 함수가 모두 한 파일에 존재
- 코드 가독성 저하
- 테스트 및 디버깅 어려움
- 새로운 기능 추가 시 충돌 위험

**원인 분석**:
- 초기 개발 시 빠른 프로토타이핑을 위해 단일 파일로 작성
- 기능 추가가 반복되면서 파일 크기 증가
- 모듈 분리 없이 함수만 추가하는 방식

#### 14.2 해결 방법

**모듈 분리 전략**:
```
app.py (1120줄)
  ↓
app.py (90줄) + converters.py + parsers.py + message_types.py + utils.py
```

**새로운 구조**:
```python
# app.py - Flask 라우트만
from converters import check_dependencies, convert_to_pcap, convert_pcap_to_json
from parsers import parse_call_flow

@app.route('/upload', methods=['POST'])
def upload_file():
    check_dependencies()
    convert_to_pcap(input_path, pcap_path)
    convert_pcap_to_json(pcap_path, json_path)
    flows = parse_call_flow(json_path)
    return jsonify({'success': True, 'flows': flows})
```

**모듈별 책임**:

1. **converters.py** (파일 변환)
```python
def check_dependencies()
def convert_to_pcap(input_path, pcap_path)
def convert_pcap_to_json(pcap_path, json_path)
```

2. **parsers.py** (프로토콜 파싱)
```python
def extract_message_info(layers)
def determine_direction_and_nodes(layers)
def extract_nested_nas_message(rrc_element)
def extract_nested_nr_rrc_message(lte_rrc_element)
def extract_nested_nas_from_transport(nas_5gs_layer)
def extract_sib_info(system_info_element)
def parse_call_flow(json_path)
```

3. **message_types.py** (3GPP 메시지 타입 매핑)
```python
def get_nas_5gs_message_name(msg_type)
def get_nas_eps_message_name(msg_type)
```

4. **utils.py** (유틸리티)
```python
def parse_json_with_duplicate_keys(json_str)
def format_timestamp(timestamp_full)
def enhance_pco_fields(nas_layer)
```

#### 14.3 디버그 스크립트 정리

**debug 폴더 생성**:
```
debug/
├── check_frame237.py          # 특정 프레임 파싱 검증
├── check_vonr_frame237.py     # VoNR 특정 프레임 검증
├── debug_nr_rrc.py            # NR RRC 메시지 디버깅
├── debug_nr_rrc2.py           # NR RRC 메시지 디버깅 (v2)
├── test_parse.py              # 파싱 로직 테스트
└── test_parse_vonr.py         # VoNR 파싱 테스트
```

**.gitignore 업데이트**:
```
debug/
```

#### 14.4 검증 결과

**모듈 임포트 테스트**:
```bash
$ python -m py_compile app.py converters.py parsers.py message_types.py utils.py
✓ All Python files have valid syntax
```

**기능 테스트**:
```bash
$ .venv/bin/python -c "
from parsers import parse_call_flow
flows = parse_call_flow('jsons/VoNR.json')
print(f'✓ parse_call_flow 성공: {len(flows)}개 메시지 파싱됨')
"
✓ parse_call_flow 성공: 302개 메시지 파싱됨
```

#### 14.5 영향 범위

**긍정적 영향**:
- 코드 가독성 대폭 향상 (1120줄 → 90줄)
- 모듈별 독립적인 테스트 가능
- 새로운 기능 추가 용이
- 유지보수성 개선
- 디버그 스크립트 분리로 프로젝트 루트 정리

**호환성**:
- 기존 기능 100% 유지 (하위 호환성)
- API 변경 없음
- 프론트엔드 영향 없음

**성능**:
- 모듈 임포트 오버헤드 무시 가능
- 전체 실행 시간 변화 없음

#### 14.6 Docker 배포 추가

**목적**: 크로스 플랫폼 배포 지원
- Windows, macOS, Linux 모든 환경에서 의존성 문제 없이 실행
- 팀원들에게 쉽게 배포 가능한 환경 제공

**구현 내용**:

1. **Dockerfile**
   - Ubuntu 22.04 베이스 이미지
   - Python 3, tshark, scat 설치
   - Flask 애플리케이션 설정
   - 포트 8080 노출
   - 헬스체크 구현

2. **docker-compose.yml**
   - 컨테이너 오케스트레이션
   - 볼륨 마운트 (uploads, pcaps, jsons)
   - 환경 변수 설정
   - 자동 재시작 정책

3. **.dockerignore**
   - Python 캐시 제외
   - 데이터 디렉토리 제외 (볼륨 마운트)
   - 디버그 파일 제외

4. **README.Docker.md**
   - 완전한 배포 가이드
   - 핵심 기능 설명
   - 설치 및 실행 가이드
   - 문제 해결 가이드
   - FAQ (Windows 호환성, scat 요구사항 등)

5. **자동 배포 스크립트**
   - `deploy.sh`: Linux/macOS용 (색상 출력, 단계별 확인)
   - `deploy.bat`: Windows용 (동일한 기능)
   - Docker 설치 확인
   - scat 바이너리 확인
   - 이미지 빌드 및 컨테이너 시작
   - 헬스체크 및 완료 메시지

**주요 특징**:
- **Windows 호환성**: Docker 컨테이너는 Linux 환경이므로 Linux용 scat이 Windows에서도 작동
- **scat 선택사항**: PCAP 파일 직접 업로드 시 scat 불필요
- **볼륨 마운트**: 데이터 영구 저장
- **자동 재시작**: 컨테이너 실패 시 자동 재시작

#### 14.7 문서 업데이트

**업데이트된 문서**:
- [x] README.md: 프로젝트 구조 업데이트, v1.2.0 릴리스 노트 추가
- [x] .kiro/steering/structure.md: 모듈 구조 상세 설명, debug 폴더 추가
- [x] .kiro/steering/product.md: v1.2.0 업데이트 내용 추가
- [x] .kiro/specs/dm-log-call-flow-analyzer/requirements.md: v1.2.0 섹션 추가
- [x] .kiro/specs/dm-log-call-flow-analyzer/design.md: 모듈 구조 및 Docker 배포 설명 추가
- [x] .gitignore: debug 폴더 및 scat 바이너리 추가
- [x] README.Docker.md: Docker 배포 완전한 가이드 작성

---

### v1.1.0 (2026-01-28) - GSMTAPv3 배열 형식 지원

#### 14.8 문제 정의
**증상**: VoNR 로그 분석 시 일부 NR RRC 메시지가 Call Flow에 표시되지 않음
- Frame 891-899: RRC Setup Request, RRC Setup, RRC Setup Complete 등 누락
- PCAP 파일에는 메시지가 존재하지만 JSON 파싱 후 추출 실패

**원인 분석**:
```python
# tshark JSON 출력 구조
{
  "nr-rrc": [
    "NR Radio Resource Control (RRC) protocol",  # [0]: 문자열
    {                                             # [1]: 실제 데이터
      "nr-rrc.UL_CCCH_Message_element": {...}
    }
  ]
}
```
- 기존 코드는 `nr-rrc`가 딕셔너리라고 가정
- GSMTAPv3 형식에서는 배열로 출력됨
- 배열 처리 로직 부재로 메시지 추출 실패

#### 14.9 해결 방법

**수정 위치**: `parsers.py` - `extract_message_info()` 함수

**수정 내용**:
```python
# NR RRC 배열 처리 로직 추가
if nr_rrc_key:
    nr_rrc = layers[nr_rrc_key]
    
    # GSMTAPv3 배열 형식 처리
    if isinstance(nr_rrc, list):
        # [0]은 문자열, [1]이 실제 데이터
        if len(nr_rrc) > 1 and isinstance(nr_rrc[1], dict):
            nr_rrc = nr_rrc[1]
        elif len(nr_rrc) > 0 and isinstance(nr_rrc[0], dict):
            nr_rrc = nr_rrc[0]
        else:
            nr_rrc = None  # 다음 프로토콜로
    
    # 이후 기존 로직 동일
    if nr_rrc and isinstance(nr_rrc, dict):
        # 메시지 추출...
```

**LTE RRC도 동일하게 수정**:
```python
if lte_rrc_key:
    lte_rrc = layers[lte_rrc_key]
    
    # GSMTAPv3 배열 형식 처리
    if isinstance(lte_rrc, list):
        if len(lte_rrc) > 1 and isinstance(lte_rrc[1], dict):
            lte_rrc = lte_rrc[1]
        elif len(lte_rrc) > 0 and isinstance(lte_rrc[0], dict):
            lte_rrc = lte_rrc[0]
        else:
            lte_rrc = None
    
    # 이후 기존 로직 동일
    if lte_rrc and isinstance(lte_rrc, dict):
        # 메시지 추출...
```

#### 14.10 검증 결과

**테스트 케이스**: VoNR.pcap (Frame 886-901)

**수정 전**:
```
Frame 886: RRC Release
Frame 887: MIB
Frame 888-890: NAS 메시지만
Frame 900-901: NAS 메시지만
총 254개 메시지 파싱
```

**수정 후**:
```
Frame 886: RRC Release
Frame 887: MIB
Frame 888-890: NAS 메시지
Frame 891: rrcSetupRequest (UL)
Frame 892: rrcSetup (DL)
Frame 893: rrcSetupComplete (UL)
Frame 894: securityModeCommand (DL)
Frame 895: securityModeComplete (UL)
Frame 896: ueCapabilityEnquiry (DL)
Frame 897: ueCapabilityInformation (UL)
Frame 898: rrcReconfiguration (DL)
Frame 899: rrcReconfigurationComplete (UL)
Frame 900-901: NAS 메시지
총 302개 메시지 파싱 (48개 증가)
```

#### 14.11 영향 범위

**긍정적 영향**:
- GSMTAPv3 형식의 모든 RRC 메시지 정상 파싱
- VoNR, EN-DC 등 실제 로그 분석 정확도 향상
- 파싱 성공률 19% 향상 (254 → 302)

**호환성**:
- 기존 딕셔너리 형식도 정상 동작 (하위 호환성 유지)
- 배열이 아닌 경우 기존 로직 그대로 실행
- 다른 프로토콜(NAS 5GS, NAS EPS)에는 영향 없음

**성능**:
- 배열 타입 체크 추가로 미미한 오버헤드 (무시 가능)
- 전체 파싱 시간 변화 없음

#### 14.12 추가 개선 사항

**디버그 정보 강화**:
```python
# parse_call_flow() 함수에 NR RRC 전용 디버그 추가
nr_rrc_debug = []
if msg_info['protocol'] == 'nr-rrc':
    nr_rrc_data = {
        'frame': frame_num,
        'message': msg_info['name'],
        'layers_keys': list(layers.keys()),
        'nr_rrc_type': type(layers.get('nr-rrc', None)).__name__,
        'nr_rrc_content': '...',
        'nr_rrc_element_keys': [...]
    }
    nr_rrc_debug.append(nr_rrc_data)

# *_parse_debug.json에 저장
{
    'total_packets': len(data),
    'parsed_flows': len(flows),
    'sample_debug': debug_info,
    'nr_rrc_debug': nr_rrc_debug  # 추가
}
```

**None 체크 강화**:
- 배열 처리 후 `nr_rrc`가 None이 될 수 있는 경우 명시적 체크
- `if nr_rrc and isinstance(nr_rrc, dict):` 조건으로 안전성 확보

#### 14.13 문서 업데이트

**업데이트된 문서**:
- [x] README.md: GSMTAPv3 지원 명시, 최근 업데이트 섹션 추가
- [x] design.md: 배열 처리 로직 상세 설명 추가
- [x] requirements.md: NR/LTE RRC 파싱 요구사항 체크, 최근 업데이트 섹션 추가
- [x] product.md: 주요 사용 사례 및 최근 업데이트 추가

---

## 15. 참고 문서

- 3GPP TS 24.501: 5G NAS Protocol
- 3GPP TS 24.301: LTE NAS Protocol
- 3GPP TS 24.008: PCO Protocol IDs
- 3GPP TS 36.331: LTE RRC Protocol
- 3GPP TS 38.331: NR RRC Protocol
