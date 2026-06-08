# Streamlit 前端页面启动入口
import streamlit as st
import requests
import time

# 配置常量。不要把 URL 硬编码在代码逻辑里
API_GENERATE_URL = "http://127.0.0.1:8000/api/v1/generate"
BASE_SERVER_URL = "http://127.0.0.1:8000"

# 1. 设置网页的全局配置（标题、图标、布局）
st.set_page_config(page_title="智能有声书引擎", page_icon="🎧", layout="centered")

# 2. 页面标题与描述
st.title("🎧 智能有声书生成引擎 (VoxCPM)")
st.markdown("""
基于大模型的 **Tokenizer-Free** 前沿语音合成技术。
本系统已实现：**长文本清洗 ➡️ 智能语义断句 ➡️ 并行推理引擎 ➡️ 音频无缝混音** 的全自动流水线。
""")
st.divider()  # 一条华丽的分割线

# 3. 用户输入区域
text_input = st.text_area(
    "📝 请输入需要转换的小说或文章：",
    height=200,
    placeholder="例如：这是人类历史上最伟大的一天。所有人都在注视着天空，等待着那个声音的降临..."
)

# 4. 核心交互按钮
# use_container_width=True 会让按钮变得宽大醒目
if st.button("🚀 启动自动化生成流水线", type="primary", use_container_width=True):

    # 基础校验：防止用户乱点
    if not text_input.strip():
        st.warning("⚠️ 请先输入一点文本内容哦！")
    else:
        # 5. 调用后端 API 进行处理
        # st.spinner 会在界面上展示一个优雅的转圈等待动画
        with st.spinner("AI 引擎疯狂运转中，请确保您的后端 FastAPI 服务已开启..."):
            try:
                start_time = time.time()

                # 构建请求体，匹配我们后端定义的 Pydantic Schema
                payload = {"text": text_input, "voice_preset": "default"}

                # 发送 POST 网络请求给后端
                response = requests.post(API_GENERATE_URL, json=payload)

                # 如果 HTTP 状态码是 200，说明网络请求成功
                if response.status_code == 200:
                    result = response.json()

                    if result.get("success"):
                        end_time = time.time()
                        st.success(f"🎉 {result.get('message')} (总耗时: {end_time - start_time:.2f} 秒)")

                        # 拼接静态文件的完整访问 URL
                        audio_url = BASE_SERVER_URL + result.get("audio_url")

                        # 6. 在网页上直接渲染音频播放器！
                        st.audio(audio_url, format="audio/wav")

                    else:
                        st.error(f"❌ 业务逻辑失败: {result.get('message')}")
                else:
                    st.error(f"❌ 服务器内部报错，状态码: {response.status_code}")

            # 网络异常捕获。服务器没开时不能让前端页面崩溃
            except requests.exceptions.ConnectionError:
                st.error("🚨 无法连接到后端服务！请检查是否已在另一个终端窗口运行了 `uvicorn main_api:app`")
            except Exception as e:
                st.error(f"💥 发生未知系统错误: {e}")