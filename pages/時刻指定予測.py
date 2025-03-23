import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import joblib
from zoneinfo import ZoneInfo

# ---------------------------
# モデルの読み込み（catalog_lengthを除いた quantile 予測モデル）
# ---------------------------
@st.cache_resource
def load_model(quantile):
    # quantile の値は 5, 50, 95 を想定
    file_name = f"./models/lgbm_quantile_without_catalog_{int(quantile)}.pkl"
    return joblib.load(file_name)

# quantile 毎のモデルを読み込み
model_lower = load_model(5)
model_median = load_model(50)
model_upper = load_model(95)

# ---------------------------
# ページタイトルと説明
# ---------------------------
st.title(':seedling: 指定時刻でスレッド落ち予測')
st.markdown("""
指定された開始時刻と曜日の場合に、スレッドが落ちる時刻を予測します。  
このモデルはカタログ数の情報を除外して学習しているため、予測精度は若干低くなっている可能性があります。
""")

# ---------------------------
# ユーザー入力
# ---------------------------
user_time = st.time_input("スレ立て時刻(ざっくり)を選択してください", datetime.time(12, 0))
weekday_option = st.selectbox("曜日を選択してください", 
                              options=["月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日", "日曜日"])
weekday_mapping = {"月曜日": 0, "火曜日": 1, "水曜日": 2, "木曜日": 3, "金曜日": 4, "土曜日": 5, "日曜日": 6}
selected_weekday = weekday_mapping[weekday_option]

# ---------------------------
# 予測実行ボタン押下時の処理
# ---------------------------
if st.button("予測実行"):
    # 入力された時刻から hour, minute を抽出
    hour = user_time.hour
    minute = user_time.minute

    # 学習時と同じ特徴量の順序で DataFrame 作成（catalog_length は含まず）
    features = pd.DataFrame({
        "hour": [hour],
        "minute": [minute],
        "weekday": [selected_weekday]
    })

    # 各 quantile に対する予測（単位は分）
    pred_lower = model_lower.predict(features)[0]
    pred_median = model_median.predict(features)[0]
    pred_upper = model_upper.predict(features)[0]

    # ユーザー入力の時刻は日付が含まれていないため、本日の日付と組み合わせる
    base_datetime = datetime.datetime.combine(datetime.date.today(), user_time)
    finish_time_lower = base_datetime + timedelta(minutes=pred_lower)
    finish_time_median = base_datetime + timedelta(minutes=pred_median)
    finish_time_upper = base_datetime + timedelta(minutes=pred_upper)

    # ---------------------------
    # 結果表示（st.metric, st.divider, st.expander を使用）
    # ---------------------------
    st.markdown("## 予測結果")
    st.markdown("指定された時刻の場合、")
    st.metric(label="スレッド落ち時刻予想", 
              value=finish_time_median.strftime('%H:%M'),
              label_visibility="collapsed",
              border=True)
    st.markdown("頃に落ちると予測されます！")
    st.divider()

    with st.expander("詳細情報を見る"):
        col1, col2 = st.columns(2)
        col1.metric(label="最小予測時刻", value=finish_time_lower.strftime('%H:%M'), border=True)
        col2.metric(label="最大予測時刻", value=finish_time_upper.strftime('%H:%M'), border=True)
