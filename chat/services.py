"""
Chat and RAG query services with Google Gemini integration.
"""
from typing import List, Dict, Optional
from django.conf import settings
from faiss_manager.services import faiss_service
from .models import Conversation, Message
import logging
import os

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling RAG-based chat queries."""
    
    def __init__(self):
        """Initialize service (Gemini client created on demand)."""
        self._client = None
        self.model = getattr(settings, 'LLM_MODEL', 'gemini-2.5-flash')
    
    @property
    def client(self):
        """Lazy-load Google Gemini client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                # Try to get API key from settings first, then from environment
                api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
                if not api_key:
                    logger.warning("GEMINI_API_KEY not set. Gemini features will not work.")
                    return None
                genai.configure(api_key=api_key)
                self._client = genai.GenerativeModel(self.model)
                logger.info(f"Google Gemini client initialized successfully with model: {self.model}")
            except ImportError as e:
                logger.error(f"Error importing google.generativeai: {str(e)}. Run: pip install google-generativeai")
                return None
            except Exception as e:
                logger.error(f"Error initializing Gemini client: {str(e)}")
                return None
        return self._client
    
    def process_query(
        self,
        question: str,
        conversation_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Dict:
        """
        Process a RAG query: search documents, build context, query LLM.
        
        Args:
            question: User's question
            conversation_id: Optional conversation ID for context
            document_ids: Optional list of document IDs to search within
            top_k: Number of context chunks to retrieve
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        try:
            # Step 1: Search for relevant chunks using FAISS
            logger.info(f"Searching for top {top_k} relevant chunks...")
            search_results = faiss_service.search(
                query=question,
                top_k=top_k,
                document_ids=document_ids
            )
            
            if not search_results:
                return {
                    'answer': "I couldn't find any relevant information in the documents to answer your question.",
                    'sources': [],
                    'conversation_id': conversation_id
                }
            
            # Step 2: Build context from retrieved chunks
            context = self._build_context(search_results)
            
            # Step 3: Get conversation history if provided
            conversation_history = []
            if conversation_id:
                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                    messages = Message.objects.filter(
                        conversation=conversation
                    ).order_by('timestamp')[:10]  # Last 10 messages
                    
                    conversation_history = [
                        {
                            'role': msg.role,
                            'content': msg.content
                        }
                        for msg in messages
                    ]
                except Conversation.DoesNotExist:
                    logger.warning(f"Conversation {conversation_id} not found")
            
            # Step 4: Query Google Gemini with context and conversation history
            logger.info("Querying Google Gemini...")
            answer = self._query_llm(question, context, conversation_history)
            
            # Step 5: Format sources
            sources = [
                {
                    'chunk_id': result['chunk_id'],
                    'document_id': result['document_id'],
                    'document_name': result['document_name'],
                    'page_number': result['page_number'],
                    'text': result['text'][:200] + '...' if len(result['text']) > 200 else result['text'],
                    'similarity_score': result['similarity_score']
                }
                for result in search_results
            ]
            
            return {
                'answer': answer,
                'sources': sources,
                'conversation_id': conversation_id,
                'chunks_retrieved': len(search_results)
            }
            
        except Exception as e:
            logger.error(f"Error processing RAG query: {str(e)}")
            raise
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """
        Build context string from search results.
        
        Args:
            search_results: List of search result dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            context_part = f"""
[Document: {result['document_name']}, Page: {result['page_number']}]
{result['text']}
"""
            context_parts.append(context_part.strip())
        
        return "\n\n---\n\n".join(context_parts)
    
    def _query_llm(
        self,
        question: str,
        context: str,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Query Google Gemini LLM with context and question.
        
        Args:
            question: User's question
            context: Context from retrieved documents
            conversation_history: Previous conversation messages
            
        Returns:
            LLM's answer
        """
        try:
            # Check if Gemini client is available
            if self.client is None:
                raise Exception("Gemini client not initialized. Please check GEMINI_API_KEY in .env file and run: pip install google-generativeai")
            
            # Build system instructions
            system_instruction = """You are a helpful AI assistant that answers questions based on the provided document context.

Rules:
1. Answer questions using ONLY the information from the provided context
2. If the context doesn't contain enough information, say so clearly
3. Cite the document name and page number when referencing information
4. Be concise but comprehensive
5. If asked about something not in the context, politely explain you can only answer based on the provided documents"""
            
            # Build prompt with context and conversation history
            prompt_parts = []
            
            # Add system instruction
            prompt_parts.append(system_instruction)
            prompt_parts.append("\n\n---\n\n")
            
            # Add conversation history if available
            if conversation_history:
                prompt_parts.append("Previous conversation:\n")
                for msg in conversation_history[-5:]:  # Last 5 messages
                    role_label = "User" if msg['role'] == 'user' else "Assistant"
                    prompt_parts.append(f"{role_label}: {msg['content']}\n")
                prompt_parts.append("\n---\n\n")
            
            # Add context
            prompt_parts.append(f"Context from documents:\n\n{context}\n\n---\n\n")
            
            # Add current question
            prompt_parts.append(f"Question: {question}\n\nPlease answer the question based on the context provided above.")
            
            full_prompt = "".join(prompt_parts)
            
            # Call Gemini API
            response = self.client.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 1500,
                }
            )
            
            answer = response.text
            logger.info("Successfully received response from Google Gemini")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error querying Gemini: {str(e)}")
            raise
    
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        source_chunks: List[str] = None
    ) -> Message:
        """
        Save a message to the conversation.
        
        Args:
            conversation_id: Conversation UUID
            role: 'user' or 'assistant'
            content: Message content
            source_chunks: List of chunk IDs used for answer
            
        Returns:
            Created Message instance
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            
            message = Message.objects.create(
                conversation=conversation,
                role=role,
                content=content,
                source_chunks=source_chunks or []
            )
            
            return message
            
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {conversation_id} not found")
            raise


# Singleton instance
chat_service = ChatService()

