import os
from models.document_ingester import DocumentIngester
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    # Paramètres depuis .env (ou valeurs par défaut)
    db_path = os.getenv("DB_PATH", "./chroma_db")
    embedding_model = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
    chunk_size = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "100"))
    strategy = "semantic"   # vous pouvez passer à "fixed" si besoin

    ingester = DocumentIngester(
        db_path=db_path,
        embedding_model=embedding_model,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        strategy=strategy
    )

    # Indexer tous les fichiers du dossier documents/
    docs_folder = "documents"
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        print(f"Création du dossier {docs_folder}. Veuillez y placer vos fichiers.")
    else:
        files = [f for f in os.listdir(docs_folder) if os.path.isfile(os.path.join(docs_folder, f))]
        if not files:
            print(f"Aucun fichier trouvé dans {docs_folder}. Placez-y vos documents (.txt, .pdf, .docx, .csv)")
        else:
            for filename in files:
                file_path = os.path.join(docs_folder, filename)
                try:
                    ingester.ingest(file_path)
                except Exception as e:
                    print(f"Erreur lors de l'indexation de {filename} : {e}")
            stats = ingester.get_stats()
            print("\n=== Statistiques de la base vectorielle ===")
            print(f"Total chunks : {stats['total_chunks']}")
            print(f"Documents : {stats['documents']}")
            print(f"Taille moyenne chunk : {stats['taille_moyenne_chunk']:.1f} caracteres")
            print(f"Derniere ingestion : {stats['date_derniere_ingestion']}")