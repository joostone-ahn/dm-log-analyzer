# 제품 개요

DM Log Call Flow Analyzer는 DM(Diagnostic Monitor) 로그를 파싱하여 Call Flow를 시각화하는 네트워크 프로토콜 분석 도구입니다.

## 핵심 기능

- **DM 로그 파싱 및 변환**
  - 다양한 DM 로그 포맷 지원 (HDF, SDM, QMDL, PCAP)
  - scat을 통한 DM 로그 → PCAP 변환
  - tshark를 통한 PCAP → JSON 파싱

- **프로토콜 지원**
  - LTE RRC, NR RRC (GSMTAPv3 배열 형식 지원), NAS EPS (4G), NAS 5GS (5G)
  - 중첩된 메시지 추출 (RRC 내 NAS, LTE RRC 내 NR RRC)

- **Call Flow 시각화**
  - 5개 노드(UE, eNB, gNB, MME, AMF) 간의 메시지 흐름 표현
  - DL/UL 방향 자동 판단 및 색상 구분
  - 메시지 클릭 시 Information Element(IE) 트리 구조로 상세 정보 표시

## 사용자 워크플로우

1. 웹 인터페이스에서 DM 로그 파일(HDF/SDM/QMDL) 또는 PCAP 파일 업로드
2. 백엔드에서 자동 변환 (DM 로그 → PCAP → JSON)
3. Call Flow 다이어그램 시각화
4. 메시지 클릭하여 상세 IE 정보 확인

## 주요 사용 사례

- 5G/LTE 네트워크 엔지니어의 DM 로그 분석
- Call Flow 디버깅 및 문제 해결
- RRC/NAS 메시지 시퀀스 검증
- 다양한 DM 로그 포맷의 통합 분석
- 프로토콜 레이어 간 메시지 흐름 추적
- VoNR 등 실제 로그의 GSMTAPv3 형식 메시지 분석

## 최근 업데이트

### v1.2.0 (2026-01-28)
- **모듈화 리팩토링**: app.py를 기능별 모듈로 분리
  - `converters.py`: 파일 변환 로직
  - `parsers.py`: 프로토콜 파싱 로직
  - `message_types.py`: 3GPP 메시지 타입 매핑
  - `utils.py`: 유틸리티 함수
  - `app.py`: Flask 라우트만 (1120줄 → 90줄)
- **Docker 배포 지원**: Windows, macOS, Linux 크로스 플랫폼 배포
  - Dockerfile, docker-compose.yml 구현
  - 자동 배포 스크립트 (deploy.sh, deploy.bat)
  - README.Docker.md 완전한 배포 가이드
  - Linux 컨테이너 환경으로 Windows에서도 Linux용 scat 작동
  - scat 없이도 PCAP 파일 직접 업로드 가능
- **코드 유지보수성 향상**: 기능별 모듈 분리로 가독성 개선, debug 폴더 정리

### v1.1.0 (2026-01-28)
- **GSMTAPv3 배열 형식 지원**: tshark JSON 출력에서 RRC 레이어가 배열로 나오는 경우 자동 처리
- **파싱 안정성 개선**: VoNR Service Request 시나리오 등 실제 로그에서 누락되던 RRC 메시지 파싱 문제 해결
- **디버그 정보 강화**: NR RRC 전용 디버그 섹션 추가
