import json
import faiss
import pickle
import os
import logging
import time
from pathlib import Path
from typing import List, Tuple, Optional, Union, Dict, Any
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
from config import config
from performance_manager import performance_manager, timing_decorator

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Data class for search results."""
    similarity: float
    index: int
    query: str
    response: str
    resources: Optional[List[Dict[str, Any]]] = None


@dataclass
class LoadingStats:
    """Data class for loading statistics."""
    total_items: int
    valid_queries: int
    total_variations: int
    loading_time: float
    embedding_time: float


class FAQLoaderError(Exception):
    """Custom exception for FAQ loader errors."""
    pass


class FAQLoader:
    """Enhanced FAQ loader with improved performance, error handling, and type safety."""
    
    def __init__(
        self,
        faq_file: Union[str, Path, None] = None,
        embeddings_file: Union[str, Path, None] = None,
        index_file: Union[str, Path, None] = None,
        model_name: str = config.ml.model_name
    ):
        """Initialize FAQ loader with proper path handling and validation.
        
        Args:
            faq_file: Path to FAQ JSON file
            embeddings_file: Path to embeddings pickle file
            index_file: Path to FAISS index file
            model_name: Name of the sentence transformer model
        """
        # Set up file paths
        self.faq_file = Path(faq_file) if faq_file else Path(config.FAQ_FILE)
        self.embeddings_file = Path(embeddings_file) if embeddings_file else Path(config.EMBEDDINGS_FILE)
        self.index_file = Path(index_file) if index_file else Path(config.INDEX_FILE)
        
        # Model configuration
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        
        # Data storage
        self.faq: Optional[List[Dict[str, Any]]] = None
        self.index: Optional[faiss.Index] = None
        self.faq_queries: Optional[List[str]] = None
        self.original_indices: List[int] = []
        
        # Performance tracking
        self.loading_stats: Optional[LoadingStats] = None
        self._model_loaded = False
        
        # Register with performance manager for tracking
        performance_manager.register_object(self)
        
        # Ensure cache directory exists
        self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"FAQ Loader initialized with model: {self.model_name}")

    @timing_decorator
    def _load_model(self) -> None:
        """Load the sentence transformer model with error handling and caching."""
        if self._model_loaded and self.model:
            return
            
        try:
            start_time = time.time()
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            
            self.model = SentenceTransformer(self.model_name)
            self._model_loaded = True
            
            load_time = time.time() - start_time
            performance_manager.metrics.embeddings_load_time = load_time
            logger.info(f"Model loaded successfully in {load_time:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise FAQLoaderError(f"Model loading failed: {e}") from e
    
    def _validate_faq_item(self, item: Dict[str, Any], index: int) -> bool:
        """Validate a single FAQ item.
        
        Args:
            item: FAQ item to validate
            index: Item index for error reporting
            
        Returns:
            bool: True if item is valid
        """
        if not isinstance(item, dict):
            logger.warning(f"FAQ item {index} is not a dictionary, skipping")
            return False
            
        if 'query' not in item:
            logger.warning(f"FAQ item {index} missing 'query' field, skipping")
            return False
            
        if not item['query'] or not isinstance(item['query'], str):
            logger.warning(f"FAQ item {index} has invalid query, skipping")
            return False
            
        if 'response' not in item:
            logger.warning(f"FAQ item {index} missing 'response' field, skipping")
            return False
            
        return True
    
    def load_faq(self) -> LoadingStats:
        """Load FAQ data with comprehensive validation and error handling.
        
        Returns:
            LoadingStats: Statistics about the loading process
        """
        start_time = time.time()
        
        try:
            if not self.faq_file.exists():
                raise FAQLoaderError(f"FAQ file not found: {self.faq_file}")
            
            logger.info(f"Loading FAQ from: {self.faq_file}")
            
            with open(self.faq_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            if not isinstance(raw_data, list):
                raise FAQLoaderError("FAQ data should be a list of items")
                
            if not raw_data:
                raise FAQLoaderError("FAQ data is empty")
            
            # Process and validate FAQ items
            self.faq = []
            self.faq_queries = []
            self.original_indices = []
            valid_items = 0
            total_variations = 0
            
            for idx, item in enumerate(raw_data):
                if not self._validate_faq_item(item, idx):
                    continue
                
                # Add validated item
                self.faq.append(item)
                valid_items += 1
                
                # Process main query
                main_query = str(item['query']).strip()
                if main_query:
                    self.faq_queries.append(main_query)
                    self.original_indices.append(len(self.faq) - 1)
                
                # Process variations
                variations = item.get('variations', [])
                if isinstance(variations, list):
                    for variation in variations:
                        if variation and isinstance(variation, str):
                            variation_text = str(variation).strip()
                            if variation_text:
                                self.faq_queries.append(variation_text)
                                self.original_indices.append(len(self.faq) - 1)
                                total_variations += 1
            
            if not self.faq_queries:
                raise FAQLoaderError("No valid FAQ queries found after processing")
            
            loading_time = time.time() - start_time
            
            self.loading_stats = LoadingStats(
                total_items=len(raw_data),
                valid_queries=valid_items,
                total_variations=total_variations,
                loading_time=loading_time,
                embedding_time=0.0  # Will be set during embedding creation
            )
            
            logger.info(
                f"FAQ loaded successfully: {valid_items} items, "
                f"{len(self.faq_queries)} total queries (including variations) "
                f"in {loading_time:.2f} seconds"
            )
            
            return self.loading_stats
            
        except json.JSONDecodeError as e:
            raise FAQLoaderError(f"Invalid JSON in FAQ file: {e}") from e
        except Exception as e:
            logger.error(f"Error loading FAQ: {e}")
            raise FAQLoaderError(f"FAQ loading failed: {e}") from e

    def create_embeddings(self, force_rebuild: bool = False) -> Tuple[List[Dict[str, Any]], faiss.Index]:
        """Create or load embeddings with improved caching and error handling.
        
        Args:
            force_rebuild: Force rebuilding embeddings even if cache exists
            
        Returns:
            Tuple[List[Dict], faiss.Index]: FAQ data and FAISS index
            
        Raises:
            FAQLoaderError: If embeddings creation fails
        """
        embedding_start_time = time.time()
        
        if not self.faq_queries:
            raise FAQLoaderError("FAQ queries not loaded. Call load_faq() first.")
        
        if not self.faq:
            raise FAQLoaderError("FAQ data not loaded. Call load_faq() first.")
        
        try:
            # Load model if not already loaded
            self._load_model()
            
            if not self.model:
                raise FAQLoaderError("Model failed to load")
            
            # Check if we can use cached embeddings
            cache_valid = (
                not force_rebuild and
                self.embeddings_file.exists() and
                self.index_file.exists()
            )
            
            if cache_valid:
                try:
                    logger.info("Loading cached embeddings and index...")
                    
                    with open(self.embeddings_file, 'rb') as f:
                        faq_embeddings = pickle.load(f)
                    
                    self.index = faiss.read_index(str(self.index_file))
                    
                    # Validate cache
                    if len(faq_embeddings) != len(self.faq_queries):
                        logger.warning("Cache size mismatch, rebuilding embeddings")
                        cache_valid = False
                    else:
                        embedding_time = time.time() - embedding_start_time
                        if self.loading_stats:
                            self.loading_stats.embedding_time = embedding_time
                        
                        if self.index is None:
                            raise FAQLoaderError("Failed to load cached index")
                            
                        logger.info(f"Cached embeddings loaded in {embedding_time:.2f} seconds")
                        return self.faq, self.index
                        
                except Exception as e:
                    logger.warning(f"Failed to load cached embeddings: {e}, rebuilding")
                    cache_valid = False
            
            # Create new embeddings
            logger.info("Creating new embeddings and index...")
            
            # Validate queries before encoding
            valid_queries = [str(query).strip() for query in self.faq_queries if query and str(query).strip()]
            
            if not valid_queries:
                raise FAQLoaderError("No valid queries to encode")
            
            if len(valid_queries) != len(self.faq_queries):
                logger.warning(f"Filtered {len(self.faq_queries) - len(valid_queries)} invalid queries")
                self.faq_queries = valid_queries
            
            # Create embeddings with progress logging
            batch_size = min(32, len(valid_queries))  # Optimize batch size
            
            logger.info(f"Encoding {len(valid_queries)} queries with batch size {batch_size}")
            
            faq_embeddings = self.model.encode(
                valid_queries,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=batch_size,
                show_progress_bar=False  # We'll log progress ourselves
            )
            
            # Validate embeddings
            if faq_embeddings is None or len(faq_embeddings) == 0:
                raise FAQLoaderError("Failed to create embeddings")
            
            if not isinstance(faq_embeddings, np.ndarray):
                faq_embeddings = np.array(faq_embeddings)
            
            faq_embeddings = faq_embeddings.astype(np.float32)
            
            # Ensure embeddings are 2D
            if len(faq_embeddings.shape) == 1:
                faq_embeddings = faq_embeddings.reshape(1, -1)
            
            logger.info(f"Created embeddings with shape: {faq_embeddings.shape}")
            
            # Create FAISS index
            dimension = faq_embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors
            
            # Add embeddings to index with proper error handling
            try:
                # Add embeddings to FAISS index
                # FAISS add() method: add(x)
                self.index.add(faq_embeddings)
            except Exception as e:
                logger.error(f"Failed to add embeddings to FAISS index: {e}")
                raise FAQLoaderError(f"FAISS index creation failed: {e}") from e
            
            # Save to cache
            try:
                with open(self.embeddings_file, 'wb') as f:
                    pickle.dump(faq_embeddings, f, protocol=pickle.HIGHEST_PROTOCOL)
                
                faiss.write_index(self.index, str(self.index_file))
                
                logger.info(f"Embeddings cached to {self.embeddings_file}")
                logger.info(f"Index cached to {self.index_file}")
                
            except Exception as e:
                logger.warning(f"Failed to cache embeddings: {e}")
                # Continue without caching
            
            embedding_time = time.time() - embedding_start_time
            if self.loading_stats:
                self.loading_stats.embedding_time = embedding_time
            
            logger.info(f"Embeddings created successfully in {embedding_time:.2f} seconds")
            
            return self.faq, self.index
            
        except Exception as e:
            logger.error(f"Embeddings creation error: {e}")
            raise FAQLoaderError(f"Embeddings creation failed: {e}") from e

    @timing_decorator
    def search(
        self, 
        query: str, 
        k: int = 3, 
        threshold: float = config.ml.similarity_threshold
    ) -> Tuple[Optional[List[float]], Optional[List[int]]]:
        """Search for similar FAQ entries with enhanced validation, performance, and caching.
        
        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            Tuple[Optional[List[float]], Optional[List[int]]]: Similarities and indices
        """
        start_time = time.time()
        
        try:
            # Validate inputs
            if not query or not isinstance(query, str):
                logger.error("Query must be a non-empty string")
                return None, None
            
            query = query.strip()
            if not query:
                logger.error("Query cannot be empty after stripping")
                return None, None
            
            # Check cache first
            cache_key = f"{query}:{k}:{threshold}"
            cached_result = performance_manager.get_cached_query_result(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_result
            
            if not self.index:
                logger.error("Index not initialized. Call create_embeddings() first.")
                return None, None
                
            if not self.faq:
                logger.error("FAQ data not loaded. Call load_faq() first.")
                return None, None
            
            # Load model if needed
            self._load_model()
            
            if not self.model:
                logger.error("Model not loaded")
                return None, None
            
            # Validate threshold
            if not (0.0 <= threshold <= 1.0):
                logger.warning(f"Invalid threshold {threshold}, using default")
                threshold = config.ml.similarity_threshold
            
            # Check for cached embedding
            cached_embedding = performance_manager.get_cached_embedding(query)
            
            if cached_embedding is not None:
                query_embedding = cached_embedding
                logger.debug(f"Using cached embedding for: {query[:50]}...")
            else:
                # Create query embedding with error handling
                try:
                    query_embedding = self.model.encode(
                        [query],
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=False
                    )
                    
                    # Cache the embedding
                    performance_manager.cache_embedding(query, query_embedding)
                    
                except Exception as e:
                    logger.error(f"Failed to encode query: {e}")
                    return None, None
            
            # Validate query embedding
            if query_embedding is None:
                logger.error("Failed to create query embedding")
                return None, None
            
            # Ensure correct format for FAISS
            if not isinstance(query_embedding, np.ndarray):
                query_embedding = np.array(query_embedding)
            
            query_embedding = query_embedding.astype(np.float32)
            
            # Ensure query embedding is 2D
            if len(query_embedding.shape) == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            # Perform search with comprehensive error handling
            try:
                search_k = min(k, self.index.ntotal)
                # FAISS search method: search(x, k) returns (distances, indices)
                distances, indices = self.index.search(query_embedding, search_k)  # type: ignore
            except Exception as e:
                logger.error(f"Error during FAISS search: {e}")
                return None, None
            
            # Validate search results
            if distances is None or indices is None:
                logger.warning(f"Search returned None results for query: {query}")
                return None, None
            
            if len(distances) == 0 or len(distances[0]) == 0:
                logger.info(f"No results found for query: {query}")
                result = (None, None)
                performance_manager.cache_query_result(cache_key, result)
                return result
            
            # Filter and process results
            filtered_results = []
            max_similarity = 0.0
            
            for i in range(min(k, len(distances[0]))):
                similarity = float(distances[0][i])
                idx = int(indices[0][i])
                
                max_similarity = max(max_similarity, similarity)
                
                # Validate index bounds
                if 0 <= idx < len(self.original_indices):
                    original_idx = self.original_indices[idx]
                    
                    # Validate original index bounds
                    if 0 <= original_idx < len(self.faq):
                        if similarity >= threshold:
                            filtered_results.append((similarity, original_idx))
                    else:
                        logger.warning(f"Invalid original index: {original_idx}")
                else:
                    logger.warning(f"Invalid search index: {idx}")
            
            # Prepare result
            if filtered_results:
                # Sort by similarity (descending)
                filtered_results.sort(key=lambda x: x[0], reverse=True)
                best_similarity, best_idx = filtered_results[0]
                
                result = ([best_similarity], [best_idx])
                
                logger.info(
                    f"Found match for '{query[:50]}...' with similarity {best_similarity:.3f}"
                )
            else:
                # No results meet threshold
                result = (None, None)
                
                logger.info(
                    f"No matches for '{query[:50]}...' "
                    f"(max similarity: {max_similarity:.3f}, threshold: {threshold:.3f})"
                )
            
            # Cache the result
            performance_manager.cache_query_result(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Search error for query '{query[:50]}...': {e}")
            return None, None
        finally:
            # Track performance
            response_time = time.time() - start_time
            performance_manager.track_request(response_time)
    
    def search_detailed(
        self, 
        query: str, 
        k: int = 3, 
        threshold: float = config.ml.similarity_threshold
    ) -> List[SearchResult]:
        """Search with detailed results including FAQ content.
        
        Args:
            query: Search query text
            k: Number of results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List[SearchResult]: Detailed search results
        """
        if not self.faq:
            logger.error("FAQ data not loaded")
            return []
            
        similarities, indices = self.search(query, k, threshold)
        
        if not similarities or not indices:
            return []
        
        results = []
        for similarity, idx in zip(similarities, indices):
            if 0 <= idx < len(self.faq):
                faq_item = self.faq[idx]
                result = SearchResult(
                    similarity=similarity,
                    index=idx,
                    query=faq_item.get('query', ''),
                    response=faq_item.get('response', ''),
                    resources=faq_item.get('resources')
                )
                results.append(result)
        
        return results
    
    def get_stats(self) -> Optional[LoadingStats]:
        """Get loading and performance statistics.
        
        Returns:
            Optional[LoadingStats]: Statistics if available
        """
        return self.loading_stats
    
    def is_ready(self) -> bool:
        """Check if the FAQ loader is ready for searches.
        
        Returns:
            bool: True if ready for searches
        """
        return (
            self.faq is not None and
            self.faq_queries is not None and
            self.index is not None and
            self._model_loaded and
            self.model is not None
        )
    
    def rebuild_index(self) -> bool:
        """Rebuild the entire index from scratch.
        
        Returns:
            bool: True if rebuild successful
        """
        try:
            logger.info("Rebuilding FAQ index from scratch")
            
            # Clear cache files
            for cache_file in [self.embeddings_file, self.index_file]:
                if cache_file.exists():
                    cache_file.unlink()
                    logger.info(f"Removed cache file: {cache_file}")
            
            # Reload everything
            self.load_faq()
            self.create_embeddings(force_rebuild=True)
            
            logger.info("Index rebuilt successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False

# Explicitly export FAQLoader for static analysis tools
__all__ = ['FAQLoader', 'FAQLoaderError', 'SearchResult', 'LoadingStats']
