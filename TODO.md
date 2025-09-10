# TODO List for Fixing FAISS Initialization Error

- [x] Add necessary imports to app.py (faiss, InMemoryDocstore)
- [x] Replace FAISS.from_texts initialization in app.py with manual FAISS creation for empty vectorstore
- [x] Replace FAISS.from_texts in clear_btn section of app.py
- [x] Update core/vectorstore.py to handle empty texts initialization
- [x] Test the app to ensure the error is fixed
