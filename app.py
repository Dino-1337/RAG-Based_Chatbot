# app.py
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from ui.sidebar import render_sidebar
from ui.chat_templates import css, user_template, bot_template, loading_template
from core.text_processing import extract_text_from_file, chunk_text
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from core.deepseek_api import DeepSeekLLM
import faiss
import time
from typing import List

st.set_page_config(page_title="RAG Document Assistant", layout="wide")
st.markdown(css, unsafe_allow_html=True)

st.title("📄 RAG Document Assistant")
st.write("Upload documents, click **Process Documents**, then ask questions. Uses local embeddings + DeepSeek.")

# Sidebar UI
uploaded_files, chunk_size, overlap, process_btn, clear_btn = render_sidebar()

# Initialize session state keys
if "vectorstore" not in st.session_state:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'}, encode_kwargs={'device': 'cpu'})
    # Initialize empty vectorstore with no texts initially
    index = faiss.IndexFlatL2(384)
    st.session_state.vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=InMemoryDocstore({}), index_to_docstore_id={})
if "rag" not in st.session_state:
    # Setup RetrievalQA chain with LangChain LLM and retriever
    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = DeepSeekLLM()
    st.session_state.rag = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")
if "conversation" not in st.session_state:
    st.session_state.conversation = []  # list of {"role": "user"/"bot", "content": "..."}
if "docs_processed" not in st.session_state:
    st.session_state.docs_processed = False
if "processed_files" not in st.session_state:
    st.session_state.processed_files = []  # names of processed files

# Handle Clear All
if clear_btn:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'}, encode_kwargs={'device': 'cpu'})
    index = faiss.IndexFlatL2(384)
    st.session_state.vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=InMemoryDocstore({}), index_to_docstore_id={})
    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = DeepSeekLLM()
    st.session_state.rag = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")
    st.session_state.conversation = []
    st.session_state.docs_processed = False
    st.session_state.processed_files = []
    st.success("Cleared vector store and chat history.")

# Processing documents only when process_btn is pressed
if process_btn:
    if not uploaded_files:
        st.sidebar.warning("No files uploaded. Please upload files before clicking Process.")
    else:
        st.sidebar.info("Processing documents — this may take a while for many/large files.")
        progress_bar = st.sidebar.progress(0)
        total_files = len(uploaded_files)
        processed_names = []
        total_chunks = 0
        all_chunks = []
        try:
            for idx, f in enumerate(uploaded_files):
                # Extract text (supports PDF / DOCX / TXT)
                raw_text = extract_text_from_file(f)
                # Chunk text
                chunks = chunk_text(raw_text, chunk_size=chunk_size, overlap=overlap)
                all_chunks.extend(chunks)
                total_chunks += len(chunks)
                processed_names.append(f.name)
                # Update progress
                progress_bar.progress(int(((idx + 1) / total_files) * 100))

            # Create vectorstore with all chunks at once
            if all_chunks:
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'}, encode_kwargs={'device': 'cpu'})
                st.session_state.vectorstore = FAISS.from_texts(all_chunks, embedding=embeddings)

                # Update retriever and RAG chain with the new vectorstore
                retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 5})
                llm = DeepSeekLLM()
                st.session_state.rag = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, chain_type="stuff")

            st.session_state.docs_processed = True
            st.session_state.processed_files = processed_names
            st.sidebar.success(f"Processed {len(processed_names)} files ({total_chunks} chunks).")
        except Exception as e:
            st.sidebar.error(f"Error while processing files: {e}")
        finally:
            progress_bar.empty()

# MAIN: Chat area
chat_container = st.container()
input_container = st.container()

def render_chat(history: List[dict]):
    """
    Render full conversation using the HTML templates.
    Renders in order of messages in history.
    """
    for msg in history:
        content = str(msg.get("content", ""))
        if msg.get("role") == "user":
            st.markdown(user_template.replace("{{MSG}}", content), unsafe_allow_html=True)
        else:
            st.markdown(bot_template.replace("{{MSG}}", content), unsafe_allow_html=True)

# If docs processed show a small badge
if st.session_state.docs_processed:
    st.sidebar.info(f"📚 Documents processed: {', '.join(st.session_state.processed_files)}")

# Render existing conversation
with chat_container:
    render_chat(st.session_state.conversation)

# Chat input form (fixed at bottom)
with input_container:
    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("💬 Ask a question about your documents:", key="user_input", placeholder="Type your message here...")
        submitted = st.form_submit_button("Send")
        if submitted:
            if not st.session_state.docs_processed:
                st.warning("Please click **Process Documents** first to load uploads into the vector DB.")
            else:
                # 1) append user message and render immediately (so user sees their message)
                st.session_state.conversation.append({"role": "user", "content": user_msg})

                # Re-render chat (user message will appear)
                with chat_container:
                    render_chat(st.session_state.conversation)
                    # show loading bubble via a placeholder
                    loading_placeholder = st.empty()
                    loading_placeholder.markdown(loading_template, unsafe_allow_html=True)

                # 2) Call the RAG chain while showing a spinner in the top-right
                with st.spinner("Thinking..."):
                    try:
                        # Pass only the user message as query to the RAG chain
                        answer = st.session_state.rag({"query": user_msg})
                    except Exception as e:
                        answer = f"⚠️ Error calling RAG chain: {e}"

                # 3) Remove loading bubble and append bot message
                loading_placeholder.empty()
                st.session_state.conversation.append({"role": "bot", "content": answer})

                # 4) Render updated conversation (including bot reply)
                with chat_container:
                    render_chat(st.session_state.conversation)

# Footer / small tips
st.markdown("---")
st.markdown("Tip: Upload PDF/TXT/DOCX files in the sidebar, click **Process Documents**, then ask questions. Use **Clear All** to reset.")
