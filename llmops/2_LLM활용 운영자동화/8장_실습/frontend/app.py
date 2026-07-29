import requests
import streamlit as st

API_URL = "http://localhost:8001/api/chat"

st.set_page_config(
    page_title="AWS Operations Copilot",
    layout="wide",
)

st.title("AWS Operations Copilot")
st.caption(
    "Terraform으로 구축한 AWS 운영 환경을 "
    "LLM과 Boto3로 조회·분석합니다."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("예: 현재 서버 상태를 알려줘")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("AWS 운영 데이터를 조회하고 분석하는 중입니다."):
            try:
                response = requests.post(
                    API_URL,
                    json={"message": question},
                    timeout=120,
                )
                response.raise_for_status()
                result = response.json()

                st.markdown(result["answer"])

                if result.get("analysis"):
                    st.subheader("분석 결과")
                    st.json(result["analysis"])

                with st.expander("수집된 AWS 원본 데이터"):
                    st.json(result.get("raw_data"))

                assistant_message = result["answer"]

            except requests.RequestException as error:
                assistant_message = f"요청 실패:{error}"
                st.error(assistant_message)

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_message}
    )
