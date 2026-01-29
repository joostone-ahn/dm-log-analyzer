# DM Log Call Flow Analyzer

DM(Diagnostic Monitor) 로그 파일을 파싱하여 LTE/NR RRC 및 EPS/5GS NAS 메시지의 Call Flow를 시각화하는 웹 애플리케이션입니다.

---

## 주요 기능

- **다양한 DM 로그 포맷 지원**: HDF, SDM, QMDL, PCAP
- **프로토콜 지원**: LTE RRC, NR RRC, NAS EPS (4G), NAS 5GS (5G)
- **Call Flow 시각화**: UE, eNB, gNB, MME, AMF 간 메시지 흐름 표시
- **상세 정보**: 메시지 클릭 시 IE(Information Element) 트리 구조 표시

---

## 빠른 시작

### 1. Docker Desktop 설치

[Docker Desktop](https://www.docker.com/products/docker-desktop/) 다운로드 및 설치

### 2. 컨테이너 실행

#### macOS / Linux

```bash
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/data:/app/uploads \
  --name dm-log-analyzer \
  ghcr.io/joostone-ahn/dm-log-analyzer:latest
```

#### macOS (Apple Silicon)

```bash
docker run -d \
  --platform linux/amd64 \
  -p 8080:8080 \
  -v $(pwd)/data:/app/uploads \
  --name dm-log-analyzer \
  ghcr.io/joostone-ahn/dm-log-analyzer:latest
```

> **참고**: Apple Silicon Mac에서는 `--platform linux/amd64` 옵션 필요 (Rosetta 2 에뮬레이션)

#### Windows (PowerShell)

```powershell
docker run -d -p 8080:8080 -v ${PWD}/data:/app/uploads --name dm-log-analyzer ghcr.io/joostone-ahn/dm-log-analyzer:latest
```

### 3. 접속

브라우저에서 http://localhost:8080 접속

---

## 사용 방법

1. 웹 페이지에서 "파일 선택" 버튼 클릭
2. DM 로그 파일(HDF/SDM/QMDL) 또는 PCAP 파일 선택
3. 자동으로 변환 및 분석 시작
4. Call Flow 다이어그램 확인
5. 메시지 클릭하여 상세 정보 확인

### 지원 파일 형식

| 형식 | 확장자 | 설명 |
|------|--------|------|
| PCAP | .pcap | Wireshark 캡처 파일 |
| QMDL | .qmdl | Qualcomm DM 로그 |
| HDF | .hdf, .hdf5 | HDF5 포맷 DM 로그 |
| SDM | .sdm | Samsung DM 로그 |

---

## Docker 관리

### 컨테이너 제어

```bash
# 중지
docker stop dm-log-analyzer

# 시작
docker start dm-log-analyzer

# 재시작
docker restart dm-log-analyzer

# 삭제
docker rm -f dm-log-analyzer

# 로그 확인
docker logs -f dm-log-analyzer
```

### 이미지 업데이트

```bash
# 최신 이미지 다운로드
docker pull ghcr.io/joostone-ahn/dm-log-analyzer:latest

# 기존 컨테이너 삭제 후 재실행
docker rm -f dm-log-analyzer
docker run -d -p 8080:8080 -v $(pwd)/data:/app/uploads --name dm-log-analyzer ghcr.io/joostone-ahn/dm-log-analyzer:latest
```

---

## 기술 스택

- **백엔드**: Flask 3.0.0, Python 3.8+
- **프론트엔드**: HTML5, CSS3, JavaScript
- **외부 도구**: scat (자동 설치), tshark
- **컨테이너**: Docker, Ubuntu 22.04

---

## 최근 업데이트

### v1.2.3 (2026-01-29)
- **프로젝트 구조 개선**: Python 파일을 src/ 폴더로 정리
- **문서 업데이트**: 사용자 중심으로 README 재구성

### v1.2.2 (2026-01-29)
- **NR RRC 파싱 안정성 개선**: Docker 환경에서 NR RRC 메시지 파싱 문제 해결
- **빌드 최적화**: AMD64 단일 플랫폼 빌드로 전환

### v1.2.0 (2026-01-28)
- **모듈화 리팩토링**: 기능별 모듈 분리로 유지보수성 향상
- **Docker 배포 지원**: Windows, macOS, Linux 크로스 플랫폼 배포

### v1.1.0 (2026-01-28)
- **GSMTAPv3 배열 형식 지원**: VoNR 등 실제 로그 파싱 안정성 개선

---

## 라이선스

MIT License

### 외부 도구 라이선스

- **SCAT**: [fgsect/scat](https://github.com/fgsect/scat) - GPL v2.0
- **tshark**: [Wireshark](https://www.wireshark.org/) - GPL v2.0
