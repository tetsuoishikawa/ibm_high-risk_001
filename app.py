import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import re

# 認証情報をsecretsから取得
API_KEY = st.secrets["nlu_api_key"]
API_URL = st.secrets["nlu_url"] + "/v1/analyze?version=2021-08-01"
MODEL_ID = st.secrets["nlu_model_id"]

# ラベルごとの色（最新版）
COLOR_MAP = {
    "high_risk": "#cc66ff",   # 紫
    "risk": "#ff6666",        # 赤
    "hazard": "#99ff99",      # 緑
    "state": "#cccccc"        # グレー
}

# ハイライト処理（textベース版）
def highlight_entities(text, entities):
    unique_ents = sorted(
        list({(ent["text"], ent["type"]) for ent in entities}),
        key=lambda x: -len(x[0])
    )
    for phrase, label in unique_ents:
        color = COLOR_MAP.get(label, "#dddddd")
        pattern = re.escape(phrase)
        span = f"<span style='background-color: {color}; padding:2px; border-radius:4px;' title='{label}'>{phrase}</span>"
        text = re.sub(pattern, span, text, flags=re.IGNORECASE)
    return text

# UI構築
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

                # デバッグ用：レスポンス内容を確認
                # st.json(entities)

                # ハイライト表示
                highlighted = highlight_entities(user_input, entities)
                st.markdown("### 🖍 抽出ハイライト", unsafe_allow_html=True)
                st.markdown(f"<div style='line-height:1.8'>{highlighted}</div>", unsafe_allow_html=True)

                # 抽出語句一覧
                st.markdown("### 📝 抽出語句一覧")
                for ent in entities:
                    conf = ent.get("confidence")
                    if conf is not None:
                        st.write(f"【{ent['type']}】{ent['text']}（信頼度: {conf:.2f}）")
                    else:
                        st.write(f"【{ent['type']}】{ent['text']}")
            else:
                st.error(f"エラーが発生しました（ステータスコード: {response.status_code}）")
