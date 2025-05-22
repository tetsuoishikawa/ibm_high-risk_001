import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import re

# 認証情報をsecretsから読み込み
API_KEY = st.secrets["nlu_api_key"]
API_URL = st.secrets["nlu_url"] + "/v1/analyze?version=2021-08-01"
MODEL_ID = st.secrets["nlu_model_id"]

# ラベルごとのハイライト色
COLOR_MAP = {
    "high_risk": "background-color: #ff6666;",  # 赤
    "risk": "background-color: #ffcc66;",       # オレンジ
    "hazard": "background-color: #99ff99;",     # 緑
    "state": "background-color: #cccccc;"       # グレー
}

# ハイライト処理（text + typeベースでマッチング）
def highlight_entities(text, entities):
    # 重複を除去して長い語句順に並び替え
    unique_ents = sorted(
        list({(ent["text"], ent["type"]) for ent in entities}),
        key=lambda x: -len(x[0])
    )

    # ハイライト表示用テキスト生成
    for phrase, label in unique_ents:
        style = COLOR_MAP.get(label, "background-color: #dddddd;")
        pattern = re.escape(phrase)
        span = f"<span style='{style} padding:2px; border-radius:4px;' title='{label}'>{phrase}</span>"
        text = re.sub(pattern, span, text, flags=re.IGNORECASE)
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
                st.markdown("### 🖍 抽出ハイライト", unsafe_allow_html=True)
                st.markdown(f"<div style='line-height:1.8'>{highlighted}</div>", unsafe_allow_html=True)

                # 詳細一覧表示
                st.markdown("### 📝 抽出語句一覧")
                for ent in entities:
                    confidence = ent.get("confidence")
                    if confidence is not None:
                        st.write(f"【{ent['type']}】{ent['text']}（信頼度: {confidence:.2f}）")
                    else:
                        st.write(f"【{ent['type']}】{ent['text']}")
            else:
                st.error(f"エラーが発生しました（コード: {response.status_code}）")
