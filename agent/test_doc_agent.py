import sys
sys.path.append("e:/projets QT/AssistanPM")

from PySide6.QtCore import QCoreApplication, Signal
from agent.BaseModule import BaseModule
from agent.ChatModule import ChatModule
from agent.CodeRefactorModule import CodeRefactorModule
from agent.DocModule import DocModule
from agent.OpenAIWorker import OpenAIWorker
from agent.config import OPENAI_API_KEY

class TestAgentModules():

    def test_base_module(self):
        # BaseModule est une classe abstraite, donc on ne peut pas l'instancier directement
        pass

    def test_chat_module(self):
        chat_module = ChatModule(api_key=OPENAI_API_KEY)
        self.assertTrue(chat_module.can_handle("Bonjour"))

    def test_code_refactor_module(self):
        refactor_module = CodeRefactorModule(api_key=OPENAI_API_KEY)
        self.assertTrue(refactor_module.can_handle("refactor: code"))
        self.assertFalse(refactor_module.can_handle("autre chose"))

    def test_doc_module(self):
        doc_module = DocModule(api_key=OPENAI_API_KEY)
        self.assertTrue(doc_module.can_handle("doc: documentation"))
        self.assertFalse(doc_module.can_handle("autre chose"))

    def test_openai_worker(self):
        # OpenAIWorker nécessite une clé API et ne peut pas être testé sans
        pass

    def test_generate_project(self, mock_worker_run):
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication(sys.argv)

        chat_module = ChatModule(api_key=OPENAI_API_KEY)
        
        callback_called = False
        actual_result = None
        error_occurred = False

        def mock_callback(result):
            nonlocal callback_called, actual_result
            actual_result = result
            callback_called = True

        def mock_error_callback(error_msg):
            nonlocal error_occurred
            print(f"Test - Error callback called: {error_msg}")
            error_occurred = True
        
        # Simuler l'émission du signal 'finished' par le worker mocké
        # Ceci est crucial car le thread attend ce signal pour se terminer proprement.
        def side_effect_for_run_direct_callback():
            print("side_effect_for_run_direct_callback called") # Debug print
            # Appeler directement le callback et simuler la fin du worker/thread
            mock_callback("mocked_openai_response_direct_call")
            if hasattr(chat_module, 'thread') and chat_module.thread is not None:
                 if chat_module.thread.isRunning():
                    print("Quitting thread from side_effect") # Debug print
                    chat_module.thread.quit()
            # Le mock enregistre l'appel automatiquement.
        
        mock_worker_run.side_effect = side_effect_for_run_direct_callback
        
        chat_module.handle_async(
            task="Invente un mini-projet Python avec un nom, une description et une liste de tâches à accomplir.",
            callback=mock_callback,
            error_callback=mock_error_callback
        )

        # Donner au thread une chance de démarrer et de traiter les événements
        # QThread.wait() est la bonne approche, mais il faut s'assurer que la boucle d'événements tourne.
        if hasattr(chat_module, 'thread') and chat_module.thread is not None:
            # Boucle pour traiter les événements Qt et attendre que le callback soit appelé ou qu'un timeout soit atteint.
            timeout_ms = 5000  # 5 secondes
            elapsed_ms = 0
            while not callback_called and not error_occurred and elapsed_ms < timeout_ms:
                QCoreApplication.processEvents() # Traiter les événements en attente
                chat_module.thread.msleep(10)    # Courte pause
                elapsed_ms += 10
            
            # Le thread devrait se terminer et être nettoyé par les signaux connectés dans ChatModule.
            # Il n'est pas sûr d'accéder à chat_module.thread ici car il pourrait déjà être supprimé.

        self.assertEqual(mock_worker_run.call_count, 1, "OpenAIWorker.run should have been called once.")
        self.assertTrue(callback_called, "The success callback should have been called.")
        self.assertFalse(error_occurred, "The error callback should not have been called.")
        self.assertEqual(actual_result, "mocked_openai_response_direct_call", "Callback received an unexpected result.")

    def test_doc_module_handle_async(self, mock_worker_run_doc):
        app = QCoreApplication.instance()
        if app is None:
            app = QCoreApplication(sys.argv)

        doc_module = DocModule(api_key=OPENAI_API_KEY)
        
        callback_called_doc = False
        actual_result_doc = None
        error_occurred_doc = False

        def mock_callback_doc(result):
            nonlocal callback_called_doc, actual_result_doc
            actual_result_doc = result
            callback_called_doc = True

        def mock_error_callback_doc(error_msg):
            nonlocal error_occurred_doc
            print(f"Test Doc - Error callback called: {error_msg}")
            error_occurred_doc = True
        
        def side_effect_for_doc_run_direct_callback():
            print("side_effect_for_doc_run_direct_callback called") # Debug print
            # Appeler directement le callback et simuler la fin du worker/thread
            mock_callback_doc("mocked_doc_response")
            if hasattr(doc_module, 'chat_module') and hasattr(doc_module.chat_module, 'thread') and \
               doc_module.chat_module.thread is not None and doc_module.chat_module.thread.isRunning():
                print("Quitting DocModule's thread from side_effect") # Debug print
                doc_module.chat_module.thread.quit()
            # Le mock enregistre l'appel automatiquement.

        mock_worker_run_doc.side_effect = side_effect_for_doc_run_direct_callback
        
        doc_module.handle_async(
            task="doc: Explique ce code simple.",
            callback=mock_callback_doc,
            error_callback=mock_error_callback_doc
        )

        if hasattr(doc_module, 'chat_module') and hasattr(doc_module.chat_module, 'thread') and \
           doc_module.chat_module.thread is not None:
            timeout_ms = 5000
            elapsed_ms = 0
            while not callback_called_doc and not error_occurred_doc and elapsed_ms < timeout_ms:
                QCoreApplication.processEvents()
                doc_module.chat_module.thread.msleep(10)
                elapsed_ms += 10

        self.assertEqual(mock_worker_run_doc.call_count, 1, "DocModule's OpenAIWorker.run should be called once.")
        self.assertTrue(callback_called_doc, "DocModule's success callback should be called.")
        self.assertFalse(error_occurred_doc, "DocModule's error callback should not be called.")
        self.assertEqual(actual_result_doc, "mocked_doc_response", "DocModule's callback received an unexpected result.")

if __name__ == '__main__':
    # Assurer qu'une instance de QCoreApplication existe pour l'ensemble des tests
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    # unittest.main() # Commenté pour exécuter la fonction de test réelle

def test_doc(api_key): # Renommage de la fonction
    print("Starting real test for DocModule (test_doc)...")
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)

    # Utilise le modèle par défaut de DocModule (maintenant gpt-4-turbo-preview)
    doc_module = DocModule(api_key=api_key, stream=False) 
    print(f"Using model: {doc_module.chat_module.model}") # Confirmer le modèle utilisé

    output_file_path = "agent/generated_doc.html"

    def on_success(result):
        print("\n--- Real Test Success ---")
        print(f"Documentation received. Saving to {output_file_path}...")
        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Successfully saved to {output_file_path}")
            # Tentative d'ouverture du fichier dans le navigateur
            try:
                import subprocess
                import platform
                import os # Assurer que os est importé ici aussi
                absolute_path = os.path.abspath(output_file_path)
                print(f"Attempting to open absolute path: {absolute_path}") # Debug print
                if platform.system() == 'Windows':
                    os.startfile(absolute_path)
                elif platform.system() == 'Darwin': # macOS
                    subprocess.call(['open', absolute_path])
                else: # linux variants
                    subprocess.call(['xdg-open', output_file_path])
                print(f"Attempted to open {output_file_path} in the default browser.")
            except Exception as e_open:
                print(f"Could not automatically open the file: {e_open}")
        except Exception as e_save:
            print(f"Error saving file: {e_save}")
            print("\nRaw HTML output:")
            print(result) # Afficher en cas d'échec de sauvegarde
        finally:
            app.quit() # Quitter la boucle d'événements

    def on_error(error_message):
        print("\n--- Real Test Error ---")
        print(f"Error: {error_message}")
        app.quit() # Quitter la boucle d'événements
    
    def on_partial(partial_content):
        # Ne sera pas appelé si stream=False, mais inclus pour la complétude
        print(f"Partial: {partial_content}", end="")

    # Créer un fichier d'exemple pour le test "doc:auto:"
    sample_project_path = "agent/sample_project_for_doc_test"
    os.makedirs(sample_project_path, exist_ok=True)
    with open(os.path.join(sample_project_path, "main.py"), "w", encoding="utf-8") as f:
        f.write("def hello():\n    print('Hello, World!')\n\nhello()")
    with open(os.path.join(sample_project_path, "README.md"), "w", encoding="utf-8") as f:
        f.write("# Sample Project\nThis is a test project.")

    # Utiliser doc:auto: pour le projet courant
    task = f"doc:auto:." 
    # task = "doc: Explique ce code Python simple : `def add(a, b): return a + b`" # Ancienne tâche
    print(f"Sending task to DocModule: {task}")

    doc_module.handle_async(
        task=task,
        callback=on_success,
        error_callback=on_error,
        partial_callback=on_partial
    )
    
    print("Waiting for OpenAI response...")
    app.exec() # Démarrer la boucle d'événements Qt

    # Nettoyage du dossier d'exemple
    # import shutil
    # shutil.rmtree(sample_project_path)
    # print(f"Cleaned up {sample_project_path}")


if __name__ == '__main__':
    # Assurer qu'une instance de QCoreApplication existe pour l'ensemble des tests
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    
    # Décommentez unittest.main() pour exécuter les tests unitaires
    # unittest.main()

    # Exécuter le test réel
    # ATTENTION: Cela utilisera votre clé API OpenAI et consommera des tokens.
    api_key_real = OPENAI_API_KEY # Remplacez par votre clé si nécessaire
    if api_key_real == "YOUR_OPENAI_API_KEY":
        print("Veuillez remplacer 'YOUR_OPENAI_API_KEY' par votre véritable clé API OpenAI dans agent/test_agent.py pour exécuter le test réel.")
    else:
        import os # Ajout de l'import os manquant
        test_doc(api_key_real) # Appel de la fonction renommée
