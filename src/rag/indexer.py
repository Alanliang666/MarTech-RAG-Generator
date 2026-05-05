"""
This module ingests CSV ad copy data into ChromaDB. 
It configures the AI embedding model to vectorize the text and store it in the vector database.
"""
import csv
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
from llama_index.core.embeddings import MockEmbedding
from src.core import get_settings

# Load environment variables
settings_config = get_settings()

# Initialize ChromaDB client and collection
client = chromadb.EphemeralClient()
ad_copies = client.get_or_create_collection('ad_copies')

# Read CSV and create documents
documents = []
with open("data/mock_ad_data.csv", 'r', encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        documents.append(Document(text=row['ad_copy'],
            metadata={
                "product_category": row['product_category'], 
                "ctr": float(row['ctr']), 
                "cvr": float(row['cvr']), 
                "roas": float(row['roas']), 
                "keyword":row['keyword']
            }
        ))

# Configure embedding model
# Settings.embed_model = OpenAIEmbedding(
#     model= "text-embedding-3-small",
#     api_key=settings_config.openai_api_key.get_secret_value()
# )
Settings.embed_model = MockEmbedding(embed_dim=1536) # Use mock model

# Set up storage context and build index
vector_store = ChromaVectorStore(chroma_collection=ad_copies)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
