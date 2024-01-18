import chromadb
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFLoader


openai_api_key = ""
name = "collection_name"
metadata_options = {"hnsw:space": "cosine"}
collection = None
maxLength = 0

def RAG_query(input):
    response = chain(input)
    return response['result']

def query(input, n_results):
    results = collection.query(query_texts=[input], n_results=n_results)
    return results

def add(documents):
    collection.add(ids=[str(getNextPos())], documents=documents)

def addFromPDF(path):
    print(path)
    loader = PyPDFLoader(path)
    docs = loader.load_and_split()
    for doc in docs:
        add(str(doc))

def delete(id):
    collection.delete(ids=[id])

def update(ids, documents):
    collection.update(ids=ids, documents=documents)

def getCollection():
    return collection.get()

def getNextPos():
    collectionIDs = getCollection()['ids']
    collectionIDs_string = [eval(i) for i in collectionIDs]
    length = len(collectionIDs_string)
    if length==0:
        return 1
    
    for i in range(1, collectionIDs_string[-1]):
        if i not in collectionIDs_string:
            return i
    return length+1

def emptyDB():
    for i in collection.get()['ids']:
        collection.delete(ids=[i])




llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.8, openai_api_key=openai_api_key)

#using default chromadb embeddings
embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# using openai embeddings (wich if used need to be used when creating the collection too)
#embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

# client on a chromadb server
client = chromadb.HttpClient(host="chromadb-container", port=8000)

# client on this machine
# client = chromadb.Client()

collection = client.get_or_create_collection(name, metadata_options)

chroma_db = Chroma(client=client, 
                   embedding_function=embeddings,
                   collection_name=name)

chain = RetrievalQA.from_chain_type(llm=llm,
                                    chain_type="stuff",
                                    retriever=chroma_db.as_retriever())