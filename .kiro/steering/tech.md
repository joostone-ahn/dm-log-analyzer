# 기술 스택

## 백엔드

- **프레임워크**: Flask 3.0.0
- **언어**: Python 3.8+
- **주요 라이브러리**: Werkzeug 3.0.1

## 프론트엔드

- **기술**: Vanilla JavaScript (프레임워크 없음)
- **스타일**: 인라인 CSS (별도 CSS 파일 없음)
- **템플릿**: Jinja2 (Flask 기본 템플릿 엔진)

## 외부 도구 의존성

- **scat**: HDF/SDM/QMDL → PCAP 변환 (필수)
- **tshark**: PCAP → JSON 파싱 (Wireshark CLI, 필수)

## 공통 명령어

### 개발 환경 설정

```bash
# 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 서버 실행

```bash
# 개발 서버 (디버그 모드)
python app.py

# 서버 주소: http://localhost:8080
```

### 외부 도구 설치 확인

```bash
# scat 설치 확인
scat --version

# tshark 설치 확인
tshark --version

# macOS에서 tshark 설치
brew install wireshark
```

### 분석 스크립트 실행

```bash
# RTCP 품질 분석
python rtcp_analyze.py pcaps/VoNR.pcap

# SA 세션 분석
python sa_session_analyze.py pcaps/SA_regi.pcap
```

## 파일 크기 제한

- 최대 업로드 크기: 2GB (app.py에서 설정)
- 큰 파일 처리 시 타임아웃 없음 (subprocess timeout=None)
