import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain.prompts.chat import (
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.vectorstores import Chroma
from get_dataset import scrape
from langchain_community.document_loaders import JSONLoader


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

# scrape(["https://www.dilmahtea.com/"])

def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])

def load_documents():
    """Load a file from path, split it into chunks, embed each chunk and load it into the vector store."""
    # raw_documents = TextLoader("./docs/dataset.txt").load()
    raw_documents = JSONLoader(
    file_path='website_data.json',
    jq_schema='.body',
    text_content=False)
    # text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
    # return text_splitter.split_documents(raw_documents)
    return raw_documents.load()


def load_embeddings(documents, user_query):
    """Create a vector store from a set of documents."""
    db = Chroma.from_documents(documents, OpenAIEmbeddings())
    docs = db.similarity_search(user_query)
    print(docs)
    return db.as_retriever()

def generate_response(retriever, query):
    # Create a prompt template using a template from the config module and input variables
    # representing the context and question.
    # create the prompt
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | chat_prompt_template
        | model
        | StrOutputParser()
    )
    return chain.invoke(query)

def query(query):
    documents = load_documents()
    retriever = load_embeddings(documents, query)
    response = generate_response(retriever, query)
    return response

response = query("give a summary about dilmah")
print(response)