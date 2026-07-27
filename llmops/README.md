# AWS 기초 및 운영자동화 — 실습 정리

교안(AWS 클라우드 기술 기초) 목차에 맞춰 실습 파일을 장별로 정리했다.

## 폴더 구조

```
llmops/
├─ 1장_boto3-API-입문/          boto3 기본 조회 스크립트
├─ 2장_운영자동화-스크립트기법/   함수화·예외처리 스크립트
├─ 3장_운영보안점검-자동화/       Terraform 인프라 + Bedrock 에이전트
├─ 4장_로그파일분석/             로컬 파일 로그 분석 (Python)
│   ├─ scripts/                본문 실습 스크립트 (19개)
│   ├─ 과제/                    실습 과제 (6.19)
│   └─ data/                   샘플 로그 데이터
├─ 5장_클라우드로그분석/          CloudWatch · S3 · Athena
│   ├─ scripts/                boto3 자동화 스크립트
│   ├─ config/                 SQL·정책·환경변수 정의
│   ├─ data/                   샘플 로그 데이터
│   └─ outputs/                쿼리 실행 결과 JSON
└─ 블로그정리/                   장별 기술 블로그 (md)
```

## 장별 내용

| 장 | 주제 | 핵심 파일 |
| --- | --- | --- |
| **1장** | boto3와 AWS API 자동화 입문 | `ec2_basic_list.py`, `describe_regions.py`, `session_test.py`, `check_bedrock.py` |
| **2장** | 운영 자동화 스크립트 작성 기법 | `boto3_summary.py`, `name_tag_test.py`, `describe_regions_safe.py` |
| **3장** | AWS 운영/보안 점검 자동화 | `main.tf` (VPC·EC2·SSM·IAM), `ec2_sre_agent.py` (Bedrock Converse 에이전트) |
| **4장** | 로그 파일 분석 개요 | `access_log_report.py` (종합), 정규식·Counter·JSON 파싱 실습 |
| **5장** | AWS 클라우드 로그 분석 실습 | `cloudwatch_logs_analyzer.py`, `athena_s3_log_analyzer.py` |

## 참고 사항

- **AWS 리소스**: 3·5장에서 생성한 실제 AWS 리소스(EC2·S3·CloudWatch·Athena·Glue)는 실습 종료 후 전부 삭제됨. 로컬 코드/설정만 보관.
- **3장 Terraform 상태**: `terraform.tfstate`는 `destroy` 완료 후의 빈 상태. 재실습 시 `terraform init` 후 사용.
- **5장 환경변수**: `config/ch7_env.sh`에 버킷명·리전 등 실습 변수 저장. 재실행 시 `source` 필요.
- **1·2장 분류**: 교안 원문 없이 스크립트 성격으로 추정 분류함 (기본 조회 → 1장, 함수·예외처리 → 2장).
- **블로그**: 파일명은 신규 장 번호(4·5장)로 맞췄으나, 본문에 옛 번호(6·7장) 표현이 남아 있음.
