# A — 디지털 트윈 챗봇

HW5 페르소나(v3)로 지인 A처럼 대화하는 챗봇입니다.

## 실행

```powershell
cd C:\Users\DAESUNG-339\a-digital-twin-chatbot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

`.env`에 OpenAI API 키를 넣은 뒤:

```powershell
streamlit run app.py
```
