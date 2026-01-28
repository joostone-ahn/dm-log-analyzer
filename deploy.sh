#!/bin/bash

# DM Log Call Flow Analyzer - Docker 배포 스크립트

set -e

echo "=========================================="
echo "DM Log Call Flow Analyzer - Docker 배포"
echo "=========================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Docker 설치 확인
echo "1. Docker 설치 확인..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Docker가 설치되지 않았습니다."
    echo "Docker Desktop을 설치하세요: https://www.docker.com/products/docker-desktop/"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Docker 버전: $(docker --version)"

# Docker Compose 설치 확인
echo ""
echo "2. Docker Compose 설치 확인..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Docker Compose가 설치되지 않았습니다."
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Docker Compose 버전: $(docker-compose --version)"

# scat 바이너리 확인
echo ""
echo "3. scat 바이너리 확인..."
if [ ! -f "scat" ]; then
    echo -e "${YELLOW}[WARNING]${NC} scat 바이너리가 없습니다."
    echo ""
    echo "중요: Docker 컨테이너는 Linux 환경입니다."
    echo "      Linux용 scat 바이너리를 사용해야 합니다."
    echo ""
    echo "scat 없이도 사용 가능:"
    echo "  - PCAP 파일을 직접 업로드하면 분석 가능합니다"
    echo "  - scat은 DM 로그(HDF/QMDL/SDM) 변환에만 필요합니다"
    echo ""
    echo "계속하려면 Enter를 누르세요 (scat 없이 빌드)..."
    read
else
    echo -e "${GREEN}[OK]${NC} scat 바이너리 발견: $(ls -lh scat | awk '{print $5}')"
    echo "      (Linux용 바이너리인지 확인하세요)"
fi

# 기존 컨테이너 중지
echo ""
echo "4. 기존 컨테이너 중지..."
docker-compose down 2>/dev/null || true
echo -e "${GREEN}[OK]${NC} 기존 컨테이너 중지 완료"

# Docker 이미지 빌드
echo ""
echo "5. Docker 이미지 빌드 중..."
echo "   (최초 실행 시 5-10분 소요될 수 있습니다)"
docker-compose build --no-cache

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} Docker 이미지 빌드 완료"
else
    echo -e "${RED}[ERROR]${NC} Docker 이미지 빌드 실패"
    exit 1
fi

# 컨테이너 시작
echo ""
echo "6. 컨테이너 시작..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK]${NC} 컨테이너 시작 완료"
else
    echo -e "${RED}[ERROR]${NC} 컨테이너 시작 실패"
    exit 1
fi

# 컨테이너 상태 확인
echo ""
echo "7. 컨테이너 상태 확인..."
sleep 3
docker-compose ps

# 헬스체크 대기
echo ""
echo "8. 서비스 헬스체크 중..."
for i in {1..10}; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo -e "${GREEN}[OK]${NC} 서비스가 정상적으로 실행 중입니다!"
        break
    fi
    echo "   대기 중... ($i/10)"
    sleep 2
done

# 완료 메시지
echo ""
echo "=========================================="
echo -e "${GREEN}배포 완료!${NC}"
echo "=========================================="
echo ""
echo "웹 브라우저에서 다음 주소로 접속하세요:"
echo -e "${GREEN}http://localhost:8080${NC}"
echo ""
echo "유용한 명령어:"
echo "  - 로그 확인:        docker-compose logs -f"
echo "  - 컨테이너 중지:    docker-compose stop"
echo "  - 컨테이너 재시작:  docker-compose restart"
echo "  - 컨테이너 삭제:    docker-compose down"
echo ""
