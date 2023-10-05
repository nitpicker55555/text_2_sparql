import os
import getpass
from dotenv import load_dotenv
import os
# from streamlit_chat import message
import io
import asyncio

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

# Load the document, split it into chunks, embed each chunk and load it into the vector store.
raw_documents = TextLoader(r'C:\Users\Morning\Desktop\hiwi\llm_sparql\query_template.txt').load()

text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0)

documents = text_splitter.split_documents(raw_documents)

db = Chroma.from_documents(documents, OpenAIEmbeddings(), persist_directory="./chroma_db2")

query="I want to get query of Get all hotels over 30m high"
docs = db.similarity_search(query)
print(docs[0].page_content)
# load from disk
db3 = Chroma(persist_directory="./chroma_db2", embedding_function=OpenAIEmbeddings())
docs = db3.similarity_search(query)
print(docs[0].page_content)