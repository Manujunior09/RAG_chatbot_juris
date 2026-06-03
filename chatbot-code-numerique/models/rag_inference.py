import uuid
import re
import time
from typing import List, Dict, Any
from datetime import datetime, timedelta
import chromadb
from sentence_transformers import SentenceTransformer
import ollama
from dotenv import load_dotenv
import os

load_dotenv()

class RAGInference:
    def __init__(self, db_path: str = None,
                 embedding_model: str = None,
                 llm_config: Dict[str, Any] = None,
                 session_timeout_minutes: int = None):
        db_path = db_path or os.getenv("DB_PATH", "./chroma_db")
        embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
        session_timeout_minutes = session_timeout_minutes or int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

        self.model = SentenceTransformer(embedding_model)
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            "documents",
            metadata={"hnsw:space": "cosine"}
        )

        self.llm_config = llm_config or {
            "provider": "ollama",
            "model": os.getenv("OLLAMA_MODEL", "mistral"),
            "temperature": 0.1,
            "host": os.getenv("OLLAMA_HOST", "http://10.46.3.3:11434")
        }
        self.ollama_client = ollama.Client(host=self.llm_config["host"])

        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.sessions: Dict[str, List[Dict[str, str]]] = {}   # historique par session
        self.last_activity: Dict[str, datetime] = {}

    # -------------------  Détection des numéros d'articles dans la question -------------------
    def _extract_article_numbers(self, question: str) -> List[str]:
        return re.findall(r'\b(?:article|art\.?)\s*(\d+)', question, re.IGNORECASE)

    # -------------------  Lookup direct des chunks contenant un article précis -------------------
    def _lookup_articles(self, article_numbers: List[str]) -> List[Dict]:
        chunks = []
        seen_ids = set()
        all_docs = self.collection.get(include=["documents", "metadatas"])
        for doc, meta in zip(all_docs['documents'], all_docs['metadatas']):
            for num in article_numbers:
                pattern = re.compile(rf'\bArticle\s+{re.escape(num)}\b', re.IGNORECASE)
                if pattern.search(doc):
                    key = (meta['source'], meta['chunk_index'])
                    if key not in seen_ids:
                        seen_ids.add(key)
                        chunks.append({
                            "contenu": doc,
                            "source": meta['source'],
                            "chunk_index": meta['chunk_index'],
                            "score": 1.0
                        })
        return chunks

    # -------------------  Retrieval hybride (sémantique + lookup direct) -------------------
    def retrieve(self, question: str, n_results: int = 6, min_score: float = 0.60) -> List[Dict]:
        # 1. Lookup direct si la question cible un article précis
        article_numbers = self._extract_article_numbers(question)
        direct_chunks = self._lookup_articles(article_numbers) if article_numbers else []
        direct_keys = {(c['source'], c['chunk_index']) for c in direct_chunks}

        # 2. Retrieval sémantique
        q_embed = self.model.encode([question]).tolist()
        results = self.collection.query(
            query_embeddings=q_embed,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        semantic_chunks = []
        if results['documents'] and results['documents'][0]:
            for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
                score = 1 - dist
                key = (meta['source'], meta['chunk_index'])
                if score >= min_score and key not in direct_keys:
                    semantic_chunks.append({
                        "contenu": doc,
                        "source": meta['source'],
                        "chunk_index": meta['chunk_index'],
                        "score": score
                    })

        # Les chunks directs en premier, puis les sémantiques
        return direct_chunks + semantic_chunks

    # -------------------  Construction du prompt avec historique -------------------
    def _build_prompt(self, question: str, context_chunks: List[Dict], history: List[Dict], max_history: int = 5) -> str:
        # Récupérer les derniers échanges (max_history tours)
        recent = history[-max_history*2:] if len(history) > max_history*2 else history
        history_str = ""
        for msg in recent:
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            history_str += f"{role}: {msg['content']}\n"

        # Construire le bloc de contexte
        context_str = ""
        for i, ch in enumerate(context_chunks):
            context_str += f"\n--- Source {i+1} ({ch['source']}, pertinence {ch['score']:.2f}) ---\n{ch['contenu']}\n"

        prompt = f"""Tu es un assistant juridique expert du droit béninois. Tu réponds UNIQUEMENT à partir des extraits fournis ci-dessous.

### RÈGLES STRICTES DE PRÉCISION ET DE CONCISION

1. **Citation obligatoire des sources**
   - Pour chaque affirmation, cite le **numéro d’article** exact (ex: "Article 12 du Code du numérique")
   - Si l’extrait comporte un **chapitre, section ou titre**, indique-le aussi (ex: "Chapitre III, Section 2, Article 42")
   - Si plusieurs articles sont concernés, liste-les tous.

2. **Cas particulier : demande du contenu textuel d’un article précis**
   - Si l’utilisateur demande explicitement "Que stipule l’article X ?", "Quel est le contenu de l’article X ?", ou toute formulation similaire :
     - **Recherche** cet article dans les extraits fournis.
     - **Si trouvé** : restitue son contenu **textuellement et intégralement** (sans couper, résumer ou reformuler). Précède la citation du numéro complet de l’article et de son code/section.
     - **Si non trouvé** : réponds exactement : "L’article [numéro] n’est pas présent dans les documents disponibles."
   - Dans ce cas, pas besoin de réponse structurée en plusieurs parties ; le texte de l’article suffit, précédé de sa référence.

3. **Pour les autres questions (hors demande textuelle d’un article)**
   - Réponds de manière **synthétique mais complète** : va droit au but, sans formules d’introduction ou de conclusion superflues.
   - Ne sacrifie aucun détail juridique utile (conditions, délais, exceptions, renvois).
   - Pour les définitions ou chiffres, reprend **textuellement** l’élément clé entre guillemets.
   - Structure conseillée : réponse courte → base légale → citation(s) textuelle(s) → limites ou renvois non résolus.

4. **Gestion des liens entre articles**
   - Si un article renvoie à un autre (ex: "sous réserve de l’article X"), vérifie que l’article X est présent dans les extraits.
   - Si oui, cite-le également ; si non, mentionne : "L’article X cité dans l’article Y n’est pas fourni dans les extraits disponibles."

5. **Absence d’information**
   - Si l’information n’est pas explicitement dans les extraits, réponds exactement :  
     *"Je ne trouve pas cette information dans les documents disponibles."*
   - N’utilise aucune connaissance externe.

6. **Cohérence interne**
   - Si deux extraits semblent contradictoires, signale-le poliment et cite les deux articles.

=== HISTORIQUE ===
{history_str if history_str else "Aucun échange précédent."}

=== EXTRAITS JURIDIQUES (classés par pertinence) ===
{context_str if context_str else "Aucun extrait pertinent trouvé."}
=== FIN DES EXTRAITS ===

Question : {question}

Réponse (en respectant les règles ci-dessus, notamment le cas des articles demandés textuellement) :"""
        return prompt

    # -------------------  Gestion des sessions isolées -------------------
    def create_session(self) -> str:
        sid = str(uuid.uuid4())
        self.sessions[sid] = []
        self.last_activity[sid] = datetime.now()
        return sid

    def _cleanup_inactive(self):
        now = datetime.now()
        to_delete = [sid for sid, last in self.last_activity.items() if now - last > self.session_timeout]
        for sid in to_delete:
            del self.sessions[sid]
            del self.last_activity[sid]

    def ask(self, question: str, session_id: str, n_results: int = 6, min_score: float = 0.60) -> Dict[str, Any]:
        self._cleanup_inactive()
        if session_id not in self.sessions:
            # Session inconnue : on la crée par tolérance
            self.sessions[session_id] = []
            self.last_activity[session_id] = datetime.now()

        # Mesure des temps
        t0 = time.time()
        chunks = self.retrieve(question, n_results, min_score)
        t1 = time.time()

        # Construire le prompt avec l'historique de cette session
        prompt = self._build_prompt(question, chunks, self.sessions[session_id])

        if not chunks:
            answer = "Je ne trouve pas d'information pertinente dans les documents disponibles pour répondre à cette question."
        else:
            response = self.ollama_client.chat(
                model=self.llm_config["model"],
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": self.llm_config["temperature"]}
            )
            answer = response["message"]["content"]
        t2 = time.time()

        # Mise à jour de l'historique
        self.sessions[session_id].append({"role": "user", "content": question})
        self.sessions[session_id].append({"role": "assistant", "content": answer})
        self.last_activity[session_id] = datetime.now()

        # Construction du dictionnaire de retour (Q2.4)
        sources = [{
            "document": c["source"],
            "chunk_index": c["chunk_index"],
            "score": c["score"],
            "extrait": c["contenu"][:150]
        } for c in chunks]

        return {
            "reponse": answer,
            "sources": sources,
            "temps_retrieval_ms": int((t1 - t0) * 1000),
            "temps_llm_ms": int((t2 - t1) * 1000),
            "temps_total_ms": int((t2 - t0) * 1000),
            "session_id": session_id,
            "nb_chunks_trouves": len(chunks),
            "question": question
        }

    def clear_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            del self.last_activity[session_id]
            return True
        return False

    def list_sessions(self) -> List[Dict]:
        now = datetime.now()
        return [{
            "session_id": sid,
            "age_minutes": int((now - self.last_activity[sid]).total_seconds() / 60),
            "nb_messages": len(hist)
        } for sid, hist in self.sessions.items()]