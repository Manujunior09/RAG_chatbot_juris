from flask import Flask
from controllers.chat_controller import chat_bp, init_rag
from models.rag_inference import RAGInference
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='views', static_folder='static')
    app.secret_key = os.getenv('SECRET_KEY', 'dev-key-change-me')

    # Initialisation du moteur RAG avec les variables d'environnement
    rag = RAGInference()
    init_rag(rag)

    # Enregistrement du Blueprint
    app.register_blueprint(chat_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    app.run(debug=debug, host=host, port=port)