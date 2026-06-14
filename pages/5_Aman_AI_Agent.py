import streamlit as st
from lib.theme import page_header, glass
from lib.profile import PROFILE
from lib.agent_kb import answer_offline, answer_with_key, SUGGESTED

st.set_page_config(page_title="Aman's AI Agent", page_icon="🤖", layout="wide")
page_header("🤖 Aman's AI Agent",
            "Ask about strategy, GTM, M&A, transformation or healthcare — answered in my frameworks. "
            "Works fully offline (no key). Optionally paste an Anthropic key for richer, generated answers.")
st.page_link("Home.py", label="← Back to Studio")

with st.sidebar:
    st.header("Mode")
    api_key = st.text_input("Anthropic API key (optional)", type="password",
                            help="Leave blank to use the built-in offline knowledge base.")
    st.caption("No key required. Nothing is stored — the key is used only for your request.")

if "chat" not in st.session_state:
    st.session_state.chat = []

st.markdown("##### Try a question")
cols = st.columns(len(SUGGESTED))
for c, q in zip(cols, SUGGESTED):
    if c.button(q, use_container_width=True):
        st.session_state.pending = q

# render history
for role, msg in st.session_state.chat:
    with st.chat_message(role, avatar="🧑‍⚕️" if role == "user" else "🤖"):
        st.markdown(msg)

prompt = st.chat_input("Ask Aman's agent…")
prompt = prompt or st.session_state.pop("pending", None)

if prompt:
    st.session_state.chat.append(("user", prompt))
    with st.chat_message("user", avatar="🧑‍⚕️"):
        st.markdown(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        if api_key:
            with st.spinner("Thinking…"):
                ans, note = answer_with_key(prompt, api_key)
            if note:
                st.caption("⚠ " + note)
        else:
            ans, note = answer_offline(prompt), None
        st.markdown(ans)
    st.session_state.chat.append(("assistant", ans))

if not st.session_state.chat:
    glass('<div style="color:#aab4d6;font-size:.9rem">This agent retrieves from a curated knowledge base of my '
          'real frameworks and engagements — GTM, route-to-market, M&A synergies, cost transformation, HCP churn '
          'and MedTech business models. Pick a question above or type your own.</div>')

st.caption("Offline mode uses TF-IDF retrieval over a curated knowledge base — no data leaves the app. "
           f"For the real thing: {PROFILE['email']}.")
