"""RAG retrievers for firm history and project documents.

This module provides vector store retrievers using ChromaDB for semantic
search over past project documents.
"""

from __future__ import annotations

import sys

# Patch sqlite3 with pysqlite3-binary to satisfy ChromaDB's >= 3.35.0 requirement
try:
    import pysqlite3  # type: ignore[import-untyped]
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

from dataclasses import dataclass
from typing import TYPE_CHECKING

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.config import Settings
from app.database.models import ProjectDocument


@dataclass
class SearchResult:
    """Result from a similarity search."""
    project: ProjectDocument
    similarity_score: float
    content: str


class FirmHistoryRetriever:
    """Retriever for searching firm project history using vector similarity.
    
    Uses ChromaDB for vector storage and OpenAI embeddings for semantic search.
    Projects are automatically indexed when added to the database.
    """
    
    def __init__(
        self,
        settings: Settings,
        collection_name: str | None = None,
        persist_directory: str | None = None
    ) -> None:
        """Initialize the retriever with ChromaDB and embeddings.
        
        Args:
            settings: Application settings containing OpenAI API key
            collection_name: Name of the ChromaDB collection (defaults to settings)
            persist_directory: Directory for ChromaDB persistence (defaults to settings)
        """
        self.settings = settings
        self.collection_name = collection_name or settings.chroma_collection_name
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        
        # Initialize embeddings via OpenRouter
        # OpenRouter supports OpenAI embedding models via their API
        api_key = None
        if settings.openrouter_api_key:
            api_key = settings.openrouter_api_key
        
        self.embeddings = OpenAIEmbeddings(
            api_key=api_key,
            model="openai/text-embedding-3-small",  # Via OpenRouter
            openai_api_base="https://openrouter.ai/api/v1"
        )
        
        # Initialize ChromaDB vector store
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    async def search(
        self,
        query: str,
        db_session: Session,
        k: int = 5,
        min_similarity: float = 0.1
    ) -> list[SearchResult]:
        """Search for similar projects based on query.
        
        Args:
            query: The search query (project description/requirements)
            db_session: SQLAlchemy session for fetching full project data
            k: Number of results to return
            min_similarity: Minimum similarity score (0-1) to include result
            
        Returns:
            List of search results with project data and similarity scores
        """
        # Perform similarity search
        results = await self.vectorstore.asimilarity_search_with_relevance_scores(
            query,
            k=k
        )
        
        search_results: list[SearchResult] = []
        
        for doc, score in results:
            if score < min_similarity:
                continue
                
            # Get the project ID from metadata
            project_id = doc.metadata.get("project_id")
            if not project_id:
                continue
            
            # Fetch full project from database
            project = db_session.query(ProjectDocument).filter_by(
                id=project_id
            ).first()
            
            if project and project.document_status == "active":
                search_results.append(SearchResult(
                    project=project,
                    similarity_score=score,
                    content=doc.page_content
                ))
        
        return search_results
    
    async def index_project(self, project: ProjectDocument) -> str:
        """Index a project document into the vector store.
        
        Args:
            project: The project document to index
            
        Returns:
            The embedding ID of the indexed document
        """
        # Create rich content for embedding
        content = self._create_project_content(project)
        
        # Add to vector store
        doc_id = await self.vectorstore.aadd_texts(
            texts=[content],
            metadatas=[{
                "project_id": project.id,
                "project_name": project.project_name,
                "industry": project.industry,
                "project_type": project.project_type,
                "tech_stack": ",".join(project.tech_stack),
            }]
        )
        
        return doc_id[0] if doc_id else ""
    
    def _create_project_content(self, project: ProjectDocument) -> str:
        """Create searchable content from a project document.
        
        Combines relevant fields into a single text for embedding.
        """
        parts = [
            f"Project: {project.project_name}",
            f"Client: {project.client_name}",
            f"Industry: {project.industry}",
            f"Type: {project.project_type}",
            f"Description: {project.description}",
            f"Tech Stack: {', '.join(project.tech_stack)}",
            f"Team Size: {project.team_size}",
            f"Duration: {project.duration_weeks} weeks",
            f"Outcome: {project.outcome}",
        ]
        
        if project.challenges:
            parts.append(f"Challenges: {', '.join(project.challenges)}")
        
        if project.key_features:
            parts.append(f"Key Features: {', '.join(project.key_features)}")
        
        return "\n".join(parts)
    
    async def delete_project_index(self, embedding_id: str) -> None:
        """Remove a project from the vector store.
        
        Args:
            embedding_id: The embedding ID to remove
        """
        await self.vectorstore.adelete([embedding_id])
