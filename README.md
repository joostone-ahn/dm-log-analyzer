# DM Log Call Flow Analyzer

DM(Diagnostic Monitor) 로그 파일을 파싱하여 LTE/NR RRC 및 EPS/5GS NAS 메시지의 Call Flow를 시각화하는 웹 애플리케이션입니다.

Docker를 사용하여 Windows, macOS, Linux 모든 환경에서 실행할 수 있습니다.

---

## 주요 기능

- **다양한 DM 로그 포맷 지원**: HDF, SDM, QMDL, PCAP
- **프로토콜 지원**: LTE RRC, NR RRC, NAS EPS (4G), NAS 5GS (5G)
- **Call Flow 시각화**: UE, eNB, gNB, MME, AMF 간 메시지 흐름 표시
- **상세 정보**: 메시지 클릭 시 IE(Information Element) 트리 구조 표시

---

## 사전 요구사항

### Docker 설치

- Windows: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
- macOS: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop/)
- Linux: [Docker Engine](https://docs.docker.com/engine/install/)

### scat 자동 설치

Docker 이미지 빌드 시 scat이 자동으로 설치됩니다 ([fgsect/scat](https://github.com/fgsect/scat)).

---

## 설치 및 실행

### macOS / Linux

```bash
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/pcaps:/app/pcaps \
  -v $(pwd)/jsons:/app/jsons \
  --name dm-log-analyzer \
  ghcr.io/joostone-ahn/dm-log-analyzer:latest
```

### Windows

```cmd
docker run -d -p 8080:8080 -v %cd%/uploads:/app/uploads -v %cd%/pcaps:/app/pcaps -v %cd%/jsons:/app/jsons --name dm-log-analyzer ghcr.io/joostone-ahn/dm-log-analyzer:latest
```

### 접속

브라우저에서 http://localhost:8080 접속

---

## Docker 관리 명령어

### 컨테이너 제어

```bash
# 시작
docker-compose up -d

# 중지
docker-compose stop

# 재시작
docker-compose restart

# 중지 및 삭제
docker-compose down

# 로그 확인
docker-compose logs -f
```

### 이미지 업데이트

```bash
# 최신 이미지 다운로드
docker-compose pull

# 컨테이너 재시작
docker-compose up -d
```

---

## 사용 방법

### 파일 업로드 및 분석

1. 웹 페이지에서 "파일 선택" 버튼 클릭
2. DM 로그 파일(HDF/SDM/QMDL) 또는 PCAP 파일 선택
3. 자동으로 변환 및 분석 시작
4. Call Flow 다이어그램 확인
5. 메시지 클릭하여 상세 정보 확인

### 지원 파일 형식

| 형식 | 확장자 | scat 필요 여부 |
|------|--------|----------------|
| PCAP | .pcap | 불필요 |
| QMDL | .qmdl | 필요 |
| HDF | .hdf, .hdf5 | 필요 |
| SDM | .sdm | 필요 |

---

## Docker 관리 명령어

## 프로젝트 구조

```
.
├── app.py                 # Flask 웹 서버 (라우트만)
├── converters.py          # 파일 변환 로직 (scat, tshark)
├── parsers.py             # 프로토콜 파싱 로직 (RRC/NAS)
├── message_types.py       # 3GPP 메시지 타입 매핑
├── utils.py               # 유틸리티 함수
├── templates/
│   └── index.html        # 프론트엔드 UI
├── uploads/              # 업로드된 로그 파일 저장
├── pcaps/                # 변환된 PCAP 파일 저장
├── jsons/                # 파싱된 JSON 파일 저장
├── Dockerfile            # Docker 이미지 정의
├── docker-compose.yml    # Docker Compose 설정
└── requirements.txt      # Python 의존성
```

---

## 기술 스택

- **백엔드**: Flask 3.0.0, Python 3.8+
- **프론트엔드**: HTML5, CSS3, JavaScript
- **외부 도구**: scat (자동 설치), tshark
- **컨테이너**: Docker, Ubuntu 22.04

---

## 최근 업데이트

### v1.2.1 (2026-01-28)
- **GitHub Container Registry 지원**: 자동 이미지 빌드 및 배포
- **README 간소화**: Docker 기준으로 설치 방법 통합, macOS/Linux와 Windows 명확히 구분
- **테스트 파일 제거**: 프로젝트 관련 파일만 Git에 포함

### v1.2.0 (2026-01-28)
- **모듈화 리팩토링**: app.py를 기능별 모듈로 분리 (1120줄 → 90줄)
- **Docker 배포 지원**: Windows, macOS, Linux 크로스 플랫폼 배포
- **scat 자동 설치**: Docker 이미지 빌드 시 자동 설치
- **코드 유지보수성 향상**: 기능별 모듈 분리로 가독성 개선

### v1.1.0 (2026-01-28)
- **GSMTAPv3 배열 형식 지원**: tshark JSON 출력에서 RRC 레이어가 배열로 나오는 경우 자동 처리
- **파싱 안정성 개선**: VoNR Service Request 시나리오 등 실제 로그에서 누락되던 RRC 메시지 파싱 문제 해결

---

## 라이선스

MIT License

### 외부 도구 라이선스

이 프로젝트는 다음 오픈소스 도구를 사용합니다:

- **SCAT (Signaling Collection and Analysis Tool)**
  - 저장소: [fgsect/scat](https://github.com/fgsect/scat)
  - 라이선스: GNU General Public License v2.0
  - 용도: DM 로그(HDF/SDM/QMDL) → PCAP 변환
  - Docker 이미지 빌드 시 자동으로 설치됩니다

- **tshark (Wireshark CLI)**
  - 저장소: [Wireshark](https://www.wireshark.org/)
  - 라이선스: GNU General Public License v2.0
  - 용도: PCAP → JSON 파싱
