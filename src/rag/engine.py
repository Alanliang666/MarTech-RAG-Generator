"""
This module implements the RAG engine, initializes the ChromaDB client.
And generates the prompt template while limiting retrieval to the top 3 results.
"""
from functools import lru_cache
import chromadb
from llama_index.core import StorageContext, VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.llms.mock import MockLLM
from src.core import get_settings

class Engine:
    def __init__(self, settings):
        """
        Initializes the ChromaDB client and sets up the vector database.
        @param settings: Settings, the application settings containing configuration variables.
        """
        # Set up the LLM
        Settings.llm = MockLLM(max_tokens=256)

        # Retrieve the ChromaDB collection for ad copies.
        self.data_base = settings.chromadb
        client = chromadb.PersistentClient(path = self.data_base)

        # Get the data from indexer.py make collection 
        ad_copies_collection = client.get_or_create_collection('ad_copies')

        # Configure the storage context and initialize the vector index.
        vector_store = ChromaVectorStore(chroma_collection = ad_copies_collection)
        storage_context = StorageContext.from_defaults(vector_store = vector_store)
        self.index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    def generate(self, request_data):
        """
        Generates the prompt and connects to the AI model to create ad copies.
        @param request_data: GenerateRequest, the user input payload based on the GenerateRequest schema.
        """
        prompt_tmpl_str = """
            You are a professional copywriter. Please refer to the previous successful copy below:
            ---------------------
            {context_str}
            ---------------------
            Based on the copy style above, please follow the product requirements below to generate 5 different ad copy test versions:
            {query_str}

            Please output the copy directly:
            """

        query_engine = self.index.as_query_engine(
            text_qa_template=PromptTemplate(prompt_tmpl_str),
            similarity_top_k=3
        )

        query_str = f"""
            - Product Name: {request_data.product_name}
            - Main Keyword: {request_data.keyword}
            - Original Price: {request_data.original_price}
            - Limited-Time Promotional Price: {request_data.promotional_price}
            - Promotional Content (Offers): {request_data.promotional_content}
            """

        response = query_engine.query(query_str)

        return response.response

@lru_cache
def rag_engine():
    """
    Returns a cached instance of the RAG Engine,
    to avoid repeated instantiations and improve performance.
    """
    settings = get_settings()
    return Engine(settings)
