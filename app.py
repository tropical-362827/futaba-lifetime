import streamlit as st
import pandas as pd
import datetime
import requests
import joblib

# catalog_length を取得する関数（キャッシュを使って60秒間有効）
@st.cache(ttl=60)
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

# quantile モデルの読み込み（キャッシュを利用）
@st.cache(allow_output_mutation=True)
def load_model(quantile):
    file_name = f"lgbm_quantile_{int(quantile*100)}.pkl"
    return joblib.load(file_name)

# quantile 毎のモデルを読み込む
model_lower = load_model(0.05)
model_median = load_model(0.5)
model_upper = load_model(0.95)

# 現在時刻から特徴量を抽出
now = datetime.datetime.now()
hour = now.hour
minute = now.minute
weekday = now.weekday()  # Monday=0, Sunday=6

# catalog_length の取得
catalog_length = get_catalog_length()

# 特徴量 DataFrame を作成（学習時と同じ順序で）
sample_features = pd.DataFrame({
    'hour': [hour],
    'minute': [minute],
    'weekday': [weekday],
    'catalog_length': [catalog_length]
})

# 各 quantile に対する予測値を取得
pred_lower = model_lower.predict(sample_features)[0]
pred_median = model_median.predict(sample_features)[0]
pred_upper = model_upper.predict(sample_features)[0]

# Streamlit 画面表示
st.title("Quantile Prediction App")
st.write("### 現在時刻と入力特徴量")
st.write(f"時刻: {now.strftime('%Y-%m-%d %H:%M:%S')}")
st.write(f"Hour: {hour}")
st.write(f"Minute: {minute}")
st.write(f"Weekday (0=月曜): {weekday}")
st.write(f"Catalog Length: {catalog_length}")

st.write("### Quantile 予測結果")
st.write(f"下側5%予測: {pred_lower:.2f}")
st.write(f"中央値予測: {pred_median:.2f}")
st.write(f"上側95%予測: {pred_upper:.2f}")
st.write(f"予測レンジ: {pred_lower:.2f} ~ {pred_upper:.2f}")
