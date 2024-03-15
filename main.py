from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from generate_answer import load_documents,load_embeddings


domain = "https://www.dilmahtea.com/"
user_query = 'What is DIlmah?'
documents = load_documents(domain)
response, metadata = load_embeddings(documents, user_query)

template: str = """/
    You are a customer support specialist /
    question: {user_query}. You assist users with general inquiries based on {documents} /
    and  technical issues. /
    """

prompt = ChatPromptTemplate.from_template(template)
model = ChatOpenAI()
chain = prompt | model

print(chain.invoke({"user_query": user_query,"documents": documents}))
