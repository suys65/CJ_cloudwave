import os
import time
import boto3

# 1. AWS 프로필 및 리전 설정
os.environ.setdefault("AWS_PROFILE", "admin")  # 터미널에 설정된 값이 없을 때만 작동
AWS_REGION = "ap-northeast-2"

# Boto3 클라이언트 생성
bedrock_client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
ssm_client = boto3.client("ssm", region_name=AWS_REGION)

# =====================================================================
# 2. 실제 실행될 파이썬 함수 (Python Functions)
# =====================================================================

def execute_ssm_shell(instance_id: str, command: str) -> str:
    """EC2 인스턴스로 SSM Run Command 전송"""
    try:
        response = ssm_client.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={'commands': [command]}
        )
        command_id = response['Command']['CommandId']
        time.sleep(3)  # SSM 처리 대기

        result = ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id
        )
        return result.get('StandardOutputContent', '') or result.get('StandardErrorContent', '')
    except Exception as e:
        return f"[SSM Execution Error]: {str(e)}"

def check_server_status(instance_id: str) -> str:
    """EC2 메모리, 디스크 및 가동 시간 점검"""
    cmd = "free -h && df -h / && uptime"
    return execute_ssm_shell(instance_id, cmd)

def check_listening_ports(instance_id: str, protocol: str = "all") -> str:
    """EC2 리스닝 포트 및 프로세스 점검"""
    if protocol.lower() == "tcp":
        cmd = "sudo ss -tlnp 2>/dev/null || sudo netstat -tlnp"
    elif protocol.lower() == "udp":
        cmd = "sudo ss -ulnp 2>/dev/null || sudo netstat -ulnp"
    else:
        cmd = "sudo ss -tulnp 2>/dev/null || sudo netstat -tulnp"

    output = execute_ssm_shell(instance_id, cmd)
    return output if output else "리스닝 중인 포트 정보를 불러올 수 없습니다."

# =====================================================================
# 3. Bedrock Converse API용 스키마 정의 (Tool Config)
# =====================================================================

tools_config = {
    "tools": [
        {
            "toolSpec": {
                "name": "check_server_status",
                "description": "EC2 인스턴스의 CPU, 메모리, 디스크 사용량 및 Uptime 상태를 점검합니다.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "instance_id": {
                                "type": "string",
                                "description": "조회할 EC2 인스턴스 ID (예: i-0123456789abcdef0)"
                            }
                        },
                        "required": ["instance_id"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "check_listening_ports",
                "description": "EC2 인스턴스에서 현재 리스닝 중인 네트워크 포트와 프로세스 목록을 확인합니다.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "instance_id": {
                                "type": "string",
                                "description": "조회할 EC2 인스턴스 ID"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "조회할 프로토콜 ('tcp', 'udp', 'all')",
                                "enum": ["tcp", "udp", "all"]
                            }
                        },
                        "required": ["instance_id"]
                    }
                }
            }
        }
    ]
}

# 함수 이름 매핑 루틴
AVAILABLE_FUNCTIONS = {
    "check_server_status": check_server_status,
    "check_listening_ports": check_listening_ports
}

# =====================================================================
# 4. Agent Execution Loop (ReAct 대화 루프)
# =====================================================================

def run_ops_agent(user_prompt: str, model_id: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"):
    # 대화 히스토리 관리
    messages = [
        {
            "role": "user",
            "content": [{"text": user_prompt}]
        }
    ]

    system_prompts = [
        {"text": "당신은 AWS EC2 인프라를 관리하는 SRE 운영 자동화 에이전트입니다. "
                 "제공된 툴을 사용하여 서버 정보를 조회하고 친절하게 답변하세요."}
    ]

    while True:
        # 1. Bedrock Converse API 호출
        response = bedrock_client.converse(
            modelId=model_id,
            messages=messages,
            system=system_prompts,
            toolConfig=tools_config
        )

        output_message = response['output']['message']
        messages.append(output_message)  # LLM 응답 대화 기록에 추가

        stop_reason = response['stopReason']

        # 2. LLM이 툴을 호출하기로 결정한 경우 (tool_use)
        if stop_reason == 'tool_use':
            tool_requests = [content for content in output_message['content'] if 'toolUse' in content]

            tool_results = []
            for tool_req in tool_requests:
                tool_use = tool_req['toolUse']
                tool_use_id = tool_use['toolUseId']
                function_name = tool_use['name']
                function_args = tool_use['input']

                print(f"\n[Tool Call 감지] 함수: {function_name}, 인자: {function_args}")

                # 매핑된 파이썬 함수 실행
                if function_name in AVAILABLE_FUNCTIONS:
                    target_function = AVAILABLE_FUNCTIONS[function_name]
                    result_content = target_function(**function_args)
                else:
                    result_content = f"Error: {function_name} 함수를 찾을 수 없습니다."

                # 툴 실행 결과를 Bedrock Converse 메시지 규격으로 구성
                tool_results.append({
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"text": str(result_content)}]
                    }
                })

            # 3. 툴 실행 결과를 LLM에게 전달할 대화 내역에 추가
            messages.append({
                "role": "user",
                "content": tool_results
            })

            # 루프를 계속 돌아 LLM이 툴 결과를 해석하여 최종 답변을 내놓도록 함
            continue

        # 4. LLM이 최종 답변을 완료한 경우 (end_turn)
        elif stop_reason == 'end_turn':
            final_text = ""
            for content in output_message['content']:
                if 'text' in content:
                    final_text += content['text']
            return final_text

        else:
            print(f"Unhandled stop reason: {stop_reason}")
            break

# =====================================================================
# 5. 실행 테스트
# =====================================================================
if __name__ == "__main__":
    target_ec2_id = "i-086b0878e33263502"  # 실제 EC2 인스턴스 ID로 변경

    prompt = f"EC2 인스턴스({target_ec2_id})의 서버 상태와 현재 리스닝 중인 TCP 포트 목록을 점검해줘."

    print(f"사용자 요청: {prompt}\n" + "="*50)
    final_response = run_ops_agent(prompt)

    print("\n[최종 LLM 응답]:")
    print(final_response)
