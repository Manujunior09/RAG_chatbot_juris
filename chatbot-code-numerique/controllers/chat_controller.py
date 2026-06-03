from flask import Blueprint, render_template, request, jsonify, session
from models.rag_inference import RAGInference
import os

chat_bp = Blueprint('chat', __name__)

# Instance unique du moteur RAG (sera initialisée dans app.py)
rag = None

def init_rag(rag_instance):
    global rag
    rag = rag_instance

@chat_bp.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = rag.create_session()
    return render_template('chat.html', session_id=session['session_id'])

@chat_bp.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    session_id = data.get('session_id')
    if not question or not session_id:
        return jsonify({"error": "Paramètres manquants"}), 400
    result = rag.ask(question, session_id)
    return jsonify(result)

@chat_bp.route('/new_session', methods=['POST'])
def new_session():
    new_sid = rag.create_session()
    session['session_id'] = new_sid
    return jsonify({"session_id": new_sid})