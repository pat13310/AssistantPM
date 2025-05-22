from PySide6.QtWebEngineWidgets import QWebEngineView

def export_pdf(view: QWebEngineView, filename: str):
    """
    Exporte le contenu actuel affiché dans QWebEngineView en PDF.
    
    :param view: Instance de QWebEngineView contenant le contenu à exporter
    :param filename: Nom du fichier PDF de sortie
    """
    if not isinstance(view, QWebEngineView):
        raise TypeError("L'objet fourni n'est pas un QWebEngineView")

    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    # Version simplifiée sans callback
    view.page().printToPdf(filename)
    print(f"Export PDF démarré vers {filename}")
