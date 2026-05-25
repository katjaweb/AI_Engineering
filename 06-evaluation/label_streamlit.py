import streamlit as st
import json
import os

st.set_page_config(layout="wide", page_title="Agent Response Labeling")

# Load results.json
def load_results(path):
    if not os.path.exists(path):
        st.error(f"File not found: {path}")
        st.stop()
    with open(path, "r") as f:
        return json.load(f)

def save_results(data, path):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

results_path = os.path.join(os.path.dirname(__file__), "results_20260525_085829.json")
data = load_results(results_path)

if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0

st.title("Agent Response Labeling")

# Navigation
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("⬅️ Prev"):
        st.session_state.current_idx = max(0, st.session_state.current_idx - 1)
    if st.button("➡️ Next"):
        st.session_state.current_idx = min(len(data) - 1, st.session_state.current_idx + 1)

with col2:
    st.progress((st.session_state.current_idx + 1) / len(data))
    st.write(f"Question {st.session_state.current_idx + 1} of {len(data)}")

item = data[st.session_state.current_idx]

st.subheader("❓ User Question")
st.markdown(f"**{item['question']}**")

st.subheader("📝 Agent Response")
st.markdown(item['output'])

# Labeling
st.subheader("Label this response:")
label = st.radio(
    "Is this response good?",
    ["Not labeled", "Good", "Bad"],
    index=1 if item.get("label") == "good" else 2 if item.get("label") == "bad" else 0,
    horizontal=True,
)

comments = st.text_area("Comments (optional)", value=item.get("comments", ""))

if st.button("💾 Save Label"):
    if label == "Good":
        item["label"] = "good"
    elif label == "Bad":
        item["label"] = "bad"
    else:
        item["label"] = None
    item["comments"] = comments
    save_results(data, results_path)
    st.success("Label saved!")

# Quick jump to any question
st.sidebar.header("Jump to question")
selected = st.sidebar.selectbox(
    "Go to question:",
    options=list(range(len(data))),
    format_func=lambda i: f"{'✅' if data[i].get('label') == 'good' else '❌' if data[i].get('label') == 'bad' else '⬜'} {data[i]['question'][:40]}...",
    index=st.session_state.current_idx,
)
if selected != st.session_state.current_idx:
    st.session_state.current_idx = selected
    st.experimental_rerun()

# Show summary stats
labeled = sum(1 for x in data if x.get("label") is not None)
st.sidebar.markdown(f"**Labeled:** {labeled} / {len(data)}")
if labeled == len(data):
    st.sidebar.success("🎉 All responses labeled!")
