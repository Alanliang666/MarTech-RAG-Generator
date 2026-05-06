import chromadb
from llama_index.core import StorageContext, VectorStoreIndex, Settings, PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.llms.mock import MockLLM
from functools import lru_cache
from src.core import get_settings

class Engine:
    def __init__(self, settings):
        
        # Setting the AI model API
        Settings.llm = MockLLM(max_tokens=256)

        # Set up the data base using ChromaDB
        self.data_base = settings.chromadb
        client = chromadb.PersistentClient(path = self.data_base)
        
        # Get the data from indexer.py make collection 
        ad_copies_collection = client.get_or_create_collection('ad_copies')
        
        # Store into Vector and set up Storage and save in the index
        vector_store = ChromaVectorStore(chroma_collection = ad_copies_collection)
        storage_context = StorageContext.from_defaults(vector_store = vector_store)
        self.index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    def generate(self, request_data):
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
    settings = get_settings()
    return Engine(settings)
