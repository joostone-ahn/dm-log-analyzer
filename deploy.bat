@echo off
REM DM Log Call Flow Analyzer - Docker 배포 스크립트 (Windows)

echo ==========================================
echo DM Log Call Flow Analyzer - Docker 배포
echo ==========================================
echo.

REM Docker 설치 확인
echo 1. Docker 설치 확인...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker가 설치되지 않았습니다.
    echo Docker Desktop을 설치하세요: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)
docker --version
echo [OK] Docker 설치 확인 완료
echo.

REM Docker Compose 설치 확인
echo 2. Docker Compose 설치 확인...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose가 설치되지 않았습니다.
    pause
    exit /b 1
)
docker-compose --version
echo [OK] Docker Compose 설치 확인 완료
echo.

REM scat 바이너리 확인
echo 3. scat 바이너리 확인...
if not exist "scat" (
    if not exist "scat.exe" (
        echo [WARNING] scat 바이너리가 없습니다.
        echo scat 바이너리를 프로젝트 루트에 배치하세요.
        echo 계속하려면 아무 키나 누르세요 (scat 없이 빌드)...
        pause >nul
    )
)
echo [OK] scat 확인 완료
echo.

REM 기존 컨테이너 중지
echo 4. 기존 컨테이너 중지...
docker-compose down 2>nul
echo [OK] 기존 컨테이너 중지 완료
echo.

REM Docker 이미지 빌드
echo 5. Docker 이미지 빌드 중...
echo    (최초 실행 시 5-10분 소요될 수 있습니다)
docker-compose build --no-cache
if errorlevel 1 (
    echo [ERROR] Docker 이미지 빌드 실패
    pause
    exit /b 1
)
echo [OK] Docker 이미지 빌드 완료
echo.

REM 컨테이너 시작
echo 6. 컨테이너 시작...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 컨테이너 시작 실패
    pause
    exit /b 1
)
echo [OK] 컨테이너 시작 완료
echo.

REM 컨테이너 상태 확인
echo 7. 컨테이너 상태 확인...
timeout /t 3 /nobreak >nul
docker-compose ps
echo.

REM 헬스체크 대기
echo 8. 서비스 헬스체크 중...
for /L %%i in (1,1,10) do (
    curl -s http://localhost:8080 >nul 2>&1
    if not errorlevel 1 (
        echo [OK] 서비스가 정상적으로 실행 중입니다!
        goto :health_ok
    )
    echo    대기 중... (%%i/10)
    timeout /t 2 /nobreak >nul
)
:health_ok

REM 완료 메시지
echo.
echo ==========================================
echo 배포 완료!
echo ==========================================
echo.
echo 웹 브라우저에서 다음 주소로 접속하세요:
echo http://localhost:8080
echo.
echo 유용한 명령어:
echo   - 로그 확인:        docker-compose logs -f
echo   - 컨테이너 중지:    docker-compose stop
echo   - 컨테이너 재시작:  docker-compose restart
echo   - 컨테이너 삭제:    docker-compose down
echo.
pause
