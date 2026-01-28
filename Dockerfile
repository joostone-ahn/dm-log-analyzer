# DM Log Call Flow Analyzer - Docker Image
FROM ubuntu:22.04

# 환경 변수 설정
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tshark \
    git \
    libusb-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

# scat 설치 (GitHub에서 직접 설치)
# SCAT: Signaling Collection and Analysis Tool
# https://github.com/fgsect/scat
RUN pip3 install --no-cache-dir git+https://github.com/fgsect/scat.git

# Python 의존성 복사 및 설치
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY app.py .
COPY converters.py .
COPY parsers.py .
COPY message_types.py .
COPY utils.py .
COPY templates/ templates/
COPY wireshark/ wireshark/

# 데이터 디렉토리 생성
RUN mkdir -p uploads pcaps jsons

# 포트 노출
EXPOSE 8080

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080')" || exit 1

# Flask 애플리케이션 실행
CMD ["python3", "app.py"]
