import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MBTI 분포 대시보드", layout="centered", page_icon="🌍")

st.title("🌍 나라별 MBTI 분포 대시보드")
st.caption("같은 폴더의 `countriesMBTI_16types.csv`를 사용함")

# 데이터 로드
@st.cache_data
def load_data(path: str):
    df = pd.read_csv(path)
    # 기본 유효성 검사
    assert "Country" in df.columns, "'Country' 컬럼이 필요함"
    mbti_cols = [c for c in df.columns if c != "Country"]
    return df, mbti_cols

try:
    df, mbti_cols = load_data("countriesMBTI_16types.csv")
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류 발생: {e}")
    st.stop()

# 국가 선택
default_country = "Korea, Republic of" if "Korea, Republic of" in df["Country"].values else df["Country"].iloc[0]
country = st.selectbox("국가를 선택하세요 🇺🇳", sorted(df["Country"].tolist()), index=sorted(df["Country"].tolist()).index(default_country))

# 선택 국가 데이터 변환 (long format)
row = df[df["Country"] == country].iloc[0]
long_df = (
    pd.DataFrame({"Type": mbti_cols, "Ratio": [row[c] for c in mbti_cols]})
    .sort_values("Ratio", ascending=True)
)

# 색상 팔레트 (부드러운 파스텔 톤)
palette = [
    "#6BAED6","#9ECAE1","#C6DBEF","#FDD0A2",
    "#FDAE6B","#FEE6CE","#A1D99B","#74C476",
    "#31A354","#C7E9C0","#BC80BD","#CCEBC5",
    "#80B1D3","#FDB462","#B3DE69","#FCCDE5"
]

# MBTI 순서를 보기 좋게 고정(알파벳)
long_df["Type"] = pd.Categorical(long_df["Type"], categories=sorted(mbti_cols), ordered=True)

st.subheader(f"📊 {country}의 MBTI 분포")
st.caption("비율은 0~1 값을 퍼센트로 표시함")

fig = px.bar(
    long_df,
    x="Ratio",
    y="Type",
    orientation="h",
    text="Ratio",
    color="Type",
    color_discrete_sequence=palette
)

fig.update_traces(
    texttemplate="%{text:.1%}",
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    xaxis=dict(title="비율(%)", tickformat=".0%"),
    yaxis=dict(title="MBTI 유형"),
    bargap=0.2,
    margin=dict(l=80, r=40, t=40, b=40),
    showlegend=False,
    plot_bgcolor="white"
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("🔎 원자료 확인"):
    st.dataframe(df[df["Country"] == country].reset_index(drop=True))

st.markdown(
    "✅ 팁: 막대의 레이블은 퍼센트로 표시되며, 값이 작은 유형도 잘 보이도록 가로 막대를 사용함 😊"
)
