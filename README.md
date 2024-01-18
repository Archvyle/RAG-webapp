# RAG-webapp
Retrieval Augmented Generation web application using **flask** as a web framework, **chromadb** as the vector database and **langchain**.

## Features
- **Modify** a vector database by
	- adding new documents either by typing them or by uploading .pdf files
	- deleting rows by ID
	- updating rows by ID
- **Query** the database through a large language model like gpt-3.5-turbo and ask it to
	-  summarize your loaded documents

## Notes
The project includes docker configuration files for building a multi-container Docker application which includes the flask server and the chromadb server, the chromadb client is set to be created in the chromadb container like this:
```
client  =  chromadb.HttpClient(host="chromadb-container", port=8000)
```
