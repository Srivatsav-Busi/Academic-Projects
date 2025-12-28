"""
Knowledge Base for Srivatsav Job Search GPT
Handles document processing, embeddings, and retrieval for personalized job search assistance.
"""

import os
import yaml
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
# RetrievalQA not available in current LangChain version, will implement custom solution
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTextRetriever:
    """Simple text-based retriever for when embeddings are not available."""
    
    def __init__(self, documents: List[Document]):
        self.documents = documents
    
    def get_relevant_documents(self, query: str, k: int = 5) -> List[Document]:
        """Get relevant documents based on simple text matching."""
        # Simple keyword matching
        query_lower = query.lower()
        scored_docs = []
        
        for doc in self.documents:
            content_lower = doc.page_content.lower()
            # Count keyword matches
            score = sum(1 for word in query_lower.split() if word in content_lower)
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score and return top k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:k]]

class JobSearchKnowledgeBase:
    """
    Knowledge base for Srivatsav's job search assistant.
    Handles document loading, processing, and retrieval.
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """Initialize the knowledge base with configuration."""
        self.config = self._load_config(config_path)
        # Initialize embeddings based on configuration
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openrouter")
        
        if provider == "openrouter":
            # Use OpenAI for embeddings (OpenRouter doesn't support text-embedding-ada-002)
            # Fall back to OpenAI API key for embeddings
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                # If no OpenAI key, use a simple embedding approach
                # For now, we'll use a fallback that doesn't require embeddings
                self.embeddings = None
                logger.warning("No OpenAI API key found. Using fallback embedding approach.")
            else:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=openai_key,
                    model="text-embedding-ada-002"
                )
        else:
            # Use OpenAI for embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-ada-002"
            )
        self.vector_store = None
        self.qa_chain = None
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def load_documents(self, data_dir: str = "data") -> List[Document]:
        """
        Load all documents from the data directory.
        
        Args:
            data_dir: Path to directory containing documents
            
        Returns:
            List of loaded documents
        """
        logger.info(f"Loading documents from {data_dir}")
        
        # Load documents from directory
        loader = DirectoryLoader(
            data_dir,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        # Also load text files
        text_loader = DirectoryLoader(
            data_dir,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        # Load CSV files (for job targets)
        csv_loader = DirectoryLoader(
            data_dir,
            glob="**/*.csv",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"}
        )
        
        documents = []
        
        try:
            # Load markdown files
            md_docs = loader.load()
            documents.extend(md_docs)
            logger.info(f"Loaded {len(md_docs)} markdown documents")
            
            # Load text files
            txt_docs = text_loader.load()
            documents.extend(txt_docs)
            logger.info(f"Loaded {len(txt_docs)} text documents")
            
            # Load CSV files
            csv_docs = csv_loader.load()
            documents.extend(csv_docs)
            logger.info(f"Loaded {len(csv_docs)} CSV documents")
            
        except Exception as e:
            logger.error(f"Error loading documents: {e}")
            
        return documents
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents by splitting them into chunks.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of processed document chunks
        """
        logger.info("Processing documents...")
        
        # Configure text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get("vector_store", {}).get("chunk_size", 1000),
            chunk_overlap=self.config.get("vector_store", {}).get("chunk_overlap", 200),
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Split documents
        processed_docs = text_splitter.split_documents(documents)
        logger.info(f"Split documents into {len(processed_docs)} chunks")
        
        return processed_docs
    
    def build_vector_store(self, documents: List[Document], save_path: str = "data/embeddings") -> None:
        """
        Build FAISS vector store from processed documents.
        
        Args:
            documents: List of processed document chunks
            save_path: Path to save the vector store
        """
        logger.info("Building vector store...")
        
        try:
            # Create vector store
            if self.embeddings is not None:
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
                
                # Save vector store
                os.makedirs(save_path, exist_ok=True)
                self.vector_store.save_local(save_path)
                logger.info(f"Vector store saved to {save_path}")
            else:
                # Fallback: store documents without embeddings for simple text search
                self.vector_store = None
                self.documents = documents
                logger.info("Vector store built successfully (text-only mode)")
            
        except Exception as e:
            logger.error(f"Error building vector store: {e}")
            raise
    
    def load_vector_store(self, load_path: str = "data/embeddings") -> bool:
        """
        Load existing vector store from disk.
        
        Args:
            load_path: Path to load the vector store from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(load_path):
                self.vector_store = FAISS.load_local(load_path, self.embeddings)
                logger.info(f"Vector store loaded from {load_path}")
                return True
            else:
                logger.warning(f"Vector store not found at {load_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def create_qa_chain(self) -> None:
        """Create the question-answering chain."""
        if not self.vector_store and not hasattr(self, 'documents'):
            raise ValueError("Vector store not initialized. Call build_vector_store() or load_vector_store() first.")
        
        # Create retriever
        if self.vector_store is not None:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 5}
            )
        else:
            # Fallback: simple text-based retriever
            retriever = SimpleTextRetriever(self.documents)
        
        # Create LLM based on configuration
        llm_config = self.config.get("llm", {})
        provider = llm_config.get("provider", "openrouter")
        
        if provider == "openrouter":
            # Use OpenRouter API
            llm = ChatOpenAI(
                openai_api_key=os.getenv("OPENROUTER_API_KEY"),
                model_name=llm_config.get("model", "anthropic/claude-3.5-sonnet"),
                temperature=llm_config.get("temperature", 0.7),
                max_tokens=llm_config.get("max_tokens", 2000),
                openai_api_base=llm_config.get("base_url", "https://openrouter.ai/api/v1")
            )
        else:
            # Use OpenAI API
            llm = OpenAI(
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                model_name=self.config.get("openai", {}).get("model", "gpt-4o"),
                temperature=self.config.get("openai", {}).get("temperature", 0.7),
                max_tokens=self.config.get("openai", {}).get("max_tokens", 2000)
            )
        
        # Create prompt template
        prompt_template = """You are Srivatsav's AI Job Search Advisor. Use the following context about Srivatsav's professional background, experience, and career goals to answer questions about job search, resume tailoring, interview preparation, and career advice.

Context:
{context}

Question: {question}

Answer: Provide a detailed, personalized response based on Srivatsav's background and the context provided. Be specific and actionable in your recommendations."""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create custom QA chain (RetrievalQA not available in current LangChain version)
        self.qa_chain = {
            "llm": llm,
            "retriever": retriever,
            "prompt": PROMPT
        }
        
        logger.info("QA chain created successfully")
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the knowledge base with a question.
        
        Args:
            question: Question to ask
            
        Returns:
            Dictionary containing answer and source documents
        """
        if not self.qa_chain:
            raise ValueError("QA chain not initialized. Call create_qa_chain() first.")
        
        try:
            # Get relevant documents
            retriever = self.qa_chain["retriever"]
            docs = retriever.get_relevant_documents(question)
            
            # Create context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = self.qa_chain["prompt"].format(
                context=context,
                question=question
            )
            
            # Get LLM response
            llm = self.qa_chain["llm"]
            response = llm.invoke(prompt)
            
            # Handle different response types
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            return {
                "answer": answer,
                "source_documents": docs
            }
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            return {"answer": "Error processing query", "source_documents": []}
    
    def get_similar_documents(self, query: str, k: int = 5) -> List[Document]:
        """
        Get similar documents for a query.
        
        Args:
            query: Query string
            k: Number of similar documents to return
            
        Returns:
            List of similar documents
        """
        if not self.vector_store:
            raise ValueError("Vector store not initialized.")
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logger.error(f"Error getting similar documents: {e}")
            return []
    
    def initialize(self, rebuild: bool = False) -> None:
        """
        Initialize the knowledge base.
        
        Args:
            rebuild: Whether to rebuild the vector store from scratch
        """
        logger.info("Initializing knowledge base...")
        
        # Try to load existing vector store first
        if not rebuild and self.load_vector_store():
            logger.info("Loaded existing vector store")
        else:
            # Build new vector store
            logger.info("Building new vector store...")
            documents = self.load_documents()
            processed_docs = self.process_documents(documents)
            self.build_vector_store(processed_docs)
        
        # Create QA chain
        self.create_qa_chain()
        logger.info("Knowledge base initialized successfully")

def main():
    """Main function for testing the knowledge base."""
    # Initialize knowledge base
    kb = JobSearchKnowledgeBase()
    kb.initialize(rebuild=True)
    
    # Test queries
    test_queries = [
        "What are Srivatsav's key technical skills?",
        "What companies is Srivatsav targeting for job applications?",
        "What are Srivatsav's recent achievements at TechCorp?",
        "Generate a LinkedIn connection request for a Google recruiter",
        "What should Srivatsav highlight in a resume for a Senior Data Engineer role at Meta?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = kb.query(query)
        print(f"Answer: {result['answer']}")
        print("-" * 80)

if __name__ == "__main__":
    main()
