# chains/rag_chain.py
from typing import List, Optional
import textwrap
import numpy as np

from core.deepseek_api import query_deepseek
from core.embeddings import get_embedding
from core.vectorstore import VectorStore

# Prompt templates
_QUERY_REWRITER_PROMPT = textwrap.dedent(
    """
    You are a helpful assistant that rewrites a user's latest question into a concise,
    keyword-rich search query meant to retrieve relevant document passages.
    Use the conversation history (if any) to create context-aware queries.
    Be concise: produce a single-line search query (3-12 words) focusing on the user's intent.

    Conversation history:
    {chat_history}

    Latest user message:
    {user_message}

    Produce a search query:
    """
).strip()

_ANSWER_PROMPT_TEMPLATE = textwrap.dedent(
    """
    You are an AI assistant that must answer the user's question using ONLY the provided document excerpts.
    - Read the document excerpts below.
    - If the excerpts contain enough information, produce a concise answer in natural language (not bullet lists),
      2-4 sentences per project. Do NOT copy verbatim — summarize and rephrase.
    - If the excerpts do not contain enough information, say "I don't have enough information in the documents" 
      and then optionally provide a brief general-knowledge answer prefaced with "General knowledge:".

    Document excerpts (most relevant first):
    {context}

    User's original question:
    {user_question}

    Answer:
    """
).strip()


class RAGChain:
    """
    RAGChain: rewrites query using conversation history, retrieves top chunks from the vectorstore,
    and asks DeepSeek to produce a summarized, context-aware answer.

    Example usage:
        rag = RAGChain(vectorstore)
        answer = rag.query("Summarize the project section", chat_history=st.session_state.conversation)
    """

    def __init__(self, vectorstore: VectorStore, top_k: int = 5):
        """
        vectorstore: instance of your core.VectorStore
        top_k: number of chunks to retrieve
        """
        if not isinstance(vectorstore, VectorStore):
            raise ValueError("vectorstore must be an instance of core.vectorstore.VectorStore")
        self.vectorstore = vectorstore
        self.top_k = top_k

    def _format_chat_history(self, chat_history: Optional[List[dict]]) -> str:
        """Format chat history (list of {'role':..., 'content':...}) into a short transcript."""
        if not chat_history:
            return ""
        lines = []
        for m in chat_history[-10:]:  # keep last 10 turns to keep rewriter focused
            role = m.get("role", "user")
            content = m.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def _rewrite_query(self, user_message: str, chat_history: Optional[List[dict]] = None) -> str:
        """Use DeepSeek to rewrite the user question into an effective search query."""
        chat_hist_text = self._format_chat_history(chat_history)
        prompt = _QUERY_REWRITER_PROMPT.format(chat_history=chat_hist_text, user_message=user_message)
        # call DeepSeek for rewriter — short response expected
        try:
            rewritten = query_deepseek(prompt)
            # Clean and keep on one line
            if not rewritten:
                return user_message
            rewritten = rewritten.strip().splitlines()[0]
            return rewritten
        except Exception:
            # On any error, fall back to raw user message
            return user_message

    def _retrieve(self, query: str) -> List[str]:
        """Embed the query and retrieve top-k chunks from the vectorstore."""
        try:
            q_emb = get_embedding(query)  # shape (1, dim)
        except Exception as e:
            # If embedding fails, return empty
            return []

        # vectorstore.search expects numpy array (1, dim)
        try:
            results = self.vectorstore.search(q_emb, top_k=self.top_k)
            return results or []
        except Exception:
            return []

    def _build_context(self, chunks: List[str], max_chars: int = 3000) -> str:
        """
        Combine retrieved chunks into a single context string.
        Truncate if too long (keeps most relevant first).
        """
        if not chunks:
            return ""
        combined = "\n\n---\n\n".join(chunks)
        if len(combined) <= max_chars:
            return combined
        # trim to max_chars while preserving start of each chunk
        out = ""
        for c in chunks:
            if len(out) + len(c) + 6 > max_chars:
                break
            out += c + "\n\n---\n\n"
        return out.strip()

    def query(self, user_question: str, chat_history: Optional[List[dict]] = None) -> str:
        """
        Main public method.
        - user_question: raw question string
        - chat_history: optional list of previous messages (dicts with 'role' and 'content')
        Returns: answer string
        """
        # 1) Re-write the query using history
        rewritten_query = self._rewrite_query(user_question, chat_history)

        # 2) Retrieve relevant chunks
        top_chunks = self._retrieve(rewritten_query)

        # 3) If no chunks found, respond accordingly (and optionally provide a general answer)
        if not top_chunks:
            # Ask DeepSeek for a general answer (no context)
            fallback_prompt = (
                "No relevant documents were found. Answer the user's question using your general knowledge:\n\n"
                f"Question: {user_question}\n\nAnswer:"
            )
            try:
                fallback_answer = query_deepseek(fallback_prompt)
                return fallback_answer
            except Exception as e:
                return f"Error: failed to call LLM: {e}"

        # 4) Build context and final prompt
        context = self._build_context(top_chunks, max_chars=3000)
        answer_prompt = _ANSWER_PROMPT_TEMPLATE.format(context=context, user_question=user_question)

        # 5) Call DeepSeek for final answer (with context)
        try:
            answer = query_deepseek(answer_prompt)
            if answer and answer.strip():
                return answer.strip()
            # If empty, try a short fallback reply
            fallback = query_deepseek(f"Provide a short answer to: {user_question}")
            return fallback or "I couldn't generate an answer."
        except Exception as e:
            return f"Error calling DeepSeek: {e}"
