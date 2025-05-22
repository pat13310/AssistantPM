from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
)
from PySide6.QtCore import Qt, Signal, QSettings
import os  # Ajout de l'import os
from components.infos.InfoBox import InfoBox
from components.InfoButton import InfoButton
from components.Step.PhaseStepBar import PhaseStepBar
from components.infos.models import ProjectData, Phase, Question
from components.dialogues.AnalyseProjectDlg import AnalyseProjectDlg # Ajout de l'import


class PhaseWizardWidget(QWidget):
    completed = Signal(ProjectData)

    def __init__(self, project: ProjectData, parent=None):
        super().__init__(parent)
        self.project = project
        self.phase_index = 0
        self.question_index = 0
        self.settings = QSettings("AssistantIA", "PhaseWizard")

        self.setStyleSheet(
            "background-color: white; font-family: 'Segoe UI'; font-size: 14px; border-radius: 8px; border: 1px solid #d1d5db; color: #374151;"
        )
        # self.setMinimumSize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSizePolicy(sizePolicy)

        self.init_ui()
        self.load_question()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        try:
            self.step_bar = PhaseStepBar(
                self.current_phase().title, len(self.current_phase().questions)
            )
            self.step_bar.stepClicked.connect(self.jump_to_question)
            self.layout.addWidget(self.step_bar)
        except Exception as e:
            print(f"Error creating step_bar: {e}")
            self.step_bar = None

        title_layout = QHBoxLayout()
        self.label_question = QLabel()
        self.label_question.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #666; border: none;"
        )
        self.label_question.setWordWrap(False)

        self.info_button = InfoButton()
        self.info_button.toggled.connect(self.toggle_info_box)

        title_layout.addWidget(self.label_question)
        title_layout.addStretch()
        title_layout.addWidget(self.info_button)
        self.layout.addLayout(title_layout)

        self.info_box = InfoBox([], "")
        self.info_box.setVisible(False)
        self.layout.addWidget(self.info_box)
        self.info_box.suggestionClicked.connect(self.insert_suggestion)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Entrez votre réponse ici…")
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout.addWidget(self.text_edit)
        self.text_edit.setStyleSheet(
            """
            QTextEdit {
                font-size: 14px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 10px;
                background-color: #f9fafb;
                color: #374151;                                     
            }
            QTextEdit:focus {
                border: 2px solid #caf9c7;
                background-color: #ffffff;
            }
            QTextEdit:hover {
                border: 2px solid #e5f9c7;
                background-color: #ffffff;
            }
        """
        )
        self.layout.addWidget(self.text_edit)

        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("⮜ Précédent")
        self.btn_next = QPushButton("Suivant ⮞")
        for btn in (self.btn_prev, self.btn_next):
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                """
                QPushButton {
                    color: white;
                    font-weight: bold;
                    padding: 8px 24px;
                    border-radius: 8px;
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #4CAF50, stop:1 #81C784
                    );
                }
                QPushButton:hover {
                    background: qlineargradient(
                        x1:0, y1:0, x2:1, y2:0,
                        stop:0 #43A047, stop:1 #66BB6A
                    );
                }
                
            """
            )
        self.btn_prev.clicked.connect(self.prev)
        self.btn_next.clicked.connect(self.next)
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addStretch()
        nav_layout.addWidget(self.btn_next)

        self.btn_reset = QPushButton("Réinitialiser")
        self.btn_reset.setObjectName("Reinit")
        self.btn_reset.setFixedHeight(30)
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet(
            """
            QPushButton#Reinit {
                color: #ef4444;
                font-weight: bold;
                padding: 6px 18px;
                border-radius: 8px;
                background-color: #fef2f2;
                border: 1px solid #fecaca;
            }
            QPushButton#Reinit:hover {
                background-color: #fee2e2;
            }
        """
        )
        self.btn_reset.clicked.connect(self.reset_answers)
        self.layout.addWidget(self.btn_reset, alignment=Qt.AlignRight)

        self.layout.addStretch()
        self.layout.addLayout(nav_layout)

    def current_phase(self) -> Phase:
        return self.project.phases[self.phase_index]

    def current_question(self) -> Question:
        return self.current_phase().questions[self.question_index]

    def get_settings_key(self) -> str:
        return f"{self.project.name}/{self.current_phase().id}/{self.current_question().id}"

    def load_question(self):
        print(
            f"load_question: phase_index={self.phase_index}, question_index={self.question_index}"
        )
        if not self.project.phases:
            print("load_question: no phases in project")
            return

        phase = self.current_phase()
        if not phase.questions:
            print("load_question: no questions in phase")
            return

        question = self.current_question()

        print(f"load_question: phase={phase.title}, question={question.text}")

        self.step_bar.set_phase_title(phase.title)
        self.label_question.setText(question.text)
        self.info_button.setChecked(True)
        self.info_box.setVisible(True)
        self.info_box.update_content(
            question.suggestions,
            question.bestPractices,
            getattr(question, "sousSuggestions", {}),
        )

        key = self.get_settings_key()
        saved = self.settings.value(key, "")
        self.text_edit.setText(saved)

        if self.project.phases:
            self.btn_prev.setEnabled(
                not (self.phase_index == 0 and self.question_index == 0)
            )
            self.btn_next.setText(
                "Terminer ✔" if self.is_last_question() else "Suivant ⮞"
            )

            self.step_bar.update_active(self.question_index)
            self.step_bar.set_answered(
                [bool(q.response) for q in self.current_phase().questions]
            )

    def is_last_question(self):
        if not self.project.phases:
            return False
        return (
            self.phase_index == len(self.project.phases) - 1
            and self.question_index == len(self.current_phase().questions) - 1
        )

    def toggle_info_box(self, checked: bool):
        self.info_box.setVisible(checked)

    def insert_suggestion(self, text: str):
        current = self.text_edit.toPlainText().strip()
        if text not in current:
            self.text_edit.append(text)

    def save_response(self):
        answer = self.text_edit.toPlainText().strip()
        self.current_question().response = answer
        self.settings.setValue(self.get_settings_key(), answer)

    def next(self):
        self.save_response()
        print(
            f"next: phase_index={self.phase_index}, question_index={self.question_index}"
        )
        if self.question_index + 1 < len(self.current_phase().questions):
            self.question_index += 1
        elif self.phase_index + 1 < len(self.project.phases):
            self.phase_index += 1
            self.question_index = 0
        else:
            self.finish()
            return
        self.load_question()
        print(
            f"next: after load_question phase_index={self.phase_index}, question_index={self.question_index}"
        )

    def prev(self):
        print(
            f"prev: phase_index={self.phase_index}, question_index={self.question_index}"
        )
        if self.question_index > 0:
            self.question_index -= 1
        elif self.phase_index > 0:
            self.phase_index -= 1
            self.question_index = len(self.current_phase().questions) - 1
        self.load_question()

    def go_to_step(self, phase_index, question_index):
        print(f"go_to_step: phase_index={phase_index}, question_index={question_index}")
        self.save_response()
        self.phase_index = phase_index
        self.question_index = question_index
        self.load_question()

    def set_current_phase_by_id(self, phase_id: str):
        """
        Définit la phase actuelle du wizard en fonction de son ID.
        """
        try:
            target_phase_index = next(
                i for i, p in enumerate(self.project.phases) if p.id == phase_id
            )
            if target_phase_index is not None:
                # Sauvegarder la réponse actuelle avant de changer de phase/question
                if self.project.phases and self.current_phase().questions:
                    self.save_response()
                
                self.phase_index = target_phase_index
                self.question_index = 0  # Commence à la première question de la nouvelle phase
                
                # S'assurer que la step_bar est mise à jour pour la nouvelle phase
                if self.step_bar:
                    self.step_bar.set_phase_title(self.current_phase().title)
                    self.step_bar.set_total_steps(len(self.current_phase().questions))
                    # La méthode load_question s'occupera de mettre à jour l'étape active et les réponses
                
                self.load_question()
                print(f"PhaseWizardWidget: Changement vers la phase '{phase_id}' (index {self.phase_index}), question 0.")
            else:
                print(f"PhaseWizardWidget: Impossible de trouver la phase avec l'ID '{phase_id}'.")
        except StopIteration:
            print(f"PhaseWizardWidget: Phase avec l'ID '{phase_id}' non trouvée dans le projet.")
        except Exception as e:
            print(f"PhaseWizardWidget: Erreur lors du changement de phase vers '{phase_id}': {e}")

    def finish(self):
        print(
            f"finish: phase_index={self.phase_index}, question_index={self.question_index}"
        )
        self.save_response()
        # self.export_to_json()
        
        markdown_str_content = self.generate_context_markdown()  # Récupérer le contenu markdown

        if markdown_str_content: # Si le contenu a bien été généré
            analyse_dlg = AnalyseProjectDlg(markdown_str_content, self)
            # analyse_dlg.analysis_complete.connect(self.handle_analysis_complete) # Optionnel: si on veut faire qqch avec le rapport
            analyse_dlg.exec() # Exécute la dialogue de manière modale

        self.completed.emit(self.project) # Émettre le signal après la dialogue

    # def handle_analysis_complete(self, report: str):
    #     print("Rapport d'analyse reçu par PhaseWizardWidget:")
    #     print(report)
    #     # Faire quelque chose avec le rapport si nécessaire

    def generate_context_markdown(self) -> str | None: # Modifier pour retourner le contenu
        context_dir = "context"
        if not os.path.exists(context_dir):
            os.makedirs(context_dir)

        markdown_file_path = os.path.join(context_dir, "context.md")

        markdown_content = []
        markdown_content.append(f"# Projet : {self.project.name}\n")

        for phase in self.project.phases:
            markdown_content.append(f"## Phase : {phase.title}\n")
            for question in phase.questions:
                markdown_content.append(f"### {question.text}\n")
                response = (
                    question.response
                    if question.response
                    else "Aucune réponse fournie."
                )
                markdown_content.append(f"{response}\n")
            markdown_content.append("\n")  # Espace entre les phases

        try:
            with open(markdown_file_path, "w", encoding="utf-8") as f:
                f.write("".join(markdown_content))
            print(f"Fichier Markdown généré : {markdown_file_path}")
            
            return "".join(markdown_content) # Retourner le contenu après écriture réussie
            
        except Exception as e:
            print(f"Erreur lors de la génération du fichier Markdown : {e}")
            # On pourrait quand même retourner le contenu si l'écriture échoue mais que la génération en mémoire a réussi
            # Pour l'instant, si l'écriture échoue, on considère que la génération a échoué pour la dialogue.
            return None

    def reset_answers(self):
        for phase in self.project.phases:
            for question in phase.questions:
                key = f"{self.project.name}/{phase.id}/{question.id}"
                self.settings.remove(key)
                question.response = ""
        self.phase_index = 0
        self.question_index = 0
        self.load_question()

   
        import json
        from PySide6.QtWidgets import QFileDialog

        export_data = {"project": self.project.name, "phases": []}
        for phase in self.project.phases:
            phase_data = {"id": phase.id, "title": phase.title, "questions": []}
            for q in phase.questions:
                phase_data["questions"].append(
                    {"id": q.id, "question": q.text, "response": q.response or ""}
                )
            export_data["phases"].append(phase_data)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en JSON",
            f"{self.project.name}.json",
            "Fichiers JSON (*.json)",
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

    def jump_to_question(self, question_index):
        self.save_response()
        self.question_index = question_index
        self.load_question()
