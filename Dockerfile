FROM python:3.11

WORKDIR /app

# Streamlit 관련 환경 변수 설정
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_RUN_ON_SAVE=false

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 80

# Streamlit 앱 실행 명령어로 변경
CMD ["streamlit", "run", "main.py", "--server.port=80", "--server.address=0.0.0.0"]
