from pinecone.grpc import PineconeGRPC
from pinecone import ServerlessSpec

from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.sparse_embeddings.fastembed import FastEmbedSparseEmbedding

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.ingestion import IngestionPipeline
from llama_index.embeddings.openai import OpenAIEmbedding


import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
PINECONE_API_KEY = os.environ['PINECONE_API_KEY']

# Initialize connection to Pinecone
pc = PineconeGRPC(api_key=PINECONE_API_KEY)
index_name = "travel-destination-agent-app"

if index_name not in [index.name for index in pc.list_indexes()]:
    pc.create_index(
        index_name,
        dimension=1536,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

# Initialize your index 
pinecone_index = pc.Index(index_name)

# Initialize VectorStore
sparse_embedding_model = FastEmbedSparseEmbedding(
    model_name="prithivida/Splade_PP_en_v1"
)

vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    # add_sparse_vector=True,
    # sparse_embedding_model=sparse_embedding_model
)

node_parser = SentenceSplitter(chunk_size=200, chunk_overlap=20)
embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)

pipeline = IngestionPipeline(
    transformations=[
        node_parser,
        embed_model,
        ],
        vector_store=vector_store
)

def add_document(text, metadata):
    _document = Document(
        text=text,
        metadata=metadata
    )

    pipeline.run(documents=[_document])
    return _document

def delete_document(ref_doc_id):
    id_gen = pinecone_index.list(
        prefix=ref_doc_id
    )
    for ids in id_gen:
        pinecone_index.delete(
            ids=ids
        )

def retrieve_document(text):
    # Instantiate VectorStoreIndex object from your vector_store object
    vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=embed_model)

    # Grab 5 search results
    retriever = VectorIndexRetriever(index=vector_index, similariy_top_k=5)

    # Query vector DB
    answers = retriever.retrieve(text)

    return [{'metadata': i.metadata, 'text': i.text} for i in answers]
