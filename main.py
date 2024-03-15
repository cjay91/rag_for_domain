
from generate_answer import load_documents,load_embeddings


domain = "https://www.dilmahtea.com/"
user_query = 'What is DIlmah?'
documents = load_documents(domain)
response, metadata = load_embeddings(documents, user_query)

print(response, metadata)