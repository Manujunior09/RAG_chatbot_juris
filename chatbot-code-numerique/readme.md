# Chatbot RAG - Installation et exécution


## 1. Créer un environnement virtuel
Ouvrir un terminal dans le dossier `chatbot-code-numerique` puis exécuter :

```bash
python -m venv venv
```

## 2. Activer l'environnement virtuel

- Sous CMD :

```cmd
.\venv\Scripts\activate
```

## 3. Installer les dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Vérifier le fichier `.env`



```env
OLLAMA_HOST=http://10.46.3.3:11434
OLLAMA_MODEL=mistral
EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
DB_PATH=./chroma_db
CHUNK_SIZE=500
CHUNK_OVERLAP=100
MIN_SCORE=0.5
SESSION_TIMEOUT_MINUTES=30
SECRET_KEY=une-cle-tres-secrete-pour-la-production
FLASK_DEBUG=false
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

## 5. Indexer les documents

Avant de démarrer le chatbot, exécuter :

```bash
python indexer.py
```

Cela va créer et remplir la base vectorielle `chroma_db`.

## 6. Lancer l'application

```bash
python app.py
```

Puis ouvrir le navigateur à l'adresse :

```text
http://127.0.0.1:5000
```
