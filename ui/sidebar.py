# ui/sidebar.py
import streamlit as st

def render_sidebar():
    """
    Renders the sidebar and returns:
    uploaded_files, chunk_size, overlap, process_btn (bool), clear_btn (bool)
    """
    st.sidebar.title("📄 Upload Documents")
    uploaded_files = st.sidebar.file_uploader(
        "Choose PDF / TXT / DOCX", accept_multiple_files=True, type=["pdf", "txt", "docx"]
    )

    st.sidebar.markdown("---")
    st.sidebar.title("⚙️ Settings")
    chunk_size = st.sidebar.slider("Chunk size (chars)", 100, 2000, 500)
    overlap = st.sidebar.slider("Chunk overlap (chars)", 0, 500, 50)

    st.sidebar.markdown("---")
    process_btn = st.sidebar.button("🚀 Process Documents")
    clear_btn = st.sidebar.button("🗑️ Clear All")

    # Optionally show small help text
    st.sidebar.markdown(
        "Upload documents (PDF/TXT/DOCX). Click **Process Documents** once all files are uploaded.\n\n"
        "Use **Clear All** to reset the vector DB and chat history."
    )

    return uploaded_files, chunk_size, overlap, process_btn, clear_btn
