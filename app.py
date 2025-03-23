import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import requests
import joblib
from zoneinfo import ZoneInfo

# ---------------------------
# キャッシュ関数の定義
# ---------------------------
@st.cache_data(ttl=60)
def get_catalog_length():
    url = "https://may.2chan.net/b/futaba.php?mode=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return len(data["res"])
    except Exception as e:
        st.error(f"Error fetching catalog data: {e}")
        return None

@st.cache_resource
def load_model(quantile):
    file_name = f"./models/lgbm_quantile_{int(quantile*100)}.pkl"
    return joblib.load(file_name)

# ---------------------------
# モデルの読み込み（quantileごと）
# ---------------------------
model_lower = load_model(0.05)
model_median = load_model(0.5)
model_upper = load_model(0.95)

# ---------------------------
# 現在時刻と入力特徴量の準備
# ---------------------------
now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
hour = now.hour
minute = now.minute
weekday = now.weekday()  # Monday=0, Sunday=6
catalog_length = get_catalog_length()

# 学習時と同じ特徴量の順序で DataFrame 作成
sample_features = pd.DataFrame({
    'hour': [hour],
    'minute': [minute],
    'weekday': [weekday],
    'catalog_length': [catalog_length]
})

# ---------------------------
# 各 quantile に対する予測（単位：分）
# ---------------------------
pred_lower = model_lower.predict(sample_features)[0]
pred_median = model_median.predict(sample_features)[0]
pred_upper = model_upper.predict(sample_features)[0]

# 現在時刻に予測分を加算し、具体的な時刻に変換
pred_time_lower = now + timedelta(minutes=pred_lower)
pred_time_median = now + timedelta(minutes=pred_median)
pred_time_upper = now + timedelta(minutes=pred_upper)

# ---------------------------
# Streamlit 画面表示
# ---------------------------
st.title(':seedling: mayスレッド落ち時刻予想')
st.markdown("今スレッドを立てると…")
st.metric(label="スレッド落ち時刻予想", value=pred_time_median.strftime('%H:%M'), border=True, label_visibility="collapsed")
st.markdown("頃落ちそうです！")
st.caption("※予測は統計モデルに基づいて算出されています。参考程度にご利用ください。")
st.divider()

with st.expander("さらに詳しい値を見る"):
    col1, col2 = st.columns(2)
    col1.metric(label="スレッド落ち時刻予想(最小)", value=pred_time_lower.strftime('%H:%M'), border=True)
    col2.metric(label="スレッド落ち時刻予想(最大)", value=pred_time_upper.strftime('%H:%M'), border=True)

    col3, col4 = st.columns(2)
    col3.metric(label="現在のスレッド数", value=catalog_length, border=True)

with st.expander("どうやって計算しているの?"):
    st.markdown("このアプリは `2025-01-09` から `2025-03-08` までのmayの **32,977スレッド** を学習し、**時刻**, **曜日**, **現在のカタログ数**からスレッドの生存時間(min)を予測しています。")
    st.markdown("スレッドがいつ落ちるのかはこの3つの値だけでほぼ決まるため、平均絶対誤差18分ほどの精度で予測できるようです。")