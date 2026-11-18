import os

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

from persona import SAMPLE_QUESTIONS, SYSTEM_PROMPT

load_dotenv()

st.set_page_config(
    page_title="A",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600&family=Song+Myung&display=swap');

:root {
  --ink: #1c2430;
  --mute: #5a6573;
  --paper: #e8eef4;
  --bubble-a: #fff7d6;
  --bubble-you: #d7e4f2;
}

html, body, [class*="css"] {
  font-family: "IBM Plex Sans KR", sans-serif;
  color: var(--ink);
}

.stApp {
  background:
    radial-gradient(1200px 520px at 18% -10%, #c5d4e4 0%, transparent 58%),
    radial-gradient(900px 480px at 110% 8%, #f3e2c4 0%, transparent 46%),
    linear-gradient(180deg, #d5dee8 0%, #eef2f6 42%, #f6f3ee 100%);
}

.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.18;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='80' height='80' filter='url(%23n)' opacity='0.55'/%3E%3C/svg%3E");
}

.block-container {
  padding-top: 2.4rem;
  max-width: 720px;
}

.brand {
  font-family: "Song Myung", serif;
  font-size: clamp(4.2rem, 14vw, 7.2rem);
  line-height: 0.9;
  letter-spacing: -0.04em;
  margin: 0 0 0.35rem;
  animation: rise 0.9s ease both;
}

.lead {
  font-size: 1.15rem;
  font-weight: 600;
  margin: 0 0 0.35rem;
}

.sub {
  color: var(--mute);
  font-size: 0.98rem;
  margin: 0 0 1.4rem;
  max-width: 28rem;
}

.stChatMessage {
  animation: fade 0.35s ease;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
  background: var(--bubble-a);
  border-radius: 4px 14px 14px 14px;
  padding: 0.7rem 0.9rem;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: var(--bubble-you);
  border-radius: 14px 4px 14px 14px;
  padding: 0.7rem 0.9rem;
}

.stButton > button {
  background: transparent;
  border: 1px solid #c3ced9;
  color: var(--ink);
  border-radius: 2px;
  font-family: "IBM Plex Sans KR", sans-serif;
  font-size: 0.86rem;
  text-align: left;
  white-space: normal;
  height: auto;
  padding: 0.55rem 0.7rem;
}

.stButton > button:hover {
  border-color: #1c2430;
  background: rgba(255,255,255,0.55);
}

@keyframes rise {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: none; }
}

@keyframes fade {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="brand">A</p><p class="lead">디지털 트윈</p>'
    '<p class="sub">2017년부터 알고 지낸 직장 후배와 카톡하듯 말해보세요.</p>',
    unsafe_allow_html=True,
)

# 1순위: 환경변수(.env 포함), 2순위: Streamlit Cloud의 Secrets
api_key = os.getenv("OPENAI_API_KEY", "").strip()
if not api_key:
    try:
        api_key = str(st.secrets["OPENAI_API_KEY"]).strip()
    except Exception:
        api_key = ""
if not api_key:
    st.warning("API 키가 설정되지 않았어요. 관리자에게 알려주세요.")
    st.stop()

client = OpenAI(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

cols = st.columns(2)
for i, q in enumerate(SAMPLE_QUESTIONS):
    if cols[i % 2].button(q, key=f"q{i}"):
        st.session_state.pending = (
            "과제 질문이야! 카톡으로 편하게 말하듯이 1~3줄로 답해줘. " + q
        )
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

prompt = st.chat_input("형처럼 말해보세요…") or st.session_state.pop("pending", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        collected = []
        stream = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.7,
            stream=True,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}]
            + st.session_state.messages,
        )
        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content or ""
            collected.append(delta)
            placeholder.markdown("".join(collected))
        answer = "".join(collected).strip()
        placeholder.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
