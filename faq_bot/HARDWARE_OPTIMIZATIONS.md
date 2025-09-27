# Hardware Optimizations for FAQ Bot

This document explains all the optimizations made to the FAQ Bot to run efficiently on your hardware:
- **CPU**: Intel i5-4570
- **GPU**: GTX 1660Ti
- **RAM**: 16GB
- **Storage**: 100GB

## Configuration Optimizations

### Environment Variables (.env)
The following environment variables have been optimized:

- `BATCH_SIZE=16` - Optimized for the i5-4570 CPU to balance performance and memory usage
- `CACHE_SIZE=500` - Optimized for 16GB RAM to maintain responsive caching without memory pressure
- `EMBEDDING_CACHE_SIZE=1000` - Larger cache for embeddings to reduce repeated model processing
- `SIMILARITY_THRESHOLD=0.73` - Slightly increased for better accuracy with the Russian/English model

### Network Settings
- `REQUEST_TIMEOUT=30` - Balanced timeout for stable connections
- `MAX_RETRIES=3` - Reasonable retry count to handle network issues without overloading

## Performance Optimizations

### Model Processing
1. **Batch Size**: Set to 16 to optimize for the i5-4570's 4 cores with hyperthreading
2. **Cache Management**: 
   - Query cache size: 500 entries
   - Embedding cache size: 1000 entries
   - TTL: 30 minutes for queries, 1 hour for embeddings

### Memory Management
1. **Garbage Collection**: Automatic memory optimization every 5 minutes
2. **Cache Eviction**: LRU (Least Recently Used) policy to maintain optimal memory usage
3. **Connection Pooling**: Limited to 20 concurrent database connections

### Database Optimizations
1. **SQLite Settings**: 
   - Timeout: 30 seconds
   - Thread safety: Disabled for better performance on single-threaded operations
2. **Indexing**: Added indexes on frequently queried columns
3. **Connection Pool**: Async connection pool with semaphore limiting

## File Structure Optimizations

### Directory Organization
1. **cache/**: Contains all temporary files (embeddings, logs)
2. **data/**: Contains persistent data (FAQ, database)
3. **files/**: Contains static files for distribution
4. **src/**: Contains all source code

### Cleanup Procedures
1. **3_Clean_All.bat**: Comprehensive cleanup script that removes:
   - Cached embeddings and indexes
   - Log files
   - Python cache directories
   - Temporary files

## Hardware-Specific Recommendations

### CPU (i5-4570)
- **Batch Processing**: Limited to 16 items to prevent CPU overload
- **Threading**: Single-threaded processing for FAISS operations to avoid context switching overhead
- **Memory Usage**: Capped cache sizes to prevent swapping

### GPU (GTX 1660Ti)
- **Model Selection**: Using CPU-based FAISS since the model is relatively small
- **Memory Allocation**: No dedicated GPU memory allocation needed for this model size

### RAM (16GB)
- **Cache Sizes**: Balanced to use approximately 2-3GB of RAM for caching
- **Model Loading**: Single model instance to prevent memory duplication
- **Garbage Collection**: Automatic cleanup to prevent memory leaks

### Storage (100GB)
- **Cache Management**: Automatic cleanup of old cache entries
- **Log Rotation**: Periodic log cleanup to prevent disk space issues
- **Embedding Storage**: Efficient binary format (pickle) for embeddings

## Performance Monitoring

### Built-in Metrics
1. **Response Time Tracking**: Average response time calculation
2. **Cache Hit Rate**: Monitoring cache efficiency
3. **Memory Usage**: Real-time memory monitoring
4. **CPU Usage**: Process CPU utilization tracking

### Health Checks
1. **Periodic Uptime Logging**: Every 30 minutes
2. **Connection Health**: Every 5 minutes
3. **Memory Optimization**: Every 5 minutes or on demand

## Batch Script Optimizations

### 0_Setup.bat
- Enhanced error handling
- Better virtual environment management
- Improved dependency installation

### 1_Start_Bot.bat
- Enhanced process checking
- Better error reporting
- Automatic dependency verification

### 3_Clean_All.bat
- Comprehensive cleanup procedures
- Extended file type removal
- Python script integration for advanced cleanup

## Training Optimizations

### Model Training
- **Batch Size**: 16 for optimal CPU utilization
- **Progress Tracking**: Disabled progress bar for cleaner logs
- **Error Handling**: Comprehensive error handling with detailed logging

## Security Optimizations

### Input Validation
- Enhanced text sanitization
- Improved query validation
- Better file path validation

### Rate Limiting
- Per-minute and per-hour rate limiting
- Automatic user blocking for suspicious activity
- Configurable limits in environment variables

## Conclusion

These optimizations ensure that the FAQ Bot will run efficiently on your hardware while maintaining high performance and reliability. The settings have been carefully balanced to provide optimal performance without overloading any single component of your system.