import asyncio
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QMessageBox,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import (
    Qt,
    Slot as pyqtSlot,
)  # Renommer Slot en pyqtSlot pour la compatibilité du code existant
from functools import partial
import os
import re  # Importer re pour la modification du markdown


class MarkdownCoherenceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Analyseur de Cohérence Markdown")
        from agent.MarkdownCoherenceAgent import MarkdownCoherenceAgent

        self.agent = MarkdownCoherenceAgent()
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.analyze_button = QPushButton("Analyser context.md")
        self.analyze_button.clicked.connect(self._run_analysis)
        layout.addWidget(self.analyze_button)

        self.apply_and_reanalyze_button = QPushButton(
            "Appliquer décisions et Ré-analyser"
        )
        self.apply_and_reanalyze_button.clicked.connect(self._apply_and_reanalyze)
        layout.addWidget(self.apply_and_reanalyze_button)
        self.apply_and_reanalyze_button.setEnabled(False)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.results_widget)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)
        self.resize(700, 500)
        self.decision_widgets = {}
        self.validated_decisions = (
            {}
        )  # Pour les choix qui modifient le fichier (backend, db)
        self.ignored_advisories = (
            set()
        )  # Pour stocker les catégories des conseils ignorés

    def _clear_results_layout(self):
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.decision_widgets.clear()

    @pyqtSlot()
    def _run_analysis(self):
        self._clear_results_layout()
        placeholder_label = QLabel("Analyse en cours...")
        placeholder_label.setObjectName("placeholder_label")
        self.results_layout.addWidget(placeholder_label)
        self.analyze_button.setEnabled(False)
        markdown_file_path = os.path.join("context", "context.md")

        if not os.path.exists(markdown_file_path):
            self._show_error(
                f"Le fichier Markdown '{markdown_file_path}' n'a pas été trouvé."
            )
            placeholder = self.results_widget.findChild(QLabel, "placeholder_label")
            if placeholder:
                placeholder.deleteLater()
            self.results_layout.addWidget(QLabel("Fichier non trouvé."))
            self.analyze_button.setEnabled(True)
            return
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                self.agent.handle_async(
                    task=f"analyser markdown {markdown_file_path}",
                    callback=self._on_analysis_complete,
                    error_callback=self._on_analysis_error,
                )
            )
        except Exception as e:
            self._show_error(f"Erreur lancement analyse: {e}")
            placeholder = self.results_widget.findChild(QLabel, "placeholder_label")
            if placeholder:
                placeholder.deleteLater()
            self.results_layout.addWidget(QLabel("Erreur lancement analyse."))
            self.analyze_button.setEnabled(True)

    @pyqtSlot(list)
    def _on_analysis_complete(self, results: list):
        self._clear_results_layout()

        processed_results = []
        if results:
            for item in results:
                if isinstance(item, dict):
                    category = item.get("category")
                    # Ne pas afficher si la catégorie est dans les ignorés ET que ce n'est pas une decision_needed
                    # (on veut toujours afficher les decision_needed même si une action a été prise dessus avant,
                    # car l'état du fichier a pu changer)
                    if (
                        category
                        and category in self.ignored_advisories
                        and item.get("type") != "decision_needed"
                    ):
                        print(
                            f"Conseil ignoré pour la catégorie '{category}', non affiché."
                        )
                        continue
                    processed_results.append(item)
                else:
                    processed_results.append(str(item))  # Garder les chaînes simples

        if not processed_results:
            self.results_layout.addWidget(
                QLabel(
                    "Aucun résultat d'analyse (ou tous les conseils ont été ignorés)."
                )
            )
        else:
            for (
                item_display_data
            ) in processed_results:  # itérer sur les résultats traités
                if isinstance(item_display_data, dict):
                    self._display_structured_item(item_display_data)
                else:
                    self.results_layout.addWidget(QLabel(item_display_data))

        self.analyze_button.setEnabled(True)

    def _display_structured_item(self, item_data: dict):
        item_frame = QFrame()
        item_frame.setFrameShape(QFrame.Shape.StyledPanel)
        item_layout = QVBoxLayout(item_frame)
        msg = f"<b>{item_data.get('type', 'Info').capitalize()}</b>: {item_data.get('message', 'N/A')}"
        message_label = QLabel(msg)
        message_label.setWordWrap(True)
        item_layout.addWidget(message_label)

        if item_data.get("details"):
            details_label = QLabel(f"<i>{item_data.get('details')}</i>")
            details_label.setWordWrap(True)
            item_layout.addWidget(details_label)

        category = item_data.get("category")
        if item_data.get("type") == "decision_needed" and item_data.get("options"):
            options_group = QButtonGroup(self)
            # Stocker item_data pour y accéder plus tard dans _validate_decision
            self.decision_widgets[category] = {
                "group": options_group,
                "item_data": item_data,
            }
            item_layout.addWidget(QLabel("Veuillez faire un choix :"))
            for option_text in item_data.get("options"):
                radio_button = QRadioButton(option_text)
                options_group.addButton(radio_button)
                item_layout.addWidget(radio_button)
            validate_button = QPushButton(f"Valider choix pour '{category}'")
            # Passer la catégorie pour retrouver les infos
            validate_button.clicked.connect(partial(self._validate_decision, category))
            item_layout.addWidget(validate_button)
        elif item_data.get("suggested_actions"):
            item_layout.addWidget(QLabel("Actions suggérées :"))
            for action_text in item_data.get("suggested_actions"):
                action_button = QPushButton(action_text)
                action_button.clicked.connect(
                    partial(
                        self._handle_suggested_action, category, action_text, item_data
                    )
                )
                item_layout.addWidget(action_button)
        self.results_layout.addWidget(item_frame)

    def _handle_suggested_action(
        self, category: str, action_taken: str, item_data: dict
    ):
        QMessageBox.information(
            self,
            "Action enregistrée",
            f"Pour '{category}', action '{action_taken}' enregistrée.\n",
        )

        if "ignorer" in action_taken.lower():  # Si l'action est d'ignorer
            self.ignored_advisories.add(category)
            print(f"Catégorie '{category}' ajoutée aux ignorés.")
            # Relancer l'affichage pour masquer l'élément ignoré immédiatement
            # Cela nécessite de stocker les résultats bruts de l'agent pour les retraiter
            # Pour l'instant, l'effet ne sera visible qu'après une ré-analyse complète.
            # Ou on peut simplement masquer le frame de cet item:
            sender_button = self.sender()
            if sender_button and isinstance(sender_button, QPushButton):
                parent_frame = sender_button.parentWidget()
                if parent_frame and isinstance(parent_frame, QFrame):
                    # parent_frame.setVisible(False) # Masque l'item
                    # Plutôt que de masquer, on va compter sur la prochaine ré-analyse ou le filtrage
                    pass

        # Les actions autres qu'ignorer ne sont pas stockées dans validated_decisions pour l'instant,
        # car _update_markdown_file ne les traite pas pour modifier le fichier.
        # Si on voulait qu'elles soient "effacées" de la liste des choses à faire par _apply_and_reanalyze,
        # il faudrait les ajouter à self.validated_decisions avec un type distinct.
        # Pour l'instant, seul "ignorer" a un effet persistant (via self.ignored_advisories).

        # Activer le bouton si des décisions modifiant le fichier sont en attente,
        # ou si une action a été prise (même ignorer, pour permettre de relancer l'analyse et voir l'effet).
        self.apply_and_reanalyze_button.setEnabled(True)

    def _validate_decision(
        self, category: str
    ):  # category est la clé pour decision_widgets
        decision_widget_info = self.decision_widgets.get(category)
        if decision_widget_info:
            button_group = decision_widget_info["group"]
            item_data = decision_widget_info["item_data"]  # Récupérer item_data
            selected_button = button_group.checkedButton()
            if selected_button:
                chosen_option = selected_button.text()
                # Stocker la phase et la question avec la décision
                self.validated_decisions[category] = {
                    "choice": chosen_option,
                    "phase": item_data.get("phase"),
                    "question": item_data.get("question"),
                }
                QMessageBox.information(
                    self,
                    "Choix enregistré",
                    f"Pour '{category}', choix '{chosen_option}' enregistré.",
                )
                self.apply_and_reanalyze_button.setEnabled(True)
                for widget in button_group.buttons():
                    widget.setEnabled(False)
                # Désactiver aussi le bouton de validation lui-même
                sender_button = self.sender()
                if sender_button and isinstance(sender_button, QPushButton):
                    sender_button.setEnabled(False)
            else:
                QMessageBox.warning(
                    self, "Aucun choix", f"Sélectionnez une option pour '{category}'."
                )
        else:
            QMessageBox.critical(
                self, "Erreur", f"Infos de décision non trouvées pour '{category}'."
            )

    @pyqtSlot()
    def _apply_and_reanalyze(self):
        file_updated_successfully = (
            True  # Par défaut à True si aucune modification de fichier n'est nécessaire
        )

        if self.validated_decisions:  # S'il y a des décisions qui modifient le fichier
            markdown_file_path = os.path.join("context", "context.md")
            success = self._update_markdown_file(
                markdown_file_path, self.validated_decisions
            )

            if success:
                QMessageBox.information(
                    self,
                    "Mise à jour du fichier",
                    "Le fichier context.md a été mis à jour avec vos choix.",
                )
                self.validated_decisions.clear()  # Effacer seulement si la mise à jour a réussi
            else:
                self._show_error(
                    "Erreur lors de la mise à jour du fichier Markdown. Les modifications n'ont pas été appliquées."
                )
                file_updated_successfully = False
                # Ne pas effacer validated_decisions pour permettre une nouvelle tentative ou correction manuelle
                # Ne pas relancer l'analyse automatiquement si l'écriture a échoué.
                return
        else:
            QMessageBox.information(
                self,
                "Aucune modification de fichier",
                "Aucune décision modifiant le fichier n'était en attente. Relance de l'analyse pour refléter les actions (ex: ignorer).",
            )

        # Toujours désactiver le bouton et relancer l'analyse si on arrive ici
        # (soit la mise à jour a réussi, soit il n'y avait rien à mettre à jour dans le fichier)
        self.apply_and_reanalyze_button.setEnabled(False)
        self._run_analysis()  # Relancer pour voir l'effet des ignorés et des modifications de fichier

    def _update_markdown_file(self, file_path: str, decisions: dict) -> bool:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Erreur lecture {file_path}: {e}")
            return False

        modified_content = content

        for category, decision_data in decisions.items():
            # Vérifier d'abord si c'est une action ou un choix
            if decision_data.get("action_taken"):
                action = decision_data.get("action_taken")
                target_phase_title_for_action = decision_data.get("phase")
                target_question_text_for_action = decision_data.get("question")
                print(
                    f"Action '{action}' pour catégorie '{category}' (Phase: {target_phase_title_for_action}, Question: {target_question_text_for_action}). Modification de fichier non implémentée pour cette action."
                )
                continue  # Passer à la décision suivante, car on ne modifie pas le fichier pour les actions ici

            # Si ce n'est pas une action, alors c'est un choix, on peut accéder à "choice"
            chosen_option = decision_data.get(
                "choice"
            )  # Utiliser .get pour plus de sûreté
            target_phase_title = decision_data.get("phase")
            target_question_text = decision_data.get("question")

            if not chosen_option or not target_phase_title or not target_question_text:
                print(
                    f"Données manquantes pour la décision sur '{category}' (Phase: {target_phase_title}, Q: {target_question_text}). Impossible de mettre à jour."
                )
                continue

            # Préparer la nouvelle réponse formatée
            new_response_text = ""
            if category == "tech_stack_backend":
                new_response_text = f"Backend: {chosen_option}"
            elif category == "tech_stack_database":
                new_response_text = f"Base de données: {chosen_option}"
            else:
                print(
                    f"Logique de formatage de réponse non implémentée pour la catégorie: {category}"
                )
                continue  # Ne pas essayer de modifier si on ne sait pas comment formater

            # Construire une regex pour trouver la section de la question et remplacer sa réponse
            # Pattern: (## Phase\s*:\s*TITRE_PHASE\s*\n(?:(?:(?!^##\s*Phase\s*:\s*|###\s*).*\n)*)###\s*TITRE_QUESTION\s*\n)(?:(?:(?!^##\s*Phase\s*:\s*|###\s*).*\n)*)
            # Ce pattern est complexe. Simplifions pour l'instant en cherchant la question et en remplaçant la ligne suivante.
            # Cela suppose que la réponse est sur une seule ligne et est la ligne *immédiatement* après la question.
            # Et que la réponse à remplacer est spécifique (par ex. "Backend: ..." ou "Base de données: ...")

            # Regex pour trouver la ligne de la question
            escaped_phase_title = re.escape(target_phase_title)
            escaped_question_text = re.escape(target_question_text)

            # Pattern pour trouver la question dans la bonne phase et remplacer la ligne de réponse spécifique
            # (## Phase : Conception\n(?:.*\n)*?### Quelles technologies et frameworks utiliser\?\n)(Backend: .*)
            # (## Phase : Conception\n(?:.*\n)*?### Quelles technologies et frameworks utiliser\?\n(?:.*\n)*?)(Base de données: .*)

            # On va essayer de remplacer la ligne spécifique (Backend: ou Base de données:)
            # à l'intérieur de la bonne phase et question. C'est toujours délicat.

            # Nouvelle approche: itérer sur les lignes et modifier en place
            temp_lines = modified_content.splitlines()
            output_lines = []
            in_target_phase = False
            in_target_question = False
            response_modified_for_current_decision = False

            for line_idx, current_line in enumerate(temp_lines):
                stripped_line = current_line.strip()

                # Détection de phase
                phase_match = re.match(
                    r"^##\s*Phase\s*:\s*(.+)$", stripped_line, re.IGNORECASE
                )
                if phase_match:
                    current_phase_name = phase_match.group(1).strip()
                    in_target_phase = (
                        current_phase_name.lower() == target_phase_title.lower()
                    )
                    in_target_question = False  # Réinitialiser si on change de phase

                # Détection de question
                question_match = re.match(r"^###\s*(.+)$", stripped_line, re.IGNORECASE)
                if question_match:
                    current_question_name = question_match.group(1).strip()
                    if (
                        in_target_phase
                        and current_question_name.lower()
                        == target_question_text.lower()
                    ):
                        in_target_question = True
                        output_lines.append(
                            current_line
                        )  # Ajouter la ligne de la question

                        # Remplacer la réponse pour les catégories gérées
                        if not response_modified_for_current_decision:
                            if category == "tech_stack_backend":
                                # Chercher la ligne "Backend:" dans les lignes suivantes immédiates
                                # et la remplacer. C'est encore une simplification.
                                # Idéalement, il faudrait parser la réponse multiligne.
                                for next_line_idx in range(
                                    line_idx + 1, len(temp_lines)
                                ):
                                    if (
                                        temp_lines[next_line_idx]
                                        .strip()
                                        .lower()
                                        .startswith("backend:")
                                    ):
                                        output_lines.append(f"{new_response_text}\n")
                                        temp_lines[next_line_idx] = (
                                            ""  # Marquer comme traitée pour ne pas la rajouter
                                        )
                                        response_modified_for_current_decision = True
                                        print(
                                            f"Remplacement pour backend: {chosen_option}"
                                        )
                                        break
                                    elif temp_lines[next_line_idx].strip().startswith(
                                        "###"
                                    ) or temp_lines[next_line_idx].strip().startswith(
                                        "##"
                                    ):
                                        # On a atteint une autre question/phase avant de trouver la ligne Backend
                                        output_lines.append(
                                            f"{new_response_text}\n"
                                        )  # Ajouter la nouvelle réponse
                                        response_modified_for_current_decision = True
                                        print(
                                            f"Ajout pour backend (ligne non trouvée): {chosen_option}"
                                        )
                                        break
                                if (
                                    not response_modified_for_current_decision
                                ):  # Si on n'a pas trouvé la ligne à remplacer
                                    output_lines.append(f"{new_response_text}\n")
                                    response_modified_for_current_decision = True
                                    print(f"Ajout forcé pour backend: {chosen_option}")

                            elif category == "tech_stack_database":
                                for next_line_idx in range(
                                    line_idx + 1, len(temp_lines)
                                ):
                                    if (
                                        temp_lines[next_line_idx]
                                        .strip()
                                        .lower()
                                        .startswith("base de données:")
                                    ):
                                        output_lines.append(f"{new_response_text}\n")
                                        temp_lines[next_line_idx] = ""
                                        response_modified_for_current_decision = True
                                        print(
                                            f"Remplacement pour database: {chosen_option}"
                                        )
                                        break
                                    elif temp_lines[next_line_idx].strip().startswith(
                                        "###"
                                    ) or temp_lines[next_line_idx].strip().startswith(
                                        "##"
                                    ):
                                        output_lines.append(f"{new_response_text}\n")
                                        response_modified_for_current_decision = True
                                        print(
                                            f"Ajout pour database (ligne non trouvée): {chosen_option}"
                                        )
                                        break
                                if not response_modified_for_current_decision:
                                    output_lines.append(f"{new_response_text}\n")
                                    response_modified_for_current_decision = True
                                    print(f"Ajout forcé pour database: {chosen_option}")
                            else:
                                # Catégorie non gérée, ne rien faire pour la réponse
                                pass  # La ligne de question a été ajoutée, la réponse originale suivra
                        continue  # On a traité la ligne de question et sa réponse (ou pas)

                    else:  # Autre question, réinitialiser
                        in_target_question = False

                # Si on est dans la réponse d'une question cible et qu'on a déjà remplacé, skipper les anciennes lignes
                if in_target_question and response_modified_for_current_decision:
                    if not (
                        stripped_line.startswith("###")
                        or stripped_line.startswith("##")
                    ):
                        # C'est une ancienne ligne de réponse, on la skippe si elle n'est pas vide (marquée par "" plus haut)
                        if temp_lines[line_idx] != "":
                            pass  # print(f"Skipping old response line: {current_line.strip()}")
                        if (
                            temp_lines[line_idx] == ""
                        ):  # Si elle a été marquée vide, ne pas l'ajouter
                            continue
                    else:  # Nouvelle question/phase, fin de la réponse
                        in_target_question = False
                        # response_modified_for_current_decision = False # Sera réinitialisé au début de la boucle for category

                if (
                    temp_lines[line_idx] != ""
                ):  # N'ajoute pas les lignes marquées comme vides
                    output_lines.append(current_line)

            modified_content = "".join(output_lines)
            # Réinitialiser pour la prochaine *décision* dans la boucle for category
            # La variable response_modified_for_current_decision est locale à cette itération de la boucle externe.

        if modified_content != content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                print(f"Fichier {file_path} mis à jour.")
                return True
            except Exception as e:
                print(f"Erreur écriture {file_path}: {e}")
                return False
        else:
            # Aucune modification n'a été faite (peut-être parce que les patterns n'ont pas matché)
            # ou que la logique pour la catégorie n'est pas là.
            # On peut considérer cela comme un succès partiel ou un non-changement.
            print("Aucune modification effective du contenu du fichier.")
            return True  # Retourner True pour permettre la ré-analyse

    @pyqtSlot(str)
    def _on_analysis_error(self, error_message: str):
        self._clear_results_layout()
        self._show_error(error_message)
        self.analyze_button.setEnabled(True)

    def _show_error(self, message: str):
        error_label = QLabel(f"<font color='red'>Erreur : {message}</font>")
        self.results_layout.addWidget(error_label)
        QMessageBox.critical(self, "Erreur d'analyse", message)


if __name__ == "__main__":
    import sys

    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    from PySide6.QtWidgets import QApplication

    mock_context_dir = "context"
    mock_context_file = os.path.join(mock_context_dir, "context.md")

    # Définir le contenu standard du fichier de test
    mock_content = """# Projet : Test Widget Projet
## Phase : Conception
### Quelles technologies et frameworks utiliser?
Backend: Node.js, Java Spring, Python/Django
Base de données: PostgreSQL, MongoDB
Frontend: React
### Quelle architecture logicielle adopter pour le projet?
Microservices
## Phase : Développement
### Comment garantir la sécurité de l'application?
Validation des entrées.
## Phase : Tests
### Quels outils de test utiliser?
Jest, Mocha
"""
    # S'assurer que le répertoire existe
    os.makedirs(mock_context_dir, exist_ok=True)

    # Toujours (ré)écrire le fichier avec le contenu défini
    try:
        with open(mock_context_file, "w", encoding="utf-8") as f:
            f.write(mock_content)
        print(
            f"Fichier de test '{mock_context_file}' (ré)écrit avec le contenu initial."
        )
    except Exception as e:
        print(
            f"Erreur lors de l'écriture du fichier de test '{mock_context_file}': {e}"
        )

    app = QApplication(sys.argv)
    widget = MarkdownCoherenceWidget()
    widget.show()
    sys.exit(app.exec())
