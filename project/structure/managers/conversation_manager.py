import os
import json
import datetime
import uuid
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtCore import Qt

class ConversationManager:
    """Classe de gestion des conversations"""
    
    @staticmethod
    def export_conversation(widget):
        """Exporter la conversation actuelle dans un fichier"""
        if not widget.current_conversation:
            QMessageBox.information(
                widget, "Information", "Aucune conversation à exporter."
            )
            return

        # Demander à l'utilisateur où sauvegarder le fichier
        file_path, _ = QFileDialog.getSaveFileName(
            widget,
            "Exporter la conversation",
            os.path.join(os.path.expanduser("~"), "conversation.json"),
            "Fichiers JSON (*.json);;Fichiers texte (*.txt);;Tous les fichiers (*.*)",
        )

        if not file_path:
            return  # L'utilisateur a annulé

        try:
            # Préparer les données de la conversation
            conversation_data = {
                "id": widget.current_conversation_id,
                "timestamp": datetime.datetime.now().isoformat(),
                "messages": widget.current_conversation,
            }

            # Sauvegarder selon le format choisi
            if file_path.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(conversation_data, f, ensure_ascii=False, indent=2)
            else:  # Format texte
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(
                        f"Conversation du {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
                    )
                    for msg in widget.current_conversation:
                        sender = "Vous" if msg["is_user"] else "IA"
                        f.write(f"[{sender}] {msg['text']}\n\n")

            QMessageBox.information(
                widget, "Succès", f"Conversation exportée avec succès vers {file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                widget, "Erreur", f"Erreur lors de l'exportation: {str(e)}"
            )
    
    @staticmethod
    def clear_conversation(widget):
        """Effacer la conversation actuelle"""
        if not widget.current_conversation:
            return

        # Créer une boîte de dialogue de confirmation personnalisée
        msgBox = QMessageBox(widget)
        msgBox.setWindowTitle("Confirmation")
        msgBox.setText("Voulez-vous vraiment effacer cette conversation ?")
        msgBox.setIcon(QMessageBox.Question)

        # Créer les boutons en français
        boutonOui = msgBox.addButton("Oui", QMessageBox.YesRole)
        boutonNon = msgBox.addButton("Non", QMessageBox.NoRole)
        msgBox.setDefaultButton(boutonNon)  # Définir "Non" comme bouton par défaut

        # Afficher la boîte de dialogue et récupérer la réponse
        msgBox.exec()

        # Vérifier si le bouton "Oui" a été cliqué
        if msgBox.clickedButton() == boutonOui:
            # Sauvegarder la conversation actuelle dans l'historique
            ConversationManager.save_current_conversation(widget)

            # Effacer les widgets de la conversation
            for i in reversed(range(widget.chat_layout.count())):
                item = widget.chat_layout.itemAt(i).widget()
                if item:
                    item.setParent(None)

            # Créer une nouvelle conversation
            widget.current_conversation_id = str(uuid.uuid4())
            widget.current_conversation = []

            # Ajouter un message de bienvenue
            widget.add_chat_bubble(
                "<b>Nouvelle conversation commencée.</b>", is_user=False
            )
    
    @staticmethod
    def save_current_conversation(widget):
        """Sauvegarder la conversation actuelle dans l'historique"""
        if not widget.current_conversation:
            return

        # Préparer les données de la conversation
        conversation_data = {
            "id": widget.current_conversation_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "preview": ConversationManager.get_conversation_preview(widget),
            "messages": widget.current_conversation,
        }

        # Ajouter à l'historique (en limitant à 20 conversations)
        widget.conversation_history.append(conversation_data)
        if len(widget.conversation_history) > 20:
            widget.conversation_history.pop(0)  # Supprimer la plus ancienne
    
    @staticmethod
    def get_conversation_preview(widget):
        """Obtenir un aperçu de la conversation pour l'historique"""
        if not widget.current_conversation:
            return "Conversation vide"

        # Trouver le premier message utilisateur
        for msg in widget.current_conversation:
            if msg["is_user"]:
                # Tronquer si nécessaire
                preview = msg["text"]
                if len(preview) > 50:
                    preview = preview[:47] + "..."
                return preview

        return "Conversation sans message utilisateur"
    
    @staticmethod
    def show_history(widget):
        """Afficher l'historique des conversations"""
        if not widget.conversation_history:
            QMessageBox.information(
                widget, "Historique", "Aucune conversation dans l'historique."
            )
            return

        # Créer une fenêtre pour afficher l'historique
        history_dialog = QMessageBox(widget)
        history_dialog.setWindowTitle("Historique des conversations")

        # Préparer le texte de l'historique
        history_text = "<h3>Historique des conversations</h3><ul>"
        for i, conv in enumerate(reversed(widget.conversation_history)):
            timestamp = datetime.datetime.fromisoformat(conv["timestamp"]).strftime(
                "%d/%m/%Y %H:%M"
            )
            preview = conv["preview"]
            history_text += f"<li><b>{timestamp}</b>: {preview}</li>"
        history_text += "</ul>"

        history_dialog.setText(history_text)
        history_dialog.setTextFormat(Qt.RichText)
        history_dialog.exec_()
