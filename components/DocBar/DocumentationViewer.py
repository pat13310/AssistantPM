from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QUrl
from components.DocBar.HorizontalDocBar import HorizontalDocBar  # ta version personnalisée
from components.dialogues.DocGenerationDlg import DocGenerationDlg


class DocumentationViewer(QWidget):
    def __init__(self, doc_definitions: list[dict], html_lookup: dict[str, str], parent=None):
        super().__init__(parent)
        self.html_lookup = html_lookup
        self.setStyleSheet("background-color: #FCFCFC;")  # Couleur de fond gris clair

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        # === En-tête avec icône + titre ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        icon = QLabel()
        icon.setPixmap(QPixmap("assets/icons/book-open.svg"))  # adapte le chemin si besoin
        #icon.setFixedSize(24, 24)

        title = QLabel("Documentation")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #1F2937;")

        header_layout.addWidget(icon)
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Barre de bulles (HorizontalDocBar)
        self.bar = HorizontalDocBar(doc_definitions)
        self.bar.bubbleClicked.connect(lambda doc_key: self.on_bubble_clicked(doc_key, doc_definitions))
        layout.addWidget(self.bar)

        # Composant HTML WebView
        self.viewer = QWebEngineView()
        self.viewer.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.viewer.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.viewer.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.viewer.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        layout.addWidget(self.viewer, stretch=1)

    def on_bubble_clicked(self, doc_key: str, doc_definitions):
        html = self.html_lookup.get(doc_key, f"<h2>{doc_key}</h2><p>Documentation indisponible</p>")
        self.viewer.setHtml(html, baseUrl=QUrl("http://localhost/"))

        # Trouver le doc correspondant
        doc = next((d for d in doc_definitions if d["title"] == doc_key), None)
        if doc:
            is_ready = doc["ready"]
        else:
            is_ready = False

        print(f"📘 Doc sélectionnée : {doc_key} | Générée : {'✅' if is_ready else '⏳'}")

        if not is_ready:
            dlg = DocGenerationDlg(doc_key, self)
            dlg.exec()
