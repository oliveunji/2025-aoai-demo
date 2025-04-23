import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수 로드 및 유효성 검사
api_key = os.getenv("APPSETTING_AZURE_OPENAI_API_KEY")
endpoint = os.getenv("APPSETTING_AZURE_OPENAI_ENDPOINT")

if not api_key or not endpoint:
    st.error("API 키 또는 엔드포인트가 환경변수에 설정되어 있지 않습니다.")
    st.stop()

# Azure OpenAI 환경변수 설정
os.environ["AZURE_OPENAI_API_KEY"] = api_key
os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint

# AzureChatOpenAI 모델 초기화
model = AzureChatOpenAI(
    openai_api_version="2024-08-01-preview",
    azure_deployment="gpt-4o-mini",
    temperature=0.7
)

# 면접 질문 생성 프롬프트 템플릿
interview_q_prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        "당신은 면접관 AI입니다. 주어진 채용공고와 이력서를 바탕으로 지원자에게 묻기 위한 예상 면접 질문 5개를 번호와 함께 생성하세요. 답변은 한국어로 간결하고 명확하게 작성하십시오."
    ),
    (
        "user", 
        "채용공고: {job_description}\n이력서: {resume}"
    )
])

# 지원자 답변 피드백 프롬프트 템플릿
feedback_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "당신은 면접관 AI입니다. 지원자가 면접 질문에 제시한 답변을 평가하고 피드백을 제공하세요. 피드백은 구체적이며 긍정점과 개선점을 모두 포함해야 합니다."
    ),
    (
        "user",
        "면접 질문: {question}\n지원자 답변: {answer}"
    )
])

st.title("모의면접관 AI 서비스")

# 사이드바 파일 업로드 섹션
with st.sidebar:
    st.header("파일 업로드")
    job_file = st.file_uploader("채용공고 파일 업로드 (TXT)", type=["txt"], key="job")
    resume_file = st.file_uploader("이력서 파일 업로드 (TXT)", type=["txt"], key="resume")

job_text = ""
resume_text = ""

if job_file:
    job_text = job_file.getvalue().decode("utf-8")

if resume_file:
    resume_text = resume_file.getvalue().decode("utf-8")

# 면접 질문 생성
if st.button("면접 질문 생성"):
    if job_text and resume_text:
        messages = interview_q_prompt.format_messages(job_description=job_text, resume=resume_text)
        try:
            interview_questions = model(messages).content
            st.session_state["interview_questions"] = interview_questions
            st.success("면접 질문이 생성되었습니다!")
        except Exception as e:
            st.error(f"면접 질문 생성 중 오류 발생: {str(e)}")
    else:
        st.error("잡 디스크립션과 이력서 파일을 모두 업로드해 주세요.")

# 생성된 면접 질문 출력
if "interview_questions" in st.session_state:
    st.subheader("생성된 면접 질문")
    st.write(st.session_state["interview_questions"])

st.markdown("---")
st.subheader("답변 피드백 받기")

# 사용자가 피드백 받고자 하는 면접 질문과 본인의 답변 입력
feedback_question = st.text_input("피드백 받고자 하는 면접 질문 입력")
candidate_answer = st.text_area("지원자 답변 입력")

if st.button("답변 피드백 받기"):
    if feedback_question and candidate_answer:
        messages = feedback_prompt.format_messages(question=feedback_question, answer=candidate_answer)
        try:
            feedback = model(messages).content
            st.subheader("피드백")
            st.write(feedback)
        except Exception as e:
            st.error(f"피드백 생성 중 오류 발생: {str(e)}")
    else:
        st.error("면접 질문과 지원자 답변을 모두 입력해 주세요.")

# 세션 초기화
if st.button("세션 초기화"):
    st.session_state.clear()
    st.experimental_rerun()
