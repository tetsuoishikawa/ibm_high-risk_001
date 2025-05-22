import streamlit as st
import requests
from requests.auth import HTTPBasicAuth

# 認証情報をsecretsから読み込み
API_KEY = st.secrets["nlu_api_key"]
API_URL = st.secrets["nlu_url"] + "/v1/analyze?version=2021-08-01"
MODEL_ID = st.secrets["nlu_model_id"]

# 色設定
# ラベルごとのハイライト色（修正後）
COLOR_MAP = {
    "high_risk": "background-color: #ff6666;",  # 赤
    "risk": "background-color: #ffcc66;",       # オレンジ
    "hazard": "background-color: #99ff99;",     # 緑
    "state": "background-color: #cccccc;"       # グレー
}

# ハイライト処理
def highlight_entities(text, entities):
    # 重複回避のため位置情報付きリストに変換
    sorted_ents = sorted(entities, key=lambda x: x['start'], reverse=True)
    for ent in sorted_ents:
        label = ent['type']
        color = LABEL_COLORS.get(label, "#dddddd")
        span = f"<span style='background-color: {color}; padding: 2px; border-radius: 4px;' title='{label}'>{ent['text']}</span>"
        text = text[:ent['start']] + span + text[ent['end']:]
    return text

# Streamlit UI
st.title("🩺 ハイリスクワード抽出（WKS + NLU）")
user_input = st.text_area("患者関連の文章を入力してください：", height=300)

if st.button("推論開始"):
    if not user_input.strip():
        st.warning("文章を入力してください。")
    else:
        with st.spinner("NLUモデルで推論中..."):
            payload = {
                "text": user_input,
                "features": {
                    "entities": {
                        "model": MODEL_ID
                    }
                }
            }
            response = requests.post(API_URL, json=payload, auth=HTTPBasicAuth("apikey", API_KEY))
            if response.status_code == 200:
                result = response.json()
                entities = result.get("entities", [])
                st.success(f"{len(entities)} 件の注目語を抽出しました。")

                # ハイライト表示
                highlighted = highlight_entities(user_input, entities)
                st.markdown(highlighted, unsafe_allow_html=True)

                # 詳細一覧
                st.subheader("🔍 抽出された語句一覧")
                for ent in entities:
                    st.write(f"【{ent['type']}】{ent['text']}（信頼度: {ent['confidence']:.2f}）")
            else:
                st.error(f"エラーが発生しました: {response.status_code}")