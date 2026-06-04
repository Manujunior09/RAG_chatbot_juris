import os
from app.ingestion.ingester import ingest, get_stats

if __name__ == "__main__":
    docs_folder = "documents"
    if not os.path.exists(docs_folder):
        os.makedirs(docs_folder)
        print(f"Dossier {docs_folder} créé. Placez-y vos documents.")
    else:
        files = [f for f in os.listdir(docs_folder) if os.path.isfile(os.path.join(docs_folder, f))]
        if not files:
            print(f"Aucun fichier dans {docs_folder}.")
        else:
            for filename in files:
                try:
                    ingest(os.path.join(docs_folder, filename))
                except Exception as e:
                    print(f"Erreur {filename} : {e}")

            stats = get_stats()
            print("\n=== Statistiques ===")
            print(f"Total chunks     : {stats['total_chunks']}")
            print(f"Documents        : {stats['documents']}")
            print(f"Taille moy. chunk: {stats['taille_moyenne_chunk']:.1f} chars")
            print(f"Dernière ingestion: {stats['date_derniere_ingestion']}")
