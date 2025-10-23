"""
Enhanced GraphRAG Service with Multi-Query, Routing, and Evaluation
Implements: Query -> Multi-Query Generator -> Routing Agent -> Retrieval -> Evaluation Agent (with feedback loop)
"""

import os
import re
import asyncio
import requests
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage
from app.services.memgraph_service import get_memgraph_service
from app.services.graph_rag_v2 import GraphRAGService as HybridGraphRAG  # NEW: Hybrid FAISS+BM25+Memgraph
from app.services.entity_extractor import get_entity_extractor
from app.services.multi_query_generator import get_multi_query_generator
from app.services.evaluation_agent import get_evaluation_agent


class EnhancedGraphRAGService:
    """
    Enhanced GraphRAG with intelligent query processing pipeline:
    1. Multi-Query Generation - Generate query variations
    2. Routing Agent - Route to appropriate retrieval strategy
    3. Retrieval - Get relevant information
    4. Evaluation Agent - Assess quality and provide feedback
    5. Feedback Loop - Re-route if answer is insufficient
    """
    
    def __init__(self):
        print("🔧 Initializing Enhanced GraphRAG with Multi-Query and Evaluation...")
        self.graph = get_memgraph_service()
        self.hybrid_rag = HybridGraphRAG()  # NEW: Hybrid retrieval system (FAISS+BM25+Memgraph)
        self.entity_extractor = get_entity_extractor()
        self.multi_query_generator = get_multi_query_generator()
        self.evaluation_agent = get_evaluation_agent()
        
        # Use Ollama directly for better control
        self.ollama_url = "http://localhost:11434"
        Settings.llm = Ollama(
            model="llama3.2", 
            request_timeout=90.0,
            temperature=0.1,
            base_url=self.ollama_url
        )
        
        # Configuration
        self.max_retries = 2  # Maximum feedback loop iterations
        self.enable_multi_query = True  # Toggle multi-query generation
        self.enable_evaluation = True  # Toggle evaluation feedback
        
        print("✅ Enhanced GraphRAG initialized")
        print(f"   - Multi-Query Generation: {'Enabled' if self.enable_multi_query else 'Disabled'}")
        print(f"   - Evaluation Feedback: {'Enabled' if self.enable_evaluation else 'Disabled'}")
        print(f"   - Max Retries: {self.max_retries}")
    
    async def query(
        self, 
        query: str, 
        document_ids: Optional[List[str]] = None, 
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Main query processing pipeline with evaluation feedback loop.
        
        Args:
            query: User's question
            document_ids: Optional list of specific documents to search
            top_k: Number of chunks to retrieve
            conversation_history: Previous messages for context
            
        Returns:
            Dictionary with answer, citations, sources, and metadata
        """
        
        print(f"\n{'='*80}")
        print(f"🔍 NEW QUERY: {query[:80]}...")
        print(f"{'='*80}")
        
        # Get knowledge base stats
        stats = self.graph.get_stats()
        
        # Check if we have documents
        if stats['documents'] == 0 and not document_ids:
            return {
                "answer": "No documents uploaded yet. Please upload a document to get started.",
                "citations": [],
                "sources": [],
                "entities": [],
                "query": query,
                "strategy": "no_documents"
            }
        
        # STEP 1: Classify query type
        query_type = self._classify_query(query)
        print(f"📋 Query Type: {query_type}")
        
        # STEP 2: Determine routing strategy
        strategy = self._determine_query_strategy(query, stats)
        print(f"🎯 Routing Strategy: {strategy}")
        
        # Handle non-retrieval strategies
        if strategy == 'direct_reply':
            return self._handle_direct_reply(query, stats)
        
        if strategy == 'clarify':
            return self._handle_clarification(query, stats)
        
        # STEP 3: Multi-Query Generation (for retrieval strategy)
        # Skip multi-query for simple, direct questions to improve efficiency
        simple_question_patterns = [
            'what is', 'what are', 'how many', 'list', 'define', 'who is', 'when',
            'where', 'which', 'give me', 'show me', 'tell me'
        ]
        is_simple_query = any(query.lower().startswith(pattern) for pattern in simple_question_patterns)
        
        if self.enable_multi_query and not is_simple_query:
            queries = self.multi_query_generator.generate_with_context(
                original_query=query,
                conversation_history=conversation_history,
                num_queries=2  # Generate 2 variations + original = 3 total
            )
        else:
            queries = [query]
            if is_simple_query:
                print(f"   ⚡ Skipping multi-query for direct question")
        
        # STEP 4: Retrieval with Evaluation Feedback Loop
        retry_count = 0
        best_answer = None
        best_evaluation = None
        
        while retry_count <= self.max_retries:
            print(f"\n🔄 Attempt {retry_count + 1}/{self.max_retries + 1}")
            
            # Retrieve information
            retrieval_result = await self._retrieve_with_multi_query(
                queries=queries,
                document_ids=document_ids,
                top_k=top_k,
                query_type=query_type
            )
            
            # STEP 5: Evaluate answer quality
            if self.enable_evaluation:
                evaluation = self.evaluation_agent.evaluate_answer(
                    query=query,
                    answer=retrieval_result["answer"],
                    retrieved_chunks=retrieval_result.get("retrieved_chunks", []),
                    sources=retrieval_result.get("sources", [])
                )
                
                # Store best answer
                if best_answer is None or evaluation["overall_score"] > best_evaluation["overall_score"]:
                    best_answer = retrieval_result
                    best_evaluation = evaluation
                
                # Check if answer is sufficient
                if evaluation["is_sufficient"]:
                    print(f"✅ Answer meets quality threshold")
                    break
                else:
                    print(f"⚠️  Answer quality insufficient, preparing retry...")
                    
                    # Get retry strategy
                    retry_strategy = self.evaluation_agent.get_retry_strategy(evaluation)
                    print(f"   Retry Strategy: {retry_strategy}")
                    
                    # Apply retry strategy for next iteration
                    if retry_strategy["expand_search"]:
                        top_k = retry_strategy["increase_top_k"]
                        print(f"   📈 Expanding search to top_{top_k}")
                    
                    if retry_strategy["refine_query"]:
                        # Generate more query variations
                        queries = self.multi_query_generator.generate_queries(query, num_queries=3)
                        print(f"   🔄 Refined queries: {len(queries)}")
            else:
                # No evaluation, just return result
                best_answer = retrieval_result
                break
            
            retry_count += 1
        
        # Add evaluation metadata to response
        if self.enable_evaluation and best_evaluation:
            best_answer["evaluation"] = {
                "overall_score": best_evaluation["overall_score"],
                "quality_score": best_evaluation["quality_score"],
                "completeness_score": best_evaluation["completeness_score"],
                "relevance_score": best_evaluation["relevance_score"],
                "attempts": retry_count + 1
            }
        
        return best_answer
    
    async def _retrieve_with_multi_query(
        self,
        queries: List[str],
        document_ids: Optional[List[str]],
        top_k: int,
        query_type: str
    ) -> Dict[str, Any]:
        """
        Retrieve information using multiple query variations and merge results.
        Now runs ALL queries through the full hybrid pipeline (FAISS + Memgraph + BM25).
        """
        
        print(f"🔎 Retrieving with {len(queries)} queries using HYBRID SYSTEM...")
        
        all_chunks = []
        seen_chunk_ids = set()
        
        # Run ALL queries through the complete hybrid pipeline
        for query_idx, query in enumerate(queries, start=1):
            print(f"\n🔍 Query {query_idx}/{len(queries)}: {query[:80]}...")
            
            # STAGE 1: FAISS semantic retrieval (top 20 candidates per query)
            print(f"   📊 Stage 1: FAISS semantic search...")
            faiss_chunks = []
            try:
                faiss_chunks = self.hybrid_rag.faiss.search(query, top_k=20, doc_ids=document_ids)
                print(f"   ✓ FAISS retrieved {len(faiss_chunks)} chunks")
            except Exception as e:
                print(f"   ⚠️ FAISS error: {e}")
            
            # STAGE 2: Memgraph relational retrieval (related nodes/chunks)
            print(f"   🕸️ Stage 2: Memgraph graph traversal...")
            memgraph_chunks = []
            try:
                memgraph_chunks = self.hybrid_rag._retrieve_with_graph_traversal(
                    query=query,
                    doc_ids=document_ids,
                    max_depth=2,
                    max_nodes=15
                )
                print(f"   ✓ Memgraph retrieved {len(memgraph_chunks)} chunks")
            except Exception as e:
                print(f"   ⚠️ Memgraph error: {e}")
            
            # STAGE 3: Merge and deduplicate (within this query)
            print(f"   🔀 Stage 3: Merging and deduplicating...")
            merged_chunks = self.hybrid_rag._merge_and_deduplicate(faiss_chunks, memgraph_chunks)
            print(f"   ✓ Merged to {len(merged_chunks)} unique chunks")
            
            # STAGE 3.5: SMART DOCUMENT FILTERING
            # Extract named entities from query and match to document filenames
            # This ensures queries about specific people/documents return relevant chunks
            filtered_chunks = self._apply_smart_document_filter(query, merged_chunks)
            if filtered_chunks and len(filtered_chunks) < len(merged_chunks):
                print(f"   🎯 Smart Filter: Filtered to {len(filtered_chunks)} relevant chunks based on query entities")
                merged_chunks = filtered_chunks
            
            # STAGE 4: BM25 reranking on (filtered) merged results
            if merged_chunks:
                print(f"   🎯 Stage 4: BM25 reranking...")
                reranked_chunks = self.hybrid_rag.faiss.rerank(query, merged_chunks, top_k=top_k * 2)
                print(f"   ✓ Reranked to top {len(reranked_chunks)} chunks")
                
                # Add to all_chunks with deduplication
                for chunk in reranked_chunks:
                    chunk_id = chunk.get('id', chunk.get('text', '')[:50])
                    if chunk_id not in seen_chunk_ids:
                        seen_chunk_ids.add(chunk_id)
                        all_chunks.append(chunk)
                        
            print(f"   ✅ Query {query_idx} complete: {len(all_chunks)} total unique chunks so far")
        
        print(f"\n✅ Total retrieved: {len(all_chunks)} unique chunks from {len(queries)} queries")
        
        if not all_chunks:
            return {
                "answer": "I couldn't find relevant information in the documents. Try rephrasing your question.",
                "citations": [],
                "sources": [],
                "entities": [],
                "retrieved_chunks": [],
                "query": queries[0],
                "strategy": "retrieve"
            }
        
        # FINAL STAGE: Re-rank all chunks using the original query for consistency
        print(f"   🎯 Final BM25 reranking using original query...")
        all_chunks = self.hybrid_rag.faiss.rerank(queries[0], all_chunks, top_k=top_k * 2)
        print(f"   ✓ Final result: {len(all_chunks)} top-ranked chunks")
        
        # Extract entities
        all_entities = self._extract_entities_from_chunks(all_chunks)
        
        # Build context
        context = self._build_context(all_chunks, all_entities, query_type)
        
        # Generate answer
        answer = await self._generate_answer(queries[0], context, query_type)
        
        # Format response with citations
        return {
            "answer": answer,
            "citations": self._format_citations(all_chunks),
            "sources": self._format_sources(all_chunks),
            "entities": all_entities,
            "retrieved_chunks": all_chunks,  # Include for evaluation
            "query": queries[0],
            "query_type": query_type,
            "strategy": "retrieve",
            "num_queries_used": len(queries)
        }
    
    def _extract_entities_from_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Extract entities from retrieved chunks"""
        all_entities = []
        doc_ids_in_chunks = list(set([
            chunk.get('doc_id') or chunk.get('source', '').split('/')[0] 
            for chunk in chunks 
            if chunk.get('doc_id') or chunk.get('source')
        ]))
        
        for doc_id in doc_ids_in_chunks:
            try:
                entities = self.graph.get_document_entities(doc_id)
                all_entities.extend(entities)
            except Exception as e:
                print(f"   Warning: Could not get entities for doc {doc_id}: {e}")
        
        # Deduplicate entities
        unique_entities = {}
        for entity in all_entities:
            key = (entity['name'], entity['type'])
            if key not in unique_entities:
                unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    def _build_context(
        self, 
        chunks: List[Dict], 
        entities: List[Dict], 
        query_type: str
    ) -> str:
        """Build context string from chunks and entities"""
        
        # Format chunks
        chunk_context = "\n\n".join([
            f"[{c.get('source', 'Unknown')}]: {c.get('text', '')}" 
            for c in chunks
        ])
        
        # Format entities
        entity_context = self._format_entity_context(entities) if entities else ""
        
        # Combine based on query type
        if query_type == 'entity' and entity_context:
            context = f"{entity_context}\n\n=== DOCUMENT EXCERPTS ===\n{chunk_context}"
        else:
            context = f"{chunk_context}\n\n{entity_context}" if entity_context else chunk_context
        
        # Limit context length (increased for better performance)
        MAX_CONTEXT_LENGTH = 12000
        if len(context) > MAX_CONTEXT_LENGTH:
            print(f"   ⚠️ Context truncated from {len(context)} to {MAX_CONTEXT_LENGTH} chars")
            context = context[:MAX_CONTEXT_LENGTH] + "\n\n[... truncated ...]"
        
        return context
    
    async def _generate_answer(self, query: str, context: str, query_type: str) -> str:
        """Generate answer using LLM"""
        
        print(f"   🤖 Generating answer...")
        
        # Use more context for better answers (increased from 3000 to 8000)
        max_context_chars = 8000
        
        # Create focused prompt with emphasis on timestamps for audio
        if query_type == 'summary':
            prompt = f"""Based on these document excerpts, provide a concise summary.

IMPORTANT: If the source is an audio file (.wav,.mp3,.mp4..etc..), include specific timestamps in your answer (e.g., "At 0:30, ..." or "Between 1:15-2:00, ...").

{context[:max_context_chars]}

Summary:"""
        else:
            prompt = f"""Context from documents:
{context[:max_context_chars]}

Question: {query}

IMPORTANT: If information comes from audio files (.wav), mention specific timestamps in your answer (e.g., "At 0:30, they mentioned..." or "Between 1:15-2:00, the speaker said...").

Provide a clear, accurate answer based on the context:"""
        
        try:
            answer = self._call_ollama_direct(prompt, max_tokens=600)
            print(f"   ✓ Generated {len(answer)} chars")
            return answer
        except Exception as e:
            print(f"   ❌ Generation failed: {e}")
            return f"Based on the documents:\n\n{context[:500]}..."
    
    def _format_citations(self, chunks: List[Dict]) -> List[Dict]:
        """Format chunks into citations with page numbers/timestamps"""
        citations = []
        for c in chunks:
            citation_data = {
                "text": c.get('text', ''),
                "source": c.get('source', 'Unknown'),
                "doc_id": c.get('doc_id', ''),
                "chunk_id": c.get('id', '')
            }
            
            # Add citation metadata if available (page numbers for PDFs, timestamps for audio)
            if 'citation' in c:
                citation_data['citation'] = c['citation']
            
            citations.append(citation_data)
        
        return citations
    
    def _format_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Format unique sources from chunks"""
        sources = list(set([c.get('source', 'Unknown') for c in chunks]))
        return [{"filename": src} for src in sources]
    
    def _format_entity_context(self, entities: List[Dict]) -> str:
        """Format entities into structured context"""
        if not entities:
            return ""
        
        # Group by type
        by_type = {}
        for entity in entities:
            etype = entity['type']
            if etype not in by_type:
                by_type[etype] = []
            by_type[etype].append(entity['name'])
        
        # Format
        lines = ["=== EXTRACTED ENTITIES ==="]
        for etype, names in sorted(by_type.items()):
            unique_names = list(set(names))[:10]  # Max 10 per type
            lines.append(f"{etype}: {', '.join(unique_names)}")
        
        return "\n".join(lines)
    
    def _classify_query(self, query: str) -> str:
        """Classify query type"""
        q_lower = query.lower().strip()
        
        # Check patterns
        if any(word in q_lower for word in ['list', 'show', 'what documents', 'which files', 'how many']):
            return 'document_list'
        
        if any(word in q_lower for word in ['summarize', 'summary', 'overview', 'key points']):
            return 'summary'
        
        if any(word in q_lower for word in ['who', 'what is', 'define', 'explain']):
            return 'factual'
        
        if any(word in q_lower for word in ['entities', 'people', 'organizations', 'dates', 'locations']):
            return 'entity'
        
        return 'general'
    
    def _determine_query_strategy(self, query: str, stats: Dict) -> str:
        """Determine routing strategy"""
        q_lower = query.lower().strip()
        
        # Direct reply patterns
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
        if any(q_lower.startswith(g) for g in greetings):
            return 'direct_reply'
        
        acknowledgments = ['thanks', 'thank you', 'ok', 'okay', 'bye', 'goodbye']
        if q_lower in acknowledgments:
            return 'direct_reply'
        
        meta_questions = ['what can you do', 'how do you work', 'help', 'what are you']
        if any(m in q_lower for m in meta_questions):
            return 'direct_reply'
        
        # Clarification needed
        vague_terms = ['it', 'that', 'this', 'them', 'more']
        if q_lower in vague_terms or len(q_lower) < 5:
            return 'clarify'
        
        # Default to retrieve
        return 'retrieve'
    
    def _handle_direct_reply(self, query: str, stats: Dict) -> Dict[str, Any]:
        """Handle queries that don't need retrieval"""
        q_lower = query.lower()
        
        if any(g in q_lower for g in ['hi', 'hello', 'hey']):
            answer = f"Hello! 👋 I'm SupaQuery, your AI document assistant.\n\nI can help you analyze and query {stats['documents']} documents in your knowledge base. What would you like to know?"
        elif 'what can you do' in q_lower or 'help' in q_lower:
            answer = f"""I'm SupaQuery, specialized in document analysis. Here's what I can do:

📚 Knowledge Base: {stats['documents']} documents, {stats['chunks']} chunks, {stats['entities']} entities

✨ Capabilities:
1. Answer questions about your documents
2. Summarize content
3. Extract key entities and facts
4. Find specific information
5. Compare and analyze documents

Just ask me anything about your documents!"""
        else:
            answer = "You're welcome! Feel free to ask if you need anything else. 😊"
        
        return {
            "answer": answer,
            "citations": [],
            "sources": [],
            "entities": [],
            "query": query,
            "strategy": "direct_reply"
        }
    
    def _handle_clarification(self, query: str, stats: Dict) -> Dict[str, Any]:
        """Handle vague queries"""
        answer = f"""I need a bit more information to help you effectively.

Your knowledge base contains:
- {stats['documents']} documents
- {stats['chunks']} text chunks
- {stats['entities']} extracted entities

Try asking:
- "Summarize the main findings"
- "What are the key entities mentioned?"
- "Explain [specific topic]"
- "List the documents"

What would you like to know?"""
        
        return {
            "answer": answer,
            "citations": [],
            "sources": [],
            "entities": [],
            "query": query,
            "strategy": "clarify"
        }
    
    def _call_ollama_direct(self, prompt: str, max_tokens: int = 500) -> str:
        """Call Ollama API directly"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": max_tokens,
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                raise Exception(f"Ollama returned status {response.status_code}")
        except Exception as e:
            raise Exception(f"Ollama API call failed: {e}")
    
    async def add_document(self, file_info: Dict[str, Any]) -> None:
        """Add document to knowledge graph (delegates to graph service)"""
        doc_id = file_info.get("id") or file_info.get("document_db_id")
        if not doc_id:
            raise ValueError("Document ID is required")
        
        print(f"📊 Adding document to knowledge graph: {file_info.get('filename', 'Unknown')}")
        
        chunks_data = file_info.get("chunks_data") or file_info.get("chunk_data", [])
        
        doc_info_for_graph = {
            "id": str(doc_id),
            "filename": file_info.get("filename", "Unknown"),
            "type": file_info.get("type", "unknown"),
            "user_id": file_info.get("user_id"),
            "chunks": chunks_data
        }
        
        self.graph.add_document(doc_info_for_graph)
        
        # Add to FAISS index for hybrid retrieval
        print(f"   📊 Adding to FAISS index for semantic search...")
        try:
            faiss_chunks = []
            for i, chunk_data in enumerate(chunks_data):
                chunk_text = chunk_data if isinstance(chunk_data, str) else chunk_data.get("text", "")
                faiss_chunks.append({
                    'text': chunk_text,
                    'doc_id': str(doc_id),
                    'chunk_id': f"{doc_id}_chunk_{i}",
                    'source': file_info.get("filename", "Unknown")
                })
            
            if faiss_chunks:
                self.hybrid_rag.faiss.add_chunks(faiss_chunks)
                print(f"   ✅ Added {len(faiss_chunks)} chunks to FAISS index")
        except Exception as e:
            print(f"   ⚠️ FAISS indexing error: {e}")
        
        # Extract entities
        if chunks_data:
            for i, chunk_data in enumerate(chunks_data):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_text = chunk_data if isinstance(chunk_data, str) else chunk_data.get("text", "")
                
                try:
                    entities = self.entity_extractor.extract_entities(chunk_text)
                    
                    for entity in entities:
                        # Validate entity has required fields
                        if not isinstance(entity, dict) or "name" not in entity or "type" not in entity:
                            continue
                        
                        self.graph.add_entity({
                            "name": entity["name"],
                            "type": entity["type"],
                            "doc_id": str(doc_id),
                            "chunk_id": chunk_id
                        })
                except Exception as e:
                    print(f"   ⚠️ Entity extraction error for chunk {i}: {e}")
    
    def _apply_smart_document_filter(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Smart filtering: Extract entities from query and match to document sources.
        This handles queries like "what did Obama say" or "Trump's speech" automatically.
        
        Args:
            query: User query
            chunks: List of chunks to filter
            
        Returns:
            Filtered chunks if entities match, otherwise original chunks
        """
        if not chunks:
            return chunks
        
        try:
            # Extract entities from the query (people, organizations, etc.)
            query_entities = self.entity_extractor.extract_entities(query)
            
            if not query_entities:
                # No entities found, return all chunks
                return chunks
            
            # Get unique entity names from query (lowercase for matching)
            entity_names = set(e['name'].lower() for e in query_entities)
            
            # Group chunks by source/document
            chunks_by_source = {}
            for chunk in chunks:
                source = chunk.get('source', 'unknown')
                if source not in chunks_by_source:
                    chunks_by_source[source] = []
                chunks_by_source[source].append(chunk)
            
            # Find sources that match query entities
            matching_sources = []
            for source in chunks_by_source.keys():
                source_lower = source.lower()
                # Check if any query entity appears in the source/filename
                for entity_name in entity_names:
                    # Split entity name to handle first/last names (e.g., "Barack Obama" → ["barack", "obama"])
                    entity_parts = entity_name.split()
                    # Match if ANY part of the entity name appears in source
                    if any(part in source_lower for part in entity_parts if len(part) > 2):
                        matching_sources.append(source)
                        print(f"      Matched entity '{entity_name}' to source: {source[:60]}...")
                        break
            
            # If we found matching sources, filter to only those chunks
            if matching_sources:
                filtered = []
                for source in matching_sources:
                    filtered.extend(chunks_by_source[source])
                return filtered
            
            # FALLBACK: No filename matches, try matching entities to chunk content
            # This handles cases where entity is mentioned IN the conversation but not in filename
            print(f"      No filename matches, checking chunk content for entities...")
            content_matched_chunks = []
            for chunk in chunks:
                chunk_text = chunk.get('text', '').lower()
                # Check if any query entity appears in the chunk text
                for entity_name in entity_names:
                    entity_parts = entity_name.split()
                    if any(part in chunk_text for part in entity_parts if len(part) > 2):
                        content_matched_chunks.append(chunk)
                        break
            
            if content_matched_chunks:
                print(f"      Matched {len(content_matched_chunks)} chunks by content")
                return content_matched_chunks
            
            # No matches at all, return original chunks
            return chunks
            
        except Exception as e:
            print(f"   ⚠️ Smart filter error: {e}")
            return chunks
    
    async def delete_document(self, document_id: str, file_path: Optional[str] = None) -> None:
        """
        Delete a document from the knowledge graph, FAISS index, and optionally delete the physical file
        
        Args:
            document_id: The ID of the document to delete
            file_path: Optional path to the physical file to delete
        """
        # Delete from knowledge graph (Memgraph)
        success = self.graph.delete_document(document_id)
        
        if success:
            print(f"✅ Deleted document {document_id} from knowledge graph")
        else:
            print(f"⚠️  Failed to delete document {document_id} from knowledge graph")
        
        # Delete from FAISS index (via hybrid_rag service)
        try:
            faiss_success = self.hybrid_rag.delete_document(document_id, file_path=file_path)
            if faiss_success:
                print(f"✅ Deleted document {document_id} from FAISS index")
            else:
                print(f"⚠️  Failed to delete document {document_id} from FAISS index")
        except Exception as e:
            print(f"❌ Error deleting document from FAISS: {e}")
        
        # Delete physical file if path provided
        if file_path:
            try:
                from pathlib import Path
                file = Path(file_path)
                if file.exists():
                    file.unlink()
                    print(f"✅ Deleted physical file: {file_path}")
                else:
                    print(f"⚠️  File not found (may have been already deleted): {file_path}")
            except Exception as e:
                print(f"❌ Error deleting file {file_path}: {e}")


# Singleton instance
_enhanced_graph_rag_service = None

def get_enhanced_graph_rag_service() -> EnhancedGraphRAGService:
    """Get the singleton EnhancedGraphRAGService instance"""
    global _enhanced_graph_rag_service
    if _enhanced_graph_rag_service is None:
        _enhanced_graph_rag_service = EnhancedGraphRAGService()
    return _enhanced_graph_rag_service
