import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="MBTI 상위 10개국 막대그래프", layout="wide")

# 데이터 로드
df = pd.read_csv("countriesMBTI_16types.csv")

# 컬럼 분리
mbti_cols = [c for c in df.columns if c != "Country"]

st.title("MBTI별 상위 10개 국가 시각화 (Altair)")
st.caption("같은 폴더의 countriesMBTI_16types.csv 파일을 사용함")

# MBTI 유형 선택
selected = st.selectbox("MBTI 유형을 선택하세요:", mbti_cols, index=mbti_cols.index("INFP") if "INFP" in mbti_cols else 0)

# 상위 10개 국가 추출
top10 = (
    df[["Country", selected]]
    .nlargest(10, selected)
    .sort_values(selected, ascending=True)  # 그래프에서 위가 큰 값이 되도록 오름차순 정렬
)

# Altair 차트 생성 (비율을 퍼센트 축으로 표시)
chart = (
    alt.Chart(top10, title=f"{selected} 비율 상위 10개 국가")
    .mark_bar()
    .encode(
        y=alt.Y("Country:N", sort=None, title="국가"),
        x=alt.X(f"{selected}:Q", title="비율", axis=alt.Axis(format=".1%")),
        tooltip=[
            alt.Tooltip("Country:N", title="국가"),
            alt.Tooltip(f"{selected}:Q", title="비율", format=".2%")
        ]
    )
    .properties(height=420)
)

st.altair_chart(chart, use_container_width=True)

# 원본 데이터 미리보기(선택)
with st.expander("원본 데이터 상위 5행 보기"):
    st.dataframe(df.head())
