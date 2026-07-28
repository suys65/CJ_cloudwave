import streamlit as st
import plotly.express as px

from bedrock_sql_generator import generate_sql_from_question
from athena_utils import run_athena_query

st.set_page_config(
    page_title="자연어 기반 S3 데이터 분석",
    layout="wide"
)

st.title("자연어 기반 S3 데이터 분석 및 시각화")
st.caption("Amazon Bedrock + Amazon Athena + Amazon S3 + Streamlit")

examples = [
    "전체 매출 합계를 알려줘",
    "월별 매출 추이를 보여줘",
    "카테고리별 매출 TOP 5를 보여줘",
    "지역별 주문 건수를 알려줘",
    "반품률이 가장 높은 카테고리를 보여줘",
    "2026년 1월 일자별 매출을 보여줘"
]

question = st.text_input(
    "분석 질문",
    value=examples[0],
    placeholder="예: 카테고리별 매출 TOP 5를 보여줘"
)

chart_type = st.selectbox(
    "차트 유형",
    ["자동", "막대그래프", "선그래프", "파이차트", "차트 없음"]
)

run_button = st.button("분석 실행")

if run_button:
    try:
        with st.spinner("Bedrock으로 SQL 생성 중..."):
            sql = generate_sql_from_question(question)

        st.subheader("생성된 SQL")
        st.code(sql, language="sql")

        with st.spinner("Athena 쿼리 실행 중..."):
            df = run_athena_query(sql)

        st.subheader("조회 결과")
        st.dataframe(df, use_container_width=True)

        if df.empty:
            st.warning("조회 결과가 없다.")
        elif chart_type != "차트 없음":
            st.subheader("시각화")

            columns = list(df.columns)

            if len(columns) >= 2:
                x_col = columns[0]
                y_col = columns[1]

                if chart_type == "선그래프":
                    fig = px.line(df, x=x_col, y=y_col, markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                elif chart_type == "파이차트":
                    fig = px.pie(df, names=x_col, values=y_col)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # '자동' 또는 '막대그래프'인 경우
                    fig = px.bar(df, x=x_col, y=y_col)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("차트를 만들려면 최소 2개 컬럼이 필요하다.")

    except Exception as e:
        st.error(str(e))
