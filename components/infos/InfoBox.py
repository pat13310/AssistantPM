from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtCore import Qt, Signal, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QMouseEvent


class InfoBox(QWidget):
    suggestionClicked = Signal(str)

    def __init__(self, suggestions: list[str], practice: str, sous_suggestions: dict[str, list[str]] = None, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setMouseTracking(True)
        self.setMinimumHeight(200)

        self.suggestions = suggestions
        self.sous_suggestions = sous_suggestions or {}
        self.practice = practice

        self.bg_color = QColor("#eef4ff")
        self.border_color = QColor("#3b82f6")
        self.hover_border_color = QColor("#3b82f6")
        self.title_color = QColor("#1d4ed8")
        self.subtitle_color = QColor("#007bff")
        self.text_color = QColor("#374151")
        self.practice_bg = QColor("#f0f9ff")
        self.sub_text_color = QColor("#1e3a8a")

        self.title_font = QFont("Segoe UI", 10, QFont.Bold)
        self.text_font = QFont("Segoe UI", 9)
        self.sub_text_font = QFont("Segoe UI", 8)

        self.suggestion_rects = []
        self.sub_suggestion_rects = []
        self.hovered_index = -1 # Index de la suggestion principale survolée
        self.hovered_sub_index = -1 # Index global de la sous-suggestion survolée

    def update_content(self, suggestions: list[str], practice: str, sous_suggestions: dict[str, list[str]] = None):
        self.suggestions = suggestions
        self.practice = practice
        self.sous_suggestions = sous_suggestions or {}
        self.hovered_index = -1
        self.hovered_sub_index = -1
        # Il est important de vider les listes de rectangles ici aussi,
        # car leur contenu dépend des suggestions.
        self.suggestion_rects.clear()
        self.sub_suggestion_rects.clear()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(1, 1, -1, -1)

        painter.setBrush(self.bg_color)
        painter.setPen(QPen(self.border_color, 1))
        painter.drawRoundedRect(rect, 12, 12)

        x, y = 20, 20
        # Ces listes sont remplies pendant le paintEvent.
        # Il est crucial de les vider ici pour s'assurer qu'elles ne contiennent que les rectangles de la passe de dessin actuelle.
        self.suggestion_rects.clear()
        self.sub_suggestion_rects.clear()
        
        current_global_sub_index = 0 # Index global pour les sous-suggestions

        painter.setFont(self.title_font)
        painter.setPen(self.title_color)
        painter.drawText(x, y, "Suggestions :")
        y += 30

        font_metrics = QFontMetrics(self.text_font)
        sub_font_metrics = QFontMetrics(self.sub_text_font)
        max_width = self.width() - 2 * x
        max_btn_width = 220
        padding_x = 12
        padding_y = 8

        for i, suggestion in enumerate(self.suggestions):
            bounding = font_metrics.boundingRect(0, 0, max_btn_width - 2 * padding_x, 1000, Qt.TextWordWrap, suggestion)
            btn_width = min(max_btn_width, bounding.width() + 2 * padding_x)
            btn_height = bounding.height() + 2 * padding_y
            btn_rect = QRect(x, y, btn_width, btn_height)
            self.suggestion_rects.append((btn_rect, suggestion)) # Garder pour la détection de survol/clic

            is_category_title = suggestion in self.sous_suggestions and self.sous_suggestions[suggestion]

            if is_category_title:
                # Style pour les titres de catégorie (ex: "Objectifs métier")
                painter.setFont(self.title_font)
                painter.setPen(self.subtitle_color)
                # Dessiner le texte directement, aligné verticalement dans l'espace du "bouton"
                painter.drawText(btn_rect.adjusted(0, 0, 0, 0), # Utiliser btn_rect pour la zone de texte
                                 Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignVCenter, suggestion)
            else:
                # Style pour les suggestions "feuilles" (comme avant)
                painter.setBrush(QColor("#dbeafe"))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(btn_rect, 8, 8)

                if i == self.hovered_index: # self.hovered_index est basé sur l'itération sur self.suggestions
                    painter.setPen(QPen(self.hover_border_color, 2))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRoundedRect(btn_rect.adjusted(1, 1, -1, -1), 8, 8)

                painter.setFont(self.text_font)
                painter.setPen(self.text_color)
                text_rect = btn_rect.adjusted(padding_x, padding_y, -padding_x, -padding_y)
                painter.drawText(text_rect, Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, suggestion)

            y += btn_height + 6

            # Sous-suggestions
            if is_category_title: # Utiliser la variable déjà définie
                for j, sub in enumerate(self.sous_suggestions[suggestion]):
                    sub_bounding = sub_font_metrics.boundingRect(0, 0, max_btn_width - 2 * padding_x, 1000, Qt.TextWordWrap, sub)
                    sub_width = min(max_btn_width, sub_bounding.width() + 2 * padding_x)
                    sub_height = sub_bounding.height() + 2 * padding_y

                    sub_rect = QRect(x + 20, y, sub_width, sub_height) # Augmentation de l'indentation
                    # Ajouter à la liste des rectangles de sous-suggestions pour la détection de survol/clic
                    # Cet ajout se fait ici, donc l'ordre dans self.sub_suggestion_rects correspondra
                    # à l'itération et donc à current_global_sub_index.
                    self.sub_suggestion_rects.append((sub_rect, sub))

                    painter.setFont(self.sub_text_font)
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor("#e0f2fe"))
                    painter.drawRoundedRect(sub_rect, 6, 6)

                    # Utiliser l'index global pour vérifier le survol
                    if current_global_sub_index == self.hovered_sub_index:
                        painter.setPen(QPen(self.hover_border_color, 1))
                        painter.setBrush(Qt.NoBrush)
                        painter.drawRoundedRect(sub_rect.adjusted(1, 1, -1, -1), 6, 6)
                    
                    current_global_sub_index += 1 # Incrémenter l'index global

                    painter.setPen(self.sub_text_color)
                    painter.drawText(sub_rect.adjusted(padding_x, padding_y, -padding_x, -padding_y),
                                    Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, sub)
                    y += sub_height + 4

                y = 50
                x += 250 # Passer à la colonne suivante

        # Bonnes pratiques
        if self.practice:
            x= 20
            y= 280
            painter.setFont(self.title_font)
            painter.setPen(self.title_color)
            painter.drawText(x, y, "Bonnes pratiques :")
            y += 30

            painter.setFont(self.text_font)
            content_width = self.width() - 2 * x
            bounding = font_metrics.boundingRect(QRect(0, 0, content_width - 20, 1000), Qt.TextWordWrap, self.practice)
            text_height = bounding.height()
            box_height = text_height + 16
            box_rect = QRect(x, y, content_width, box_height)

            painter.setPen(Qt.NoPen)
            painter.setBrush(self.practice_bg)
            painter.drawRoundedRect(box_rect, 8, 8)

            painter.setPen(self.text_color)
            painter.drawText(box_rect.adjusted(10, 8, -10, -8), Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, self.practice)

            y += box_height + 20

        self.setMinimumHeight(y)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        
        old_hovered_index = self.hovered_index
        old_hovered_sub_index = self.hovered_sub_index
        
        current_hovered_index = -1
        current_hovered_sub_index = -1
        
        # Priorité aux sous-suggestions car elles peuvent être superposées
        # self.sub_suggestion_rects contient les rectangles dans leur ordre de dessin global
        for i, (rect, _) in enumerate(self.sub_suggestion_rects):
            if rect.contains(pos):
                current_hovered_sub_index = i # i est l'index global
                break # Une seule sous-suggestion peut être survolée à la fois
        
        if current_hovered_sub_index == -1: # Si aucune sous-suggestion n'est survolée
            # Vérifier les suggestions principales
            for i, (rect, suggestion_text) in enumerate(self.suggestion_rects):
                # On ne met en surbrillance que les suggestions "feuilles", pas les titres de catégorie
                is_category_title = suggestion_text in self.sous_suggestions and self.sous_suggestions[suggestion_text]
                if not is_category_title and rect.contains(pos):
                    current_hovered_index = i
                    break # Une seule suggestion principale peut être survolée

        # Mettre à jour l'état et redessiner seulement si l'élément survolé a changé
        if old_hovered_index != current_hovered_index or old_hovered_sub_index != current_hovered_sub_index:
            self.hovered_index = current_hovered_index
            self.hovered_sub_index = current_hovered_sub_index
            self.update() # Demander un redessin

        # Mettre à jour le curseur
        if self.hovered_index != -1 or self.hovered_sub_index != -1:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        for rect, suggestion in self.suggestion_rects:
            if rect.contains(pos):
                self.suggestionClicked.emit(suggestion)
                return

        for rect, sub in self.sub_suggestion_rects:
            if rect.contains(pos):
                self.suggestionClicked.emit(sub)
                return
