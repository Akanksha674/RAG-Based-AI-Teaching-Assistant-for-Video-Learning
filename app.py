import streamlit as st
import numpy as np
import pandas as pd
import joblib
import requests
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# Load data
# ---------------------------
df = joblib.load("embeddings.joblib")

# ---------------------------
# Functions
# ---------------------------

def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "bge-m3",
        "input": text_list
    })
    return r.json()["embeddings"]

def inference(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    return r.json()["response"]

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="AI Teaching Assistant", layout="centered")

st.title("📚 AI Teaching Assistant")
st.caption("Ask questions from your course videos 🎓")

# ---------------------------
# Chat History
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Chat Input
# ---------------------------
query = st.chat_input("Ask your question here...")

if query:

    # Store user message
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking... 🤔"):

            # Step 1: Embed query
            question_embedding = create_embedding([query])[0]

            # Step 2: Similarity search
            similarities = cosine_similarity(
                np.vstack(df['embedding']),
                [question_embedding]
            ).flatten()

            top_k = 5
            indices = similarities.argsort()[::-1][:top_k]
            context_df = df.loc[indices]

            # Step 3: Prompt
            prompt = f"""
You are an AI teaching assistant.

Here are lecture chunks:
{context_df[['title','number','start','end','text']].to_json(orient="records")}

User question:
"{query}"

Answer clearly and guide the user to the correct video and timestamp.
"""

            # Step 4: LLM response
            answer = inference(prompt)

        st.markdown(answer)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": answer})