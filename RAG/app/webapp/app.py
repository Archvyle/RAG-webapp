import os
import chromadbClient
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename

# path assoluto per salvare i pdf caricati dal form html
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir + '/data/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

sum_results = ""
RAG_results = ""
questions = ""
results = None
length = 0

# query alla chain di langchain e quindi tramite llm
def RAG_query(input, summarize, source):
    global RAG_results
    # in base ai parametri booleani vengono aggiune parti al prompt
    RAG_results = chromadbClient.RAG_query(("Summarize the answer to this question: " if summarize else '') + str(input) + ("(Specify the source)" if source else ''))

# query al db vettoriale chromadb
def query(input, nQueries):
    global results, length
    results = chromadbClient.query(str(input), int(nQueries))
    length = len(results['ids'][0])

# RAG query con aggiunta richiesta 10 domande
def generate_questions(questions_query):
    global questions
    questions = chromadbClient.RAG_query("Generate 10 questions about this topic: " + str(questions_query))

def add(documents):
    chromadbClient.add(documents)

def addFromPDF(path):
    chromadbClient.addFromPDF(path)

def delete(id):
    chromadbClient.delete(id)

def update(ids, documents):
    chromadbClient.update(ids=ids, documents=documents)

def emptyDB():
    chromadbClient.emptyDB()

# index page
@app.route("/", methods=['GET', 'POST'])
def index_page():
    return render_template('index.html')

# complete view of the database
# viene presa la collection con getCollection(), viene scorsa e viene restituita
@app.route("/complete-view", methods=['GET', 'POST'])
def complete_view_page():
    collectionItems = chromadbClient.getCollection()
    collectionItems['ids'].sort()
    length = len(collectionItems['ids'])
    return render_template('complete-view.html', collectionItems=collectionItems, length=length)

# queries page
@app.route("/query", methods=['GET', 'POST'])
def query_page():

    # se la richiesta è una GET non succede niente
    if request.method == 'GET':
        return render_template('query.html', results=results, length=length)
    
    # se la richiesta è una POST viene controllato il valore 'action' per determinare che bottone di invio form è stato premuto
    elif request.method == 'POST':
        if request.form.get('action') == 'RAG Search':
            RAG_queryInput = request.form.get('RAG_query')
            # condizione che determina se le checkbox per cambiare il prompt sono state checckate
            if request.form.get('source'):
                specifySource = True
            else:
                specifySource = False
            if request.form.get('summarize'):
                summarizeResult = True
            else:
                summarizeResult = False
            RAG_query(RAG_queryInput, summarizeResult, specifySource)
            return render_template('query.html', questions=questions, sum_results=sum_results, RAG_results=RAG_results, results=results, length=length)
    
        elif request.form.get('action') == 'Search':
            queryInput = request.form.get('query')
            # nQueries è il numero di queries che vengono mostrate
            nQueries = request.form.get('nQueries')
            query(queryInput, nQueries)
            return render_template('query.html', questions=questions, sum_results=sum_results, RAG_results=RAG_results, results=results, length=length)
        
        elif request.form.get('action') == 'Generate Questions':
            questions_query = request.form.get('questions_query')
            generate_questions(questions_query)
            return render_template('query.html', questions=questions, sum_results=sum_results, RAG_results=RAG_results, results=results, length=length)
        
        else:
             return render_template('query.html', questions=questions, sum_results=sum_results, RAG_results=RAG_results, results=results, length=length)

# db modifications page
@app.route('/modify', methods=['GET', 'POST'])
def modify_page():

    if request.method == 'GET':
        return render_template('modify.html')
    
    elif request.method == 'POST':
        if request.form.get('action') == 'Add':
            documentAdd = request.form.get('document_add')
            add(documentAdd)
            return render_template('modify.html')
        
        elif request.form.get('action') == 'Add PDF':
            # il pdf dal form html viene salvato su disco, aggiunto al database e rimosso dal disco
            file = request.files['file']
            # pulizia filename
            fileName = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], fileName))
            addFromPDF(UPLOAD_FOLDER + fileName)
            os.remove(UPLOAD_FOLDER + fileName)
            return render_template('modify.html')
        
        elif request.form.get('action') == 'Remove':
            IDRemove = request.form.get('id_remove')
            delete(IDRemove)
            return render_template('modify.html')
        
        elif request.form.get('action') == 'Update':
            IDUpdate = request.form.get('id_update')
            documentUpdate = request.form.get('document_update')
            update(IDUpdate, documentUpdate)
            return render_template('modify.html')

        elif request.form.get('action') == 'EMPTY DB':
            emptyDB()
            return render_template('modify.html')
        
        else:
            return render_template('modify.html')

# Do not use run() in a production setting. It is not intended to meet security and performance requirements for a production server.
# Instead, see /deploying/index for WSGI server recommendations.
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)