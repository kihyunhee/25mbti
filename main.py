import streamlit as st
import pandas as pd

# CSV 파일 불러오기
df = pd.read_csv("countriesMBTI_16types.csv")

# 제목 표시
st.title("Countries MBTI 16 Types 데이터 미리보기")

# 상위 5줄만 출력
st.write("데이터 상위 5줄:")
st.dataframe(df.head())

