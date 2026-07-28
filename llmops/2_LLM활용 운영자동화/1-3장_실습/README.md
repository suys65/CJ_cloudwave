# 실습1 — LLM 기반 AWS 운영 요청 분석과 명령 생성

Amazon Bedrock Converse API + Boto3 로 자연어 AWS 운영 요청을 분석·분류하고
읽기 전용 CLI 명령 초안을 생성하는 실습.

## 실행 방법

```powershell
# 가상환경 활성화
.venv\Scripts\Activate.ps1

# 각 실습 실행
python 01_check_aws_session.py
python 02_basic_bedrock_call.py
python 03_analyze_operation_request.py
python 04_classify_operation_risk.py
python 05_generate_read_only_command.py
python 06_ec2_status_summary.py
```

> 한글이 깨지면 `$env:PYTHONUTF8=1` 을 먼저 실행한다.

## 파일 구성

| 파일 | 내용 |
| --- | --- |
| `config.py` | `.env` 로딩 및 설정값 |
| `aws_clients.py` | Boto3 Session / STS · EC2 · Bedrock 클라이언트 |
| `bedrock_utils.py` | `converse()`, `extract_text()`, `strip_json_fence()` |
| `01_check_aws_session.py` | STS 인증 주체 확인 |
| `02_basic_bedrock_call.py` | Converse 기본 호출 + usage/stopReason |
| `03_analyze_operation_request.py` | 운영 요청 의도·작업유형 분류 |
| `04_classify_operation_risk.py` | 작업 위험도 분류 |
| `05_generate_read_only_command.py` | 읽기 전용 CLI 명령 생성 |
| `06_ec2_status_summary.py` | EC2 조회 결과 LLM 요약 |

## 이 환경에 맞춘 조정 사항 (교재와의 차이)

1. **AWS Profile**: 교재는 `student` 를 가정하지만 이 PC에는 `student` 프로파일이
   없고 유효한 자격증명은 `admin`(SSO) 뿐이라 `.env` 의 `AWS_PROFILE=admin` 으로 설정했다.
   (`default`, `bedrock-training`, `lab`, `kyt-profile` 은 토큰 만료 상태)

2. **모델 ID**: `apac.anthropic.claude-sonnet-4-20250514-v1:0` 는 Legacy 로 표시되어
   호출이 거부되므로 활성 모델
   `global.anthropic.claude-sonnet-4-5-20250929-v1:0` 로 설정했다.

3. **`strip_json_fence()` 추가**: 모델이 JSON 을 ```json ... ``` 코드블록으로 감싸
   `json.loads()` 가 실패하는 문제(교재 16.4 절)를 해결하기 위해 파싱 전에
   코드블록 펜스를 제거하는 헬퍼를 `bedrock_utils.py` 에 추가하고
   실습 03/04/05 에서 사용한다. (엄격한 검증은 6장 Pydantic 에서 다룸)

4. **실습 05 시스템 프롬프트**: 허용 `operation_type` 값 목록을 명시해 조회 작업이
   반드시 `read_only` 로 분류되도록 보강했다.

5. **EC2 인스턴스 없음**: 계정에 EC2 인스턴스가 없어 실습 06 은 "인스턴스 없음"
   경로를 정상적으로 시연한다.
