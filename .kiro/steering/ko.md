---
inclusion: always
---

# 한국어 응답 규칙

## 기본 응답 언어

모든 응답은 한국어로 작성합니다. 사용자가 영어로 질문하더라도 한국어로 답변하며, 명시적으로 다른 언어를 요청할 때만 해당 언어를 사용합니다.

## 응답 스타일

- 존댓말 사용 (~습니다, ~해주세요)
- 친근하고 전문적인 톤 유지
- 기술적 설명은 명확하고 이해하기 쉽게 작성
- 불필요한 반복 피하기

## 기술 용어 표기

- 주요 기술 용어는 한국어와 영어 병행 표기 (예: 함수(function), 변수(variable), 프로토콜(protocol))
- 널리 알려진 약어는 그대로 사용 (예: RRC, NAS, API, JSON, PCAP)
- 3GPP 표준 용어는 영문 유지 (예: PDU Session, QoS Flow, SystemInformation)

## 코드 작성 규칙

### 명명 규칙
- 함수명과 변수명: snake_case (영어)
- 클래스명: PascalCase (영어)
- 상수: UPPER_SNAKE_CASE (영어)
- 파일명: snake_case (영어)

### 주석 작성
- 모든 코드 주석은 한국어로 작성
- 함수 docstring은 한국어로 작성하되, 파라미터명은 영어 유지
- 복잡한 로직에는 설명 주석 추가

예시:
```python
def parse_call_flow(json_data):
    """
    JSON 데이터를 파싱하여 Call Flow 데이터를 생성합니다.
    
    Args:
        json_data: tshark로 변환된 JSON 데이터
        
    Returns:
        list: Call Flow 메시지 리스트
    """
    # RRC 메시지 추출
    messages = []
    # ...
```

## 문서 작성

- README, 설계 문서, 요구사항 문서는 한국어로 작성
- 코드 예시와 명령어는 영어 유지
- 파일 경로와 기술 스택 이름은 원문 유지

## 에러 처리 및 로깅

- 에러 메시지는 한국어로 작성
- 디버그 로그는 한국어로 작성
- 사용자 대면 메시지는 친절하고 명확한 한국어 사용

예시:
```python
try:
    result = convert_to_pcap(file_path)
except Exception as e:
    return {"error": f"PCAP 변환 중 오류가 발생했습니다: {str(e)}"}
```

## 설명 및 답변 구조

1. 간단한 요약으로 시작
2. 필요시 단계별 설명 제공
3. 코드 예시 포함
4. 관련 파일이나 함수 참조
5. 추가 고려사항이나 주의사항 언급

## 프로젝트 특화 용어

- DM 로그: Diagnostic Monitor 로그
- Call Flow: 호 흐름도 (시각화 시에는 Call Flow 사용)
- IE: Information Element (정보 요소)
- UL/DL: Uplink/Downlink (상향/하향)
- 노드: UE(단말), eNB(기지국), gNB(5G 기지국), MME(이동성 관리), AMF(접속 관리)