import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStore:
    def __init__(self, texts):
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={'device': 'cpu'})
        if not texts:
            index = faiss.IndexFlatL2(384)
            self.vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=InMemoryDocstore({}), index_to_docstore_id={})
        else:
            self.vectorstore = FAISS.from_texts(texts, embedding=embeddings)

    def add(self, embeddings, texts):
        # FAISS from_texts already adds texts, so this method can be a no-op or raise NotImplementedError
        raise NotImplementedError("Use VectorStore constructor to initialize with texts.")

    def search(self, query_embedding, top_k=5):
        # FAISS retriever usage
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        results = retriever.get_relevant_documents(query_embedding)
        # Return list of (score, text) tuples - LangChain retriever does not return scores by default
        return [(None, doc.page_content) for doc in results]
