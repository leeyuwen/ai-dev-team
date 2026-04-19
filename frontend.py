import streamlit as st
import requests
import json

st.set_page_config(
    page_title="AI 开发团队",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI 开发团队")
st.markdown("由多个AI角色组成的开发团队，从需求到部署全流程自动化")

API_URL = "http://localhost:8000/develop/stream"

if "development_result" not in st.session_state:
    st.session_state.development_result = None
if "current_status" not in st.session_state:
    st.session_state.current_status = ""
if "product_spec" not in st.session_state:
    st.session_state.product_spec = ""
if "code_result" not in st.session_state:
    st.session_state.code_result = ""
if "test_result" not in st.session_state:
    st.session_state.test_result = ""
if "deploy_result" not in st.session_state:
    st.session_state.deploy_result = ""
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

with st.form(key="development_form"):
    st.subheader("📝 输入项目需求")
    requirement = st.text_area(
        "请详细描述您的项目需求:",
        height=150,
        placeholder="例如：创建一个基于FastAPI的用户管理系统，包含用户注册、登录、权限管理等功能...",
        disabled=st.session_state.is_processing
    )
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_button = st.form_submit_button(
            label="🚀 开始开发",
            disabled=st.session_state.is_processing
        )
    with col2:
        if st.form_submit_button("🔄 重置", disabled=st.session_state.is_processing):
            st.session_state.clear()
            st.rerun()

if submit_button and requirement:
    st.session_state.is_processing = True
    st.session_state.development_result = None
    st.session_state.current_status = "正在连接服务器..."
    st.session_state.product_spec = ""
    st.session_state.code_result = ""
    st.session_state.test_result = ""
    st.session_state.deploy_result = ""

    status_placeholder = st.empty()
    progress_bar = st.progress(0)
    progress_text = st.empty()

    try:
        def process_stream():
            try:
                response = requests.post(
                    API_URL,
                    json={"requirement": requirement},
                    stream=True,
                    timeout=600
                )

                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('event: '):
                            event_type = line.split(': ')[1]
                        elif line.startswith('data: '):
                            data_str = line[6:]
                            try:
                                data = json.loads(data_str)
                                yield data
                            except:
                                pass
            except Exception as e:
                yield {"type": "error", "data": str(e)}

        events = process_stream()

        progress_steps = [
            ("产品经理正在分析需求...", 25),
            ("开发工程师正在编写代码...", 50),
            ("测试工程师正在编写测试用例...", 75),
            ("部署工程师正在制定部署方案...", 100)
        ]

        step_index = 0

        for event in events:
            if event["type"] == "status":
                status_text = event["data"]
                st.session_state.current_status = status_text
                status_placeholder.info(f"� {status_text}")

                if step_index < len(progress_steps):
                    _, progress_value = progress_steps[step_index]
                    progress_bar.progress(progress_value)
                    progress_text.text(f"进度: {progress_value}%")
                    step_index += 1

            elif event["type"] == "product_manager":
                st.session_state.product_spec = event["data"]
                progress_bar.progress(25)
                progress_text.text("进度: 25%")

            elif event["type"] == "developer":
                st.session_state.code_result = event["data"]
                progress_bar.progress(50)
                progress_text.text("进度: 50%")

            elif event["type"] == "tester":
                st.session_state.test_result = event["data"]
                progress_bar.progress(75)
                progress_text.text("进度: 75%")

            elif event["type"] == "devops":
                st.session_state.deploy_result = event["data"]
                progress_bar.progress(90)
                progress_text.text("进度: 90%")

            elif event["type"] == "complete":
                st.session_state.development_result = event["data"]
                progress_bar.progress(100)
                progress_text.text("进度: 100%")
                status_placeholder.success("✅ 开发完成!")
                st.session_state.is_processing = False

            elif event["type"] == "error":
                status_placeholder.error(f"❌ 发生错误: {event['data']}")
                st.session_state.is_processing = False

    except Exception as e:
        status_placeholder.error(f"❌ 连接失败: {str(e)}")
        st.session_state.is_processing = False

if st.session_state.product_spec or st.session_state.code_result or st.session_state.test_result or st.session_state.deploy_result:
    st.divider()
    st.subheader("📋 开发结果")

    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.product_spec:
            with st.expander("📋 产品规格文档", expanded=True):
                st.markdown(st.session_state.product_spec)

        if st.session_state.code_result:
            with st.expander("� 代码实现"):
                st.markdown(st.session_state.code_result)

    with col2:
        if st.session_state.test_result:
            with st.expander("🧪 测试报告"):
                st.markdown(st.session_state.test_result)

        if st.session_state.deploy_result:
            with st.expander("🚢 部署计划"):
                st.markdown(st.session_state.deploy_result)

st.sidebar.title("ℹ️ 使用说明")
st.sidebar.markdown("""
1. **输入项目需求**
2. **点击开始开发**
3. **实时查看进度** - 每个Agent完成时会显示结果
4. **最终结果** - 包含产品规格、代码、测试和部署方案
""")

st.sidebar.title("⚙️ 当前配置")
st.sidebar.markdown("""
- Provider: MiniMax
- Model: MiniMax-M2.7
""")