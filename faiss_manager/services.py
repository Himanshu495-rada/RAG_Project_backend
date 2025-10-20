"""
FAISS vector database management and embedding generation services.
"""
import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from django.conf import settings
from documents.models import Chunk
from .models import FAISSIndex
import logging

logger = logging.getLogger(__name__)


class FAISSService:
    """Service for managing FAISS indexes and embeddings."""
    
    _instance = None
    _model = None
    _index = None
    _chunk_id_map = None  # Maps FAISS vector ID to Chunk database ID
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance."""
        if cls._instance is None:
            cls._instance = super(FAISSService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the FAISS service."""
        if FAISSService._model is None:
            self.load_embedding_model()
    
    def load_embedding_model(self):
        """Load the sentence transformer model for embeddings."""
        try:
            logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
            FAISSService._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding vector for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array of embedding vector (384 dimensions)
        """
        if FAISSService._model is None:
            self.load_embedding_model()
        
        try:
            embedding = FAISSService._model.encode([text])[0]
            return embedding.astype('float32')
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch processing).
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Numpy array of embeddings (n_texts x 384)
        """
        if FAISSService._model is None:
            self.load_embedding_model()
        
        try:
            embeddings = FAISSService._model.encode(texts, show_progress_bar=True)
            return embeddings.astype('float32')
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def build_index(self, document_ids: Optional[List[str]] = None) -> bool:
        """
        Build or rebuild FAISS index from chunks in database.
        
        Args:
            document_ids: Optional list of document IDs to index. If None, index all.
            
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Building FAISS index...")
            
            # Get chunks from database
            if document_ids:
                chunks = Chunk.objects.filter(document_id__in=document_ids).order_by('id')
            else:
                chunks = Chunk.objects.all().order_by('id')
            
            if not chunks.exists():
                logger.warning("No chunks found to index")
                return False
            
            # Extract texts and IDs
            chunk_texts = [chunk.chunk_text for chunk in chunks]
            chunk_ids = [str(chunk.id) for chunk in chunks]
            
            logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
            
            # Generate embeddings
            embeddings = self.generate_embeddings_batch(chunk_texts)
            
            # Create FAISS index
            dimension = embeddings.shape[1]  # Should be 384
            FAISSService._index = faiss.IndexFlatL2(dimension)
            
            # Add embeddings to index
            FAISSService._index.add(embeddings)
            
            # Create mapping from FAISS vector ID to Chunk database ID
            FAISSService._chunk_id_map = {i: chunk_ids[i] for i in range(len(chunk_ids))}
            
            # Save index to disk
            self.save_index()
            
            # Update FAISSIndex model
            index_record, created = FAISSIndex.objects.get_or_create(
                index_name='default',
                defaults={
                    'dimension': dimension,
                    'total_vectors': len(chunk_ids),
                    'index_file_path': str(self._get_index_path())
                }
            )
            
            if not created:
                index_record.total_vectors = len(chunk_ids)
                index_record.last_updated = None  # Will auto-update
                index_record.save()
            
            logger.info(f"FAISS index built successfully with {len(chunk_ids)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error building FAISS index: {str(e)}")
            raise
    
    def search(self, query: str, top_k: int = 5, document_ids: Optional[List[str]] = None) -> List[Dict]:
        """
        Search for similar chunks using FAISS.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            document_ids: Optional list of document IDs to filter results
            
        Returns:
            List of dictionaries with chunk info and similarity scores
        """
        try:
            # Load index if not already loaded
            if FAISSService._index is None or FAISSService._chunk_id_map is None:
                logger.info("Loading FAISS index from disk...")
                self.load_index()
            
            if FAISSService._index is None:
                logger.warning("No FAISS index available")
                return []
            
            if FAISSService._chunk_id_map is None or len(FAISSService._chunk_id_map) == 0:
                logger.warning("Chunk ID mapping is empty")
                return []
            
            logger.info(f"FAISS index has {FAISSService._index.ntotal} vectors, mapping has {len(FAISSService._chunk_id_map)} entries")
            logger.info(f"Document filter: {document_ids} (type: {type(document_ids)})")
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            query_embedding = np.array([query_embedding])
            
            # Search FAISS index
            distances, indices = FAISSService._index.search(query_embedding, min(top_k * 3, FAISSService._index.ntotal))
            
            logger.info(f"FAISS search returned {len(indices[0])} results, distances: {distances[0][:5]}")
            logger.info(f"FAISS indices: {indices[0][:5]}")
            logger.info(f"Sample chunk_id_map entries: {list(FAISSService._chunk_id_map.items())[:3]}")
            
            # Convert results to chunk info
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for empty results
                    continue
                
                logger.debug(f"Looking for index {idx} (type: {type(idx)}) in mapping")
                
                # Get chunk ID from mapping
                chunk_id = FAISSService._chunk_id_map.get(int(idx))
                if not chunk_id:
                    logger.warning(f"No chunk ID found for FAISS index {idx}. Mapping keys type: {type(list(FAISSService._chunk_id_map.keys())[0]) if FAISSService._chunk_id_map else 'empty'}")
                    continue
                
                logger.info(f"Found chunk_id {chunk_id} for index {idx}")
                
                # Get chunk from database
                try:
                    chunk = Chunk.objects.select_related('document').get(id=chunk_id)
                    
                    # Filter by document if specified (only if document_ids is not None and not empty)
                    if document_ids is not None and len(document_ids) > 0:
                        # Convert both to strings for comparison
                        chunk_doc_id = str(chunk.document_id)
                        filter_ids = [str(doc_id) for doc_id in document_ids]
                        
                        if chunk_doc_id not in filter_ids:
                            logger.info(f"Filtered out chunk from document {chunk_doc_id} (not in {filter_ids})")
                            continue
                    
                    # Calculate similarity score (convert L2 distance to similarity)
                    similarity = 1 / (1 + float(distance))
                    
                    results.append({
                        'chunk_id': str(chunk.id),
                        'document_id': str(chunk.document_id),
                        'document_name': chunk.document.original_filename,
                        'text': chunk.chunk_text,
                        'page_number': chunk.page_number,
                        'similarity_score': similarity,
                        'distance': float(distance)
                    })
                    
                    # Stop if we have enough results
                    if len(results) >= top_k:
                        break
                        
                except Chunk.DoesNotExist:
                    logger.warning(f"Chunk {chunk_id} not found in database")
                    continue
            
            logger.info(f"Found {len(results)} results for query")
            return results
            
        except Exception as e:
            logger.error(f"Error searching FAISS index: {str(e)}")
            raise
    
    def save_index(self):
        """Save FAISS index and chunk mapping to disk."""
        try:
            index_path = self._get_index_path()
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(FAISSService._index, str(index_path))
            
            # Save chunk ID mapping
            mapping_path = index_path.parent / 'chunk_mapping.pkl'
            with open(mapping_path, 'wb') as f:
                pickle.dump(FAISSService._chunk_id_map, f)
            
            logger.info(f"FAISS index saved to {index_path}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS index: {str(e)}")
            raise
    
    def load_index(self):
        """Load FAISS index and chunk mapping from disk."""
        try:
            index_path = self._get_index_path()
            
            if not index_path.exists():
                logger.warning(f"FAISS index file not found at {index_path}")
                return False
            
            # Load FAISS index
            FAISSService._index = faiss.read_index(str(index_path))
            
            # Load chunk ID mapping
            mapping_path = index_path.parent / 'chunk_mapping.pkl'
            if mapping_path.exists():
                with open(mapping_path, 'rb') as f:
                    FAISSService._chunk_id_map = pickle.load(f)
            
            logger.info(f"FAISS index loaded from {index_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading FAISS index: {str(e)}")
            return False
    
    def _get_index_path(self) -> Path:
        """Get path to FAISS index file."""
        media_root = Path(settings.MEDIA_ROOT)
        return media_root / 'faiss_indexes' / 'default_index.faiss'
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the current FAISS index."""
        if FAISSService._index is None:
            self.load_index()
        
        if FAISSService._index is None:
            return {
                'status': 'not_initialized',
                'total_vectors': 0,
                'dimension': 0
            }
        
        return {
            'status': 'active',
            'total_vectors': FAISSService._index.ntotal,
            'dimension': FAISSService._index.d,
            'total_chunks': Chunk.objects.count()
        }


# Singleton instance
faiss_service = FAISSService()

