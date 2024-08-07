import os
import streamlit as st
from openai import OpenAI
import base64
import tempfile

st.set_page_config(page_title="Education Assistant Dashboard", layout="wide")

# OpenAI設定
MODEL = "gpt-4o-2024-08-06" 
client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])

# セッション状態の初期化
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'show_checker' not in st.session_state:
    st.session_state.show_checker = False


# 既存の関数（generate_questions, get_scope_example, show_input_area）はそのまま維持
def generate_questions(subject, question_type, num_questions, difficulty, scope):
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",
             "content": "あなたは経験豊富な教師です。生徒に渡すための問題を作成してください。標準出力で大丈夫です。問題を生成し終えたのち回答を出力してください。"},
            {"role": "user",
             "content": f"{subject}の{question_type}形式で、{difficulty}レベルの生徒向けの問題を{num_questions}問作成してください。範囲は「{scope}」です。"}
        ]
    )
    return completion.choices[0].message.content

# --- UIカスタマイズ ---
st.markdown(
    """
    <style>
        .stApp {
            background-color: #E6F3FF; /* 薄い青色 */
        }
        .main {
            background-color: white;
            padding: 20px;
            border-radius: 20px;
        }
        .stButton>button {
            background-color: #4E8098; /* 落ち着いた青色 */
            color: white;
            border: none;
            border-radius: 20px;
            padding: 15px 25px;
            font-family: 'Rounded Mplus 1c', sans-serif; /* 丸ゴシック体 */
            font-size: 16px;
            transition: all 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stButton>button:hover {
            background-color: #3A6073; /* ホバー時の色 */
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }
        .subject-button {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }
        .subject-button i {
            margin-right: 10px;
            font-size: 20px;
        }
        /* アイコンフォントを追加（例：Font Awesome） */
        @import url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css");
    </style>
    """,
    unsafe_allow_html=True,
)
def get_scope_example(subject):
    examples = {
        "数学": "中学2年生の2次方程式",
        "理科": "中学3年生の遺伝の法則",
        "国語": "高校1年生の古文（平安時代）",
        "社会": "小学6年生の日本の歴史（江戸時代）",
        "英語": "中学3年生の不定詞",
        "その他": "高校2年生の音楽（クラシック音楽史）"
    }
    return examples.get(subject, "例: 中学2年生の2次方程式")

def show_input_area(subject):
    if subject:
        st.subheader(f"{subject}の問題生成")
        question_type = st.selectbox("問題形式を選択してください:", ["選択問題", "記述問題", "穴埋め問題"])
        num_questions = st.number_input("問題数を入力してください:", min_value=1, value=5)
        difficulty = st.selectbox("難易度を選択してください:", ["簡単", "普通", "難しい"])
        scope_example = get_scope_example(subject)
        scope = st.text_input("問題の範囲を入力してください:", placeholder=f"例: {scope_example}")

        if st.button("問題生成"):
            if not scope:
                st.warning("問題の範囲を入力してください。")
            else:
                with st.spinner("問題を生成中..."):
                    response = generate_questions(subject, question_type, num_questions, difficulty, scope)
                
                # Split the response into questions and answers
                parts = response.split("回答:")
                questions = parts[0].strip()
                # answers = parts[1].strip() if len(parts) > 1 else "回答が見つかりません。"

                st.subheader("生成された問題:")
                st.text_area("", value=questions, height=200)

                # st.subheader("回答:")
                # st.text_area("回答:", value=answers, height=200)


def encode_image(image_file):
    with open(image_file, "rb") as f:
        image_data = f.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
    return base64_image

def check_answer(question, correct_answer, uploaded_image):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_image.read())
        temp_file_path = temp_file.name

    base64_image = encode_image(temp_file_path)

    os.remove(temp_file_path)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"問題: {question}\n正答: {correct_answer}\n\nこの画像に書かれている回答は正答ですか？"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
    )
    return response.choices[0].message.content

def toggle_checker():
    st.session_state.show_checker = not st.session_state.show_checker

# メインレイアウト
st.title("教育アシスタントダッシュボード")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="subject-button">', unsafe_allow_html=True)
    st.button("🧮 数学", on_click=lambda: st.session_state.update(selected_subject="数学"))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="subject-button">', unsafe_allow_html=True)
    st.button("🧪 理科", on_click=lambda: st.session_state.update(selected_subject="理科"))
    st.markdown('</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="subject-button">', unsafe_allow_html=True)
    st.button("📖 国語", on_click=lambda: st.session_state.update(selected_subject="国語"))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="subject-button">', unsafe_allow_html=True)
    st.button("🌎 社会", on_click=lambda: st.session_state.update(selected_subject="社会"))
    st.markdown('</div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="subject-button">', unsafe_allow_html=True)
    st.button("🇬🇧 英語", on_click=lambda: st.session_state.update(selected_subject="英語"))
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="subject-button">', unsafe_allow_html=True)
    st.button("🎨 その他", on_click=lambda: st.session_state.update(selected_subject="その他"))
    st.markdown('</div>', unsafe_allow_html=True)

# 選択された教科に応じて入力エリアを表示
if st.session_state.selected_subject:
    show_input_area(st.session_state.selected_subject)

# サイドバーに追加の機能を配置
with st.sidebar:
    st.subheader("その他の機能")
    if st.button("📝 授業計画作成"):
        st.write("授業計画作成機能は準備中です。")
    if st.button("📊 成績分析"):
        st.write("成績分析機能は準備中です。")
    if st.button("📅 スケジュール管理"):
        st.write("スケジュール管理機能は準備中です。")
    
    # 正誤チェッカーボタン
    st.button("✅ 正誤チェッカー", on_click=toggle_checker)

    # 正誤チェッカーの表示
    if st.session_state.show_checker:
        st.subheader("手書き回答チェック")
        question = st.text_area("問題文を入力してください:")
        correct_answer = st.text_input("正答を入力してください:")
        uploaded_image = st.file_uploader("回答画像をアップロードしてください", type=["jpg", "png", "jpeg"])

        if st.button("回答をチェック"):
            if question and correct_answer and uploaded_image:
                result = check_answer(question, correct_answer, uploaded_image)
                st.write("回答:", result)
            else:
                st.warning("問題文、正答、回答画像を全て入力してください。")