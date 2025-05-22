import sys
import os
import ast
import tokenize
import io
import keyword
import mypy.api
import requests
import autopep8
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QHBoxLayout,
    QCompleter,
    QInputDialog,
    QLineEdit,
    QToolBar,
)
from PySide6.QtGui import (
    QTextCharFormat,
    QFont,
    QColor,
    QTextCursor,
    QPainter,
    QTextOption,
    QKeySequence,
    QMouseEvent,
    QTextDocument,
    QSyntaxHighlighter,
    QResizeEvent, # Ajout pour le type hint de resizeEvent
)
from PySide6.QtCore import (
    Qt,
    QRect,
    QStringListModel,
    QPoint,
    QSize,
)
import subprocess


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent_document):
        super().__init__(parent_document)
        # print("[Highlighter] __init__")

        self.formats = {
            "keyword": QTextCharFormat(),
            "string": QTextCharFormat(),
            "comment": QTextCharFormat(),
            "number": QTextCharFormat(),
            "decorator": QTextCharFormat(),
            "identifier": QTextCharFormat(),
            "operator": QTextCharFormat(),
            "builtin": QTextCharFormat(),
            "function_name": QTextCharFormat(),
            "class_name": QTextCharFormat(),
        }

        self.formats["keyword"].setForeground(QColor("#FF79C6"))
        self.formats["keyword"].setFontWeight(QFont.Bold)
        self.formats["string"].setForeground(QColor("#F1FA8C"))
        self.formats["comment"].setForeground(QColor("#6272A4"))
        self.formats["comment"].setFontItalic(True)
        self.formats["number"].setForeground(QColor("#BD93F9"))
        self.formats["decorator"].setForeground(QColor("#50FA7B"))
        self.formats["decorator"].setFontWeight(QFont.Bold)
        self.formats["operator"].setForeground(QColor("#FF79C6"))
        self.formats["identifier"].setForeground(QColor("#F8F8F2"))
        self.formats["builtin"].setForeground(QColor("#8BE9FD"))
        self.formats["builtin"].setFontItalic(True)
        self.formats["function_name"].setForeground(QColor("#50FA7B"))
        self.formats["function_name"].setFontWeight(QFont.Bold)
        self.formats["class_name"].setForeground(QColor("#8BE9FD"))
        self.formats["class_name"].setFontWeight(QFont.Bold)

        self.STATE_NORMAL = 0 
        self.STATE_EXPECT_FUNC_NAME = 1
        self.STATE_EXPECT_CLASS_NAME = 2
        
        self.MULTILINE_STATE_NONE = 0
        self.MULTILINE_STATE_TRIPLE_DOUBLE = 3
        self.MULTILINE_STATE_TRIPLE_SINGLE = 4

    def highlightBlock(self, text_of_block):
        # print(f"[Highlighter] highlightBlock: '{text_of_block[:30]}...'")
        current_block_final_multiline_state = self.MULTILINE_STATE_NONE
        start_offset_for_tokenization = 0
        
        previous_block_multiline_state = self.previousBlockState()
        if previous_block_multiline_state == -1:
            previous_block_multiline_state = self.MULTILINE_STATE_NONE
        
        # print(f"  Prev state: {previous_block_multiline_state}, Text: '{text_of_block}'")

        if previous_block_multiline_state == self.MULTILINE_STATE_TRIPLE_DOUBLE:
            end_index = text_of_block.find('"""')
            if end_index != -1:
                length = end_index + 3
                self.setFormat(0, length, self.formats["string"])
                start_offset_for_tokenization = length
            else:
                self.setFormat(0, len(text_of_block), self.formats["string"])
                self.setCurrentBlockState(self.MULTILINE_STATE_TRIPLE_DOUBLE)
                return
        elif previous_block_multiline_state == self.MULTILINE_STATE_TRIPLE_SINGLE:
            end_index = text_of_block.find("'''")
            if end_index != -1:
                length = end_index + 3
                self.setFormat(0, length, self.formats["string"])
                start_offset_for_tokenization = length
            else:
                self.setFormat(0, len(text_of_block), self.formats["string"])
                self.setCurrentBlockState(self.MULTILINE_STATE_TRIPLE_SINGLE)
                return
        
        text_to_tokenize = text_of_block[start_offset_for_tokenization:]

        if not text_to_tokenize.strip() and start_offset_for_tokenization > 0:
             self.setCurrentBlockState(current_block_final_multiline_state) 
             return
        if not text_to_tokenize: 
            self.setCurrentBlockState(current_block_final_multiline_state)
            return

        try:
            block_reader = io.StringIO(text_to_tokenize).readline
            current_intra_block_parsing_state = self.STATE_NORMAL
            
            tokens_for_block = []
            try:
                for tok_info in tokenize.generate_tokens(block_reader):
                    tokens_for_block.append(tok_info)
            except tokenize.TokenError:
                pass 
            except Exception as e_tok:
                # print(f"Tokenization error in highlightBlock: {e_tok} on text: '{text_to_tokenize}'")
                self.setCurrentBlockState(current_block_final_multiline_state)
                return

            for i, tok_info in enumerate(tokens_for_block):
                token_type_name = tokenize.tok_name[tok_info.type].lower()
                start_col_in_tokenized_text = tok_info.start[1]
                end_col_in_tokenized_text = tok_info.end[1]
                length = end_col_in_tokenized_text - start_col_in_tokenized_text
                token_text = tok_info.string

                actual_start_col_in_block = start_col_in_tokenized_text + start_offset_for_tokenization
                
                target_format_key = None

                if current_intra_block_parsing_state == self.STATE_EXPECT_FUNC_NAME and token_type_name == "name":
                    target_format_key = "function_name"
                    current_intra_block_parsing_state = self.STATE_NORMAL
                elif current_intra_block_parsing_state == self.STATE_EXPECT_CLASS_NAME and token_type_name == "name":
                    target_format_key = "class_name"
                    current_intra_block_parsing_state = self.STATE_NORMAL
                elif token_type_name == "name":
                    if token_text == "def" and (i + 1 < len(tokens_for_block)):
                        target_format_key = "keyword"
                        current_intra_block_parsing_state = self.STATE_EXPECT_FUNC_NAME
                    elif token_text == "class" and (i + 1 < len(tokens_for_block)):
                        target_format_key = "keyword"
                        current_intra_block_parsing_state = self.STATE_EXPECT_CLASS_NAME
                    elif token_text in keyword.kwlist:
                        target_format_key = "keyword"
                    elif token_text.startswith("@"):
                        target_format_key = "decorator"
                    elif token_text in ['str', 'int', 'list', 'dict', 'tuple', 'set', 'self', 'cls']:
                        target_format_key = "builtin"
                    elif len(token_text) > 0 and token_text[0].isupper() and not token_text.isupper():
                        is_likely_class_name = True
                        if len(token_text) > 1:
                            has_lower = any(c.islower() for c in token_text[1:])
                            if not has_lower and token_text[1:].isupper():
                                is_likely_class_name = False
                        if is_likely_class_name:
                            target_format_key = "class_name"
                        else:
                            target_format_key = "identifier"
                    else:
                        target_format_key = "identifier"
                elif token_type_name == "string":
                    target_format_key = "string"
                    if start_offset_for_tokenization == 0 and previous_block_multiline_state == self.MULTILINE_STATE_NONE:
                        if token_text.startswith('"""') and not (token_text.endswith('"""') and len(token_text) >= 6):
                            current_block_final_multiline_state = self.MULTILINE_STATE_TRIPLE_DOUBLE
                        elif token_text.startswith("'''") and not (token_text.endswith("'''") and len(token_text) >= 6):
                            current_block_final_multiline_state = self.MULTILINE_STATE_TRIPLE_SINGLE
                elif token_type_name == "comment":
                    target_format_key = "comment"
                elif token_type_name == "number":
                    target_format_key = "number"
                elif token_type_name == "op":
                    target_format_key = "operator"

                if target_format_key and length > 0:
                    format_to_apply = self.formats.get(target_format_key, self.formats["identifier"])
                    self.setFormat(actual_start_col_in_block, length, format_to_apply)
        
        except Exception as e:
            print(f"Unexpected error in highlightBlock (main try): {type(e).__name__}: {e} on text '{text_of_block}'")
            import traceback
            traceback.print_exc()
        
        self.setCurrentBlockState(current_block_final_multiline_state)


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.bookmarks = set()
        self.setFont(self.editor.font())
        # Important: Set a background to make sure the widget is visible
        self.setStyleSheet("background-color: #333333;")

    def sizeHint(self):
        return QSize(self.width(), 10000)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Fill background with a distinct color
        painter.fillRect(event.rect(), QColor("#333333"))
        
        # Get the first visible block
        block = self.editor.firstVisibleBlock()
        if not block.isValid():
            return

        # Initialize variables
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(
            self.editor.contentOffset()
        ).top()
        bottom = top + self.editor.blockBoundingRect(block).height()
        font_height = self.editor.fontMetrics().height()
        
        # Loop through all visible blocks
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                # Draw the line number
                number = block_number + 1
                painter.setPen(QColor("#AAAAAA"))  # Light gray text
                painter.drawText(
                    0, 
                    int(top), 
                    self.width() - 10, 
                    font_height, 
                    Qt.AlignRight,
                    str(number)
                )
                
                # Draw bookmark indicator if this line is bookmarked
                if number in self.bookmarks:
                    painter.setBrush(QColor("red"))
                    painter.setPen(Qt.NoPen)
                    painter.drawEllipse(2, int(top) + (font_height - 8) // 2, 8, 8)
            
            # Move to next block
            block = block.next()
            if not block.isValid():
                break
                
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # Find which block was clicked
            block = self.editor.firstVisibleBlock()
            top = self.editor.blockBoundingGeometry(block).translated(
                self.editor.contentOffset()
            ).top()
            
            # Loop through blocks to find which one was clicked
            while block.isValid() and top <= event.y():
                height = self.editor.blockBoundingRect(block).height()
                bottom = top + height
                
                if top <= event.y() <= bottom:
                    # Toggle bookmark for this line
                    block_number = block.blockNumber() + 1
                    self.editor.toggle_bookmark(block_number)
                    self.update()
                    break
                    
                block = block.next()
                top = bottom

class DeepSeekAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"

    def generate_text(self, prompt, model="deepseek", max_tokens=500):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }
        try:
            response = requests.post(
                f"{self.base_url}/completions", json=payload, headers=headers
            )
            response.raise_for_status()
            return (
                response.json()
                .get("choices", [{}])[0]
                .get("text", "Erreur : aucune réponse")
            )
        except requests.RequestException as e:
            return f"Erreur API : {str(e)}"


class CodeEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Éditeur de Code Avancé avec Indentation Automatique")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet(
            "background-color: black; color: #F2F2F2; font-family: 'Courier New'; font-size: 11px;"
        )

        self.deepseek = DeepSeekAPI(api_key="YOUR_DEEPSEEK_API_KEY")
        self.bookmarks = set()
        self.search_cursor = None
        self.search_text = ""

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.search_bar = QToolBar()
        self.search_bar.setVisible(False)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.returnPressed.connect(self.find_next)
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Remplacer par...")
        self.find_next_button = QPushButton("Suivant")
        self.find_next_button.clicked.connect(self.find_next)
        self.find_prev_button = QPushButton("Précédent")
        self.find_prev_button.clicked.connect(self.find_prev)
        self.replace_button = QPushButton("Remplacer")
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button = QPushButton("Tout remplacer")
        self.replace_all_button.clicked.connect(self.replace_all)
        self.search_bar.addWidget(QLabel("Rechercher : "))
        self.search_bar.addWidget(self.search_input)
        self.search_bar.addWidget(QLabel(" Remplacer : "))
        self.search_bar.addWidget(self.replace_input)
        self.search_bar.addWidget(self.find_next_button)
        self.search_bar.addWidget(self.find_prev_button)
        self.search_bar.addWidget(self.replace_button)
        self.search_bar.addWidget(self.replace_all_button)
        self.addToolBar(self.search_bar)

        self.code_label = QLabel("Éditeur de code Python :")
        self.layout.addWidget(self.code_label)

        self.code_input = QPlainTextEdit()
        self.code_input.setFont(QFont("Courier New", 12))
        self.code_input.setPlaceholderText(
            "# Écrivez votre code Python ici...\n# Ctrl+B pour bookmark, Ctrl+F pour rechercher, Ctrl+R pour remplacer, F1 pour indenter"
        )
        self.highlighter = PythonHighlighter(
            self.code_input.document()
        ) 
        self.line_number_area = LineNumberArea(self.code_input)
        self.line_number_area.bookmarks = self.bookmarks 
        self.code_input.blockCountChanged.connect(self.update_line_number_area_width)
        self.code_input.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width() 

        self.completer = QCompleter(self)
        self.completer.setWidget(self.code_input)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)
        self.code_input.keyPressEvent = self.keyPressEvent
        self.update_completions()

        self.layout.addWidget(self.code_input)

        self.button_layout = QHBoxLayout()

        self.run_button = QPushButton("Exécuter le code")
        self.run_button.clicked.connect(self.run_code)
        self.button_layout.addWidget(self.run_button)

        self.check_types_button = QPushButton("Vérifier les types (mypy)")
        self.check_types_button.clicked.connect(self.check_types)
        self.button_layout.addWidget(self.check_types_button)

        self.deepseek_button = QPushButton("Envoyer à DeepSeek")
        self.deepseek_button.clicked.connect(self.send_to_deepseek)
        self.button_layout.addWidget(self.deepseek_button)

        self.bookmark_next_button = QPushButton("Bookmark suivant")
        self.bookmark_next_button.clicked.connect(self.goto_next_bookmark)
        self.button_layout.addWidget(self.bookmark_next_button)

        self.bookmark_prev_button = QPushButton("Bookmark précédent")
        self.bookmark_prev_button.clicked.connect(self.goto_prev_bookmark)
        self.button_layout.addWidget(self.bookmark_prev_button)

        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_file)
        self.button_layout.addWidget(self.save_button)

        self.load_button = QPushButton("Charger")
        self.load_button.clicked.connect(self.load_file)
        self.button_layout.addWidget(self.load_button)

        self.layout.addLayout(self.button_layout)

        self.output_label = QLabel("Sortie :")
        self.layout.addWidget(self.output_label)

        self.output_display = QPlainTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setFont(QFont("Courier New", 12))
        self.layout.addWidget(self.output_display)

    def resizeEvent(self, event: QResizeEvent): # Type hint corrigé
        # print("[CodeEditor] resizeEvent called") 
        super().resizeEvent(event) 
        self.update_line_number_area_width() 
        self.line_number_area.update()       

    def keyPressEvent(self, event):
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab):
                event.ignore()
                return
        if event.key() == Qt.Key_F1:
            self.auto_indent()
            return
        if event.key() == Qt.Key_F and event.modifiers() & Qt.ControlModifier:
            self.search_bar.setVisible(True)
            self.search_input.setFocus()
            return
        if event.key() == Qt.Key_R and event.modifiers() & Qt.ControlModifier:
            self.search_bar.setVisible(True)
            self.replace_input.setFocus()
            return
        if event.key() == Qt.Key_Space and event.modifiers() & Qt.ControlModifier:
            self.show_completions()
            return
        if event.key() == Qt.Key_B and event.modifiers() & Qt.ControlModifier:
            cursor = self.code_input.textCursor()
            block_number = cursor.blockNumber() + 1
            self.toggle_bookmark(block_number) 
            return
        QPlainTextEdit.keyPressEvent(self.code_input, event)
        self.update_completions()

    def auto_indent(self):
        code = self.code_input.toPlainText()
        if not code.strip():
            self.output_display.setPlainText("Aucun code à indenter.")
            return
        try:
            formatted_code = autopep8.fix_code(code, options={"max_line_length": 88})
            self.code_input.setPlainText(formatted_code)
            self.output_display.setPlainText("Code indenté selon PEP 8.")
        except Exception as e:
            self.output_display.setPlainText(f"Erreur lors de l'indentation : {str(e)}")

    def show_completions(self):
        cursor = self.code_input.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        prefix = cursor.selectedText()
        self.completer.setCompletionPrefix(prefix)
        cr = self.code_input.cursorRect()
        cr.setWidth(
            self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width()
        )
        self.completer.complete(cr)

    def insert_completion(self, completion):
        cursor = self.code_input.textCursor()
        cursor.select(QTextCursor.WordUnderCursor)
        cursor.insertText(completion)
        self.code_input.setTextCursor(cursor)

    def update_completions(self):
        code = self.code_input.toPlainText()
        completions = set(keyword.kwlist)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Name)):
                    name = getattr(node, "name", getattr(node, "id", None))
                    if name:
                        completions.add(name)
        except SyntaxError:
            pass
        model = QStringListModel(list(completions), self.completer)
        self.completer.setModel(model)

    def toggle_bookmark(self, line_number): 
        if line_number in self.bookmarks:
            self.bookmarks.remove(line_number)
            self.output_display.setPlainText(
                f"Bookmark supprimé à la ligne {line_number}"
            )
        else:
            self.bookmarks.add(line_number)
            self.output_display.setPlainText(
                f"Bookmark ajouté à la ligne {line_number}"
            )
        self.line_number_area.update() 

    def goto_next_bookmark(self):
        if not self.bookmarks:
            self.output_display.setPlainText("Aucun bookmark défini.")
            return
        cursor = self.code_input.textCursor()
        current_line = cursor.blockNumber() + 1
        next_line = min(
            [line for line in self.bookmarks if line > current_line],
            default=min(self.bookmarks) if self.bookmarks else 0 
        )
        if next_line > 0 : self.goto_line(next_line)


    def goto_prev_bookmark(self):
        if not self.bookmarks:
            self.output_display.setPlainText("Aucun bookmark défini.")
            return
        cursor = self.code_input.textCursor()
        current_line = cursor.blockNumber() + 1
        prev_line = max(
            [line for line in self.bookmarks if line < current_line],
            default=max(self.bookmarks) if self.bookmarks else 0 
        )
        if prev_line > 0 : self.goto_line(prev_line)


    def goto_line(self, line_number):
        cursor = self.code_input.textCursor()
        cursor.movePosition(QTextCursor.Start)
        for _ in range(line_number - 1):
            cursor.movePosition(QTextCursor.Down)
        self.code_input.setTextCursor(cursor)
        self.code_input.ensureCursorVisible()
        self.output_display.setPlainText(f"Aller au bookmark à la ligne {line_number}")

    def find_next(self):
        search_text = self.search_input.text()
        if not search_text:
            self.output_display.setPlainText("Entrez un texte à rechercher.")
            return
        self.search_text = search_text
        cursor = self.code_input.textCursor()
        if self.search_cursor:
            cursor.setPosition(self.search_cursor.position())
        doc = self.code_input.document()
        self.search_cursor = doc.find(
            search_text, cursor, QTextDocument.FindCaseSensitively
        )
        if not self.search_cursor.isNull():
            self.code_input.setTextCursor(self.search_cursor)
            extra_selection = QPlainTextEdit.ExtraSelection()
            extra_selection.format.setBackground(QColor("yellow"))
            extra_selection.cursor = self.search_cursor
            self.code_input.setExtraSelections([extra_selection])
        else:
            self.output_display.setPlainText("Aucune correspondance trouvée.")
            self.search_cursor = None

    def find_prev(self):
        search_text = self.search_input.text()
        if not search_text:
            self.output_display.setPlainText("Entrez un texte à rechercher.")
            return
        self.search_text = search_text
        cursor = self.code_input.textCursor()
        if self.search_cursor:
            cursor.setPosition(self.search_cursor.position())
        doc = self.code_input.document()
        self.search_cursor = doc.find(
            search_text,
            cursor,
            QTextDocument.FindCaseSensitively | QTextDocument.FindBackward,
        )
        if not self.search_cursor.isNull():
            self.code_input.setTextCursor(self.search_cursor)
            extra_selection = QPlainTextEdit.ExtraSelection()
            extra_selection.format.setBackground(QColor("yellow"))
            extra_selection.cursor = self.search_cursor
            self.code_input.setExtraSelections([extra_selection])
        else:
            self.output_display.setPlainText("Aucune correspondance trouvée.")
            self.search_cursor = None

    def replace(self):
        if not self.search_cursor or self.search_cursor.isNull():
            self.output_display.setPlainText("Aucune correspondance sélectionnée.")
            return
        replace_text = self.replace_input.text()
        cursor = self.code_input.textCursor()
        cursor.setPosition(self.search_cursor.position())
        cursor.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        cursor.insertText(replace_text)
        self.code_input.setTextCursor(cursor)
        self.find_next()

    def replace_all(self):
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        if not search_text:
            self.output_display.setPlainText("Entrez un texte à rechercher.")
            return
        code = self.code_input.toPlainText()
        new_code = code.replace(search_text, replace_text)
        self.code_input.setPlainText(new_code)
        self.output_display.setPlainText(
            f"Toutes les occurrences de '{search_text}' remplacées par '{replace_text}'."
        )

    def update_line_number_area_width(self):
        # print("[CodeEditor] update_line_number_area_width called") # Décommenter pour débogage
        max_lines = max(1, self.code_input.blockCount())
        digits = 1
        temp_count = max_lines
        while temp_count >= 10:
            digits += 1
            temp_count //= 10
        
        font_metrics = self.line_number_area.fontMetrics()
        space_for_digits = font_metrics.horizontalAdvance("9" * digits)
        
        padding_left = 5
        padding_right_for_bookmark_and_margin = 15
        new_width = padding_left + space_for_digits + padding_right_for_bookmark_and_margin
        
        if self.line_number_area.width() != new_width:
            self.line_number_area.setFixedWidth(new_width)
            self.code_input.setViewportMargins(new_width, 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        # print(f"[CodeEditor] update_line_number_area: rect={rect}, dy={dy}") # Décommenter pour débogage
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

    def check_syntax(self, code):
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Erreur de syntaxe : {str(e)}"

    def check_types(self):
        code = self.code_input.toPlainText()
        if not code.strip():
            self.output_display.setPlainText("Erreur : Aucun code à analyser.")
            return

        temp_file = "temp_code.py"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            stdout, stderr, _ = mypy.api.run([temp_file])
            output = stdout + stderr
            self.output_display.setPlainText(
                output if output else "Aucune erreur de type détectée."
            )
        except Exception as e:
            self.output_display.setPlainText(f"Erreur mypy : {str(e)}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def send_to_deepseek(self):
        prompt, ok = QInputDialog.getText(
            self,
            "DeepSeek Prompt",
            "Entrez le prompt pour DeepSeek (le code actuel sera inclus) :",
        )
        if not ok:
            return
        code = self.code_input.toPlainText()
        full_prompt = f"{prompt}\n\nCode:\n{code}"
        response = self.deepseek.generate_text(full_prompt)
        self.output_display.setPlainText(response)

    def run_code(self):
        code = self.code_input.toPlainText()
        if not code.strip() or code.strip().startswith(
            "# Écrivez votre code Python ici..."
        ):
            self.output_display.setPlainText("Erreur : Aucun code à exécuter.")
            return

        is_valid, error_msg = self.check_syntax(code)
        if not is_valid:
            self.output_display.setPlainText(error_msg)
            return

        temp_file = "temp_code.py"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code)
            result = subprocess.run(
                [sys.executable, temp_file], capture_output=True, text=True, timeout=10
            )
            output = result.stdout + result.stderr
            self.output_display.setPlainText(
                output if output else "Exécution terminée sans sortie."
            )
        except subprocess.TimeoutExpired:
            self.output_display.setPlainText(
                "Erreur : Le code a pris trop de temps à s'exécuter."
            )
        except Exception as e:
            self.output_display.setPlainText(f"Erreur : {str(e)}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le fichier", "", "Python Files (*.py);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(self.code_input.toPlainText())
                self.output_display.setPlainText(f"Fichier sauvegardé : {file_name}")
            except Exception as e:
                self.output_display.setPlainText(
                    f"Erreur lors de la sauvegarde : {str(e)}"
                )

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Charger un fichier", "", "Python Files (*.py);;All Files (*)"
        )
        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f:
                    self.code_input.setPlainText(f.read())
                self.output_display.setPlainText(f"Fichier chargé : {file_name}")
            except Exception as e:
                self.output_display.setPlainText(
                    f"Erreur lors du chargement : {str(e)}"
                    
                )
                
    def resizeEvent(self, event: QResizeEvent):
        # print("[CodeEditor] resizeEvent called") # Décommenter pour débogage
        super().resizeEvent(event) 
        self.update_line_number_area_width() 
        self.line_number_area.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CodeEditor()
    window.show()
    sys.exit(app.exec())
