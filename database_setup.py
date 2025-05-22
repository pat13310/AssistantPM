import sqlite3
import os

# Le chemin vers la base de données est relatif à l'emplacement de ce script.
# Si projects.db est à la racine du projet, et ce script aussi, alors c'est direct.
# Sinon, ajustez le chemin.
DATABASE_NAME = 'projects.db'
SCHEMA_PATH = 'schema.sql'

def create_tables():
    """
    Crée les tables dans la base de données SQLite en utilisant le schéma défini
    dans schema.sql.
    """
    conn = None  # Initialiser conn à None
    try:
        # Vérifier si le fichier de schéma existe
        if not os.path.exists(SCHEMA_PATH):
            print(f"Erreur : Le fichier de schéma '{SCHEMA_PATH}' n'a pas été trouvé.")
            return

        # Lire le contenu du fichier de schéma
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # Se connecter à la base de données SQLite
        # La base de données sera créée si elle n'existe pas encore.
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Exécuter les commandes SQL du schéma
        # Utiliser executescript pour exécuter plusieurs instructions SQL
        cursor.executescript(schema_sql)

        # Valider les changements
        conn.commit()
        print(f"Les tables ont été créées avec succès dans '{DATABASE_NAME}' en utilisant '{SCHEMA_PATH}'.")

    except sqlite3.Error as e:
        print(f"Erreur lors de la création des tables : {e}")
        if conn:
            conn.rollback()  # Annuler les changements en cas d'erreur
    except FileNotFoundError:
        print(f"Erreur : Le fichier de schéma '{SCHEMA_PATH}' n'a pas été trouvé lors de la lecture.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
    finally:
        # Fermer la connexion à la base de données
        if conn:
            conn.close()

if __name__ == '__main__':
    # Cette partie permet d'exécuter la fonction directement si le script est lancé.
    # Par exemple, python database_setup.py
    create_tables()
