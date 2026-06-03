import os

# ==========================================
# CONFIGURATION
# ==========================================
# Le dossier de sortie (le fichier texte final)
OUTPUT_FILE = "project_extract_back.txt"

# Les dossiers à ignorer ABSOLUMENT (pour ne pas faire crasher l'extraction)
IGNORE_DIRS = {'.venv', '__pycache__', '.git', '.idea', 'node_modules', 'alembic'}

# Les extensions de fichiers qu'on veut garder
ALLOWED_EXTENSIONS = {'.py', '.sql', '.json', '.md', '.toml', '.env.example','.html','.ts','.scss','.spec','.tsx','.mjs'}


# ==========================================
# SCRIPT
# ==========================================
def extract_project():
    print("⏳ Début de l'extraction...")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        # On parcourt tous les dossiers à partir d'ici
        for root, dirs, files in os.walk("../../PycharmProjects/APP_BACKEND"):

            # On supprime de la liste les dossiers qu'on veut ignorer
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

            for file in files:
                ext = os.path.splitext(file)[1].lower()

                # Si le fichier a la bonne extension et n'est pas le script lui-même
                if ext in ALLOWED_EXTENSIONS and file != os.path.basename(__file__) and file != OUTPUT_FILE:
                    filepath = os.path.join(root, file)

                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()

                            # On crée un bel en-tête pour chaque fichier
                            outfile.write(f"\n{'=' * 80}\n")
                            outfile.write(f"FILE: {filepath}\n")
                            outfile.write(f"{'=' * 80}\n\n")

                            outfile.write(content)
                            outfile.write("\n")
                            print(f"✅ Ajouté : {filepath}")
                    except Exception as e:
                        print(f"❌ Erreur sur {filepath}: {e}")

    print(f"\n🎉 Extraction terminée ! Tout est dans le fichier : {OUTPUT_FILE}")


if __name__ == "__main__":
    extract_project()