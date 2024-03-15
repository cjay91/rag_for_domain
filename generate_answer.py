import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts import ChatPromptTemplate
from langchain.vectorstores import Chroma
from get_dataset import scrape
from langchain_community.document_loaders import DirectoryLoader
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter



load_dotenv()


template: str = """/
    You are a customer support specialist /
    question: {question}. You assist users with general inquiries based on {context} /
    and  technical issues. /
    """
system_message_prompt = SystemMessagePromptTemplate.from_template(template)
human_message_prompt = HumanMessagePromptTemplate.from_template(
    input_variables=["question", "context"],
    template="{question}",
)
chat_prompt_template = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)
model = ChatOpenAI()

def generate_txt_directory(url):

    scrape(url)

    return True

def load_documents(domain):
    generate_txt_directory(domain)
    website_dir = os.path.join('docs', domain.lstrip('https://').rstrip('/').replace('/', '_'))
    loaders = DirectoryLoader(f'{website_dir}', glob="**/*.txt")
    docs = loaders.load()

    return docs

def load_embeddings(documents, user_query):
    # This text splitter is used to create the child documents
    child_splitter = RecursiveCharacterTextSplitter(chunk_size=400)

    # The vectorstore to use to index the child chunks
    vectorstore_new = Chroma(
        collection_name="full_documents_new", embedding_function=OpenAIEmbeddings()
    )
    # The storage layer for the parent documents
    store = InMemoryStore()
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore_new,
        docstore=store,
        child_splitter=child_splitter,
    )

    retriever.add_documents(documents, ids=None)

    sub_docs = vectorstore_new.similarity_search(user_query)

    return (sub_docs[0].page_content,sub_docs[0].metadata['source'])

