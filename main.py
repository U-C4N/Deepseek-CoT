import streamlit as st
from deepseek_api import generate_response, set_api_key


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def set_api_key_in_sidebar():
    st.sidebar.header("Configuration")
    api_key = st.sidebar.text_input("Enter your DeepSeek API key:",
                                    type="password")
    if api_key:
        set_api_key(api_key)
    else:
        st.sidebar.warning(
            "Please enter your DeepSeek API key to use the chatbot.")
    return api_key


def toggle_chain_of_thought():
    return st.sidebar.checkbox("Enable Chain of Thought", value=False)


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def get_user_input(api_key_present):
    if not api_key_present:
        st.error("Please enter your DeepSeek API key in the sidebar.")
        return None
    return st.chat_input("What would you like to know?")


def add_message(role, content):
    st.session_state.messages.append({"role": role, "content": content})


def generate_and_display_response(prompt, use_cot):
    add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    add_message("assistant", "")  # Placeholder for assistant's message
    with st.chat_message("assistant") as assistant_message:
        message_placeholder = st.empty()
        full_response = ""
        reasoning_steps = []

        try:
            if use_cot:
                with st.spinner("Thinking..."):
                    for response in generate_response(prompt, use_cot):
                        if response.startswith("Step"):
                            reasoning_steps.append(response)
                        else:
                            full_response += response
                            message_placeholder.markdown(full_response + "▌")
            else:
                with st.spinner("Generating response..."):
                    for response in generate_response(prompt, use_cot):
                        full_response += response
                        message_placeholder.markdown(full_response + "▌")
        except Exception as e:
            full_response = "😕 Sorry, I encountered an error while generating the response."
            message_placeholder.markdown(full_response)
            st.error(f"Error: {e}")
            return

        message_placeholder.markdown(full_response)
        st.session_state.messages[-1][
            "content"] = full_response  # Update the placeholder message

        if use_cot and reasoning_steps:
            with st.expander("Show reasoning steps"):
                for step in reasoning_steps:
                    st.markdown(step)


def main():
    st.set_page_config(page_title="DeepSeek Chatbot",
                       page_icon="🤖",
                       layout="wide")
    st.title("🤖 DeepSeek Chatbot with Chain of Thought")

    initialize_session_state()

    api_key = set_api_key_in_sidebar()
    use_cot = toggle_chain_of_thought()

    st.write("---")
    display_chat_history()

    prompt = get_user_input(api_key_present=bool(api_key))
    if prompt:
        generate_and_display_response(prompt, use_cot)


if __name__ == "__main__":
    main()
