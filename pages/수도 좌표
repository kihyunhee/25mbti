import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="MBTI 분포 대시보드", layout="wide", page_icon="🧭")

# =========================
# 데이터 로드
# =========================
@st.cache_data
def load_mbti(path: str):
    df = pd.read_csv(path)
    assert "Country" in df.columns, "'Country' 컬럼이 필요함"
    mbti_cols = [c for c in df.columns if c != "Country"]
    return df, mbti_cols

@st.cache_data
def try_load_capitals(path: str):
    try:
        caps = pd.read_csv(path)
        required = {"Country", "Capital", "Latitude", "Longitude"}
        if not required.issubset(set(caps.columns)):
            raise ValueError("capitals.csv 컬럼은 Country, Capital, Latitude, Longitude 이어야 함")
        return caps
    except Exception:
        return None

df, mbti_cols = load_mbti("countriesMBTI_16types.csv")
capitals = try_load_capitals("capitals.csv")  # 선택 파일

# =========================
# UI
# =========================
st.title("🌍 나라별 MBTI 대시보드")
st.caption("같은 폴더의 `countriesMBTI_16types.csv`를 사용함. 선택적으로 `capitals.csv`(Country, Capital, Latitude, Longitude)를 두면 수도 마커 지도 표시함.")

with st.sidebar:
    st.header("⚙️ 설정")
    # 국가 선택
    countries_sorted = sorted(df["Country"].unique().tolist())
    default_country = "Korea, Republic of" if "Korea, Republic of" in countries_sorted else countries_sorted[0]
    selected_countries = st.multiselect("국가 선택 🇺🇳", countries_sorted, default=[default_country])

    # 차트 유형
    chart_type = st.radio("차트 유형 선택", ["막대(비교)", "파이", "레이더"], index=0, help="여러 국가를 선택하면 막대/레이더에서 비교 가능함")

    # 상위 N개 유형
    top_n = st.slider("상위 N개 MBTI 유형", min_value=2, max_value=len(mbti_cols), value=10, step=1)

    # 지도용 MBTI 유형
    map_mbti = st.selectbox("지도 색칠 기준 MBTI 유형", mbti_cols, index=mbti_cols.index("INFP") if "INFP" in mbti_cols else 0)

    # 보기 옵션
    show_table = st.checkbox("원자료 표 보기", value=False)

# 방어 로직
if not selected_countries:
    st.warning("최소 1개 국가는 선택해야 함.")
    st.stop()

# =========================
# 데이터 준비
# =========================
def long_df_for_country(country: str) -> pd.DataFrame:
    row = df[df["Country"] == country]
    if row.empty:
        return pd.DataFrame(columns=["Type", "Ratio", "Country"])
    row = row.iloc[0]
    return pd.DataFrame({"Type": mbti_cols, "Ratio": [row[c] for c in mbti_cols], "Country": country})

# 선택 국가 데이터 결합(long)
long_all = pd.concat([long_df_for_country(c) for c in selected_countries], ignore_index=True)

# 상위 N 선정을 위해: 선택국 평균으로 공통 Top N 유형 선정
avg_by_type = long_all.groupby("Type", as_index=False)["Ratio"].mean().rename(columns={"Ratio": "AvgRatio"})
top_types = avg_by_type.sort_values("AvgRatio", ascending=False).head(top_n)["Type"].tolist()

# 시각화용 데이터 필터
long_top = long_all[long_all["Type"].isin(top_types)].copy()
# 보기 좋게 정렬(평균 기준)
type_order = avg_by_type.sort_values("AvgRatio", ascending=True)["Type"].tolist()
long_top["Type"] = pd.Categorical(long_top["Type"], categories=type_order, ordered=True)

# =========================
# 메인 차트
# =========================
st.subheader("📊 MBTI 분포 시각화")

if chart_type == "막대(비교)":
    # 그룹 막대 (나라별 비교)
    fig = px.bar(
        long_top,
        x="Ratio",
        y="Type",
        color="Country",
        orientation="h",
        barmode="group",
        text="Ratio",
        labels={"Ratio": "비율", "Type": "MBTI 유형", "Country": "국가"},
    )
    fig.update_traces(texttemplate="%{text:.1%}", textposition="outside", cliponaxis=False)
    fig.update_layout(
        xaxis=dict(title="비율(%)", tickformat=".0%"),
        yaxis=dict(title="MBTI 유형"),
        bargap=0.2,
        margin=dict(l=80, r=40, t=60, b=40),
        legend_title_text="국가",
        title=f"✨ 선택국 공통 상위 {top_n} 유형 비교"
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "파이":
    # 다중 국가 선택 시: 평균 파이 / 단일 국가는 해당 국가 파이
    if len(selected_countries) == 1:
        country = selected_countries[0]
        df_one = long_df_for_country(country).sort_values("Ratio", ascending=False)
        fig = px.pie(df_one.head(top_n), values="Ratio", names="Type",
                     title=f"🥧 {country} 상위 {top_n} MBTI 분포",
                     hole=0.35)
    else:
        # 평균 파이
        fig = px.pie(avg_by_type.sort_values("AvgRatio", ascending=False).head(top_n),
                     values="AvgRatio", names="Type",
                     title=f"🥧 선택국 평균 기준 상위 {top_n} MBTI 분포",
                     hole=0.35)
    fig.update_traces(textposition="inside", texttemplate="%{label}<br>%{percent:.1%}")
    st.plotly_chart(fig, use_container_width=True)

elif chart_type == "레이더":
    # Scatterpolar로 나라별 레이더 중첩
    # 축 순서는 평균 낮은→높은 순으로(시계방향 가독성)
    type_order_radar = avg_by_type.sort_values("AvgRatio", ascending=False)["Type"].tolist()[:top_n]
    fig = go.Figure()
    for c in selected_countries:
        row = long_df_for_country(c)
        row = row[row["Type"].isin(type_order_radar)]
        row = row.set_index("Type").reindex(type_order_radar).reset_index()
        fig.add_trace(go.Scatterpolar(
            r=row["Ratio"],
            theta=row["Type"],
            fill="toself",
            name=c,
            hovertemplate="%{theta}: %{r:.1%}<extra>%s</extra>" % c
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, tickformat=".0%")),
        showlegend=True,
        title=f"🧭 레이더 차트(상위 {top_n} 유형)"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# 지도(국가/수도)
# =========================
st.subheader("🗺️ 지도에서 보기")

map_base = df[["Country", map_mbti]].copy().rename(columns={map_mbti: "Ratio"})

if capitals is not None:
    st.caption("📌 `capitals.csv`가 감지되어 수도 마커 지도 표시함.")
    # 수도 좌표 병합
    geo = capitals.merge(map_base, on="Country", how="right")
    # 마커 지도(Scattergeo)
    fig_map = px.scatter_geo(
        geo,
        lat="Latitude", lon="Longitude",
        hover_name="Country",
        hover_data={"Capital": True, "Ratio": ":.2%"},
        size="Ratio",
        size_max=22,
        color="Ratio",
        color_continuous_scale="Blues",
        projection="natural earth",
        title=f"📍 수도 기준 마커 지도 — {map_mbti} 비율"
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.caption("🖌️ `capitals.csv`가 없어 국가 색칠 지도로 대체함(수도 마커 미표시).")
    # 국가 이름 기반 Choropleth
    fig_ch = px.choropleth(
        map_base,
        locations="Country",
        locationmode="country names",
        color="Ratio",
        color_continuous_scale="Blues",
        hover_name="Country",
        hover_data={"Ratio": ":.2%"},
        projection="natural earth",
        title=f"🗺️ 국가 색칠 지도 — {map_mbti} 비율"
    )
    st.plotly_chart(fig_ch, use_container_width=True)

# =========================
# 원자료 표
# =========================
if show_table:
    st.subheader("🔎 원자료(선택국)")
    st.dataframe(df[df["Country"].isin(selected_countries)].reset_index(drop=True))

# =========================
# 푸터 안내
# =========================
st.markdown(
    """
    ---  
    🔧 팁  
    - **capitals.csv**(선택): `Country, Capital, Latitude, Longitude` 컬럼을 가진 CSV를 같은 폴더에 두면 수도 마커 지도 활성화됨.  
    - **상위 N**: 선택국 평균으로 공통 Top N 유형을 뽑아 비교함.  
    - **레이더**: 여러 국가를 겹쳐 비교 가능함.  
    - **파이**: 1개 국가는 해당 나라 파이, 여러 국가는 평균 파이로 표시함.  
    """
)

st.success("✨ 준비 완료! 원하는 국가를 선택해 탐색하고, 상단 사이드바 옵션으로 차트 유형과 상위 N을 조정하면 됨 😊")
