from pathlib import Path
import datetime
import json

class DocumentEditor:
    def __init__(self, doc_type, save_dir):
        self.doc_type = doc_type
        self.save_dir = Path(save_dir)
        self.generated_content = {}
        self.versions = {}
        self.favorites = []
        self.history = []
        self.custom_prompts = {}
        self.current_item_path = None
        self.current_version = 0
        self._source_view_active = False

    def load_json_file(self, filename, default):
        try:
            file_path = self.save_dir / filename
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de {filename} : {e}")
        return default

    def save_json_file(self, filename, data):
        try:
            file_path = self.save_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de {filename} : {e}")

    def apply_content_edits(self, html):
        if not self.current_item_path:
            return

        current_path = self.current_item_path
        previous_html = self.generated_content.get(current_path)

        if previous_html:
            self.versions.setdefault(current_path, {})[self.current_version] = previous_html
            self.current_version += 1

        self.generated_content[current_path] = html

    def toggle_html_source(self, html_view, show_source_button, render_html):
        if not self.current_item_path:
            return

        html = self.generated_content.get(self.current_item_path)
        if not html:
            return

        if self._source_view_active:
            html_view.setHtml(render_html(html))
            show_source_button.setText("Afficher le source")
        else:
            self.show_html_source(html_view, html)
            show_source_button.setText("Masquer le source")

        self._source_view_active = not self._source_view_active

    def show_html_source(self, html_view, html):
        # Extraire le dernier élément du chemin en tenant compte de l'icône
        if "<i class='nav-icon'></i>" in self.current_item_path:
            title = self.current_item_path.split("<i class='nav-icon'></i>")[-1].strip()
        else:
            title = self.current_item_path
        escaped_html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        source_view = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Code source</title></head>
        <body>
            <h2>Code source : {title}</h2>
            <pre>{escaped_html}</pre>
        </body>
        </html>
        """
        html_view.setHtml(source_view)

    def get_export_filename(self, extension):
        # Extraire le dernier élément du chemin en tenant compte de l'icône
        if "<i class='nav-icon'></i>" in self.current_item_path:
            base = self.current_item_path.split("<i class='nav-icon'></i>")[-1].strip()
        else:
            base = self.current_item_path.strip()
        return base.replace(" ", "") + f".{extension}"

    def save_document(self, file_path):
        data = {
            "doc_type": self.doc_type.name,
            "content": self.generated_content,
            "versions": self.versions,
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.save_json_file(file_path, data)

    def load_document(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if data.get("doc_type") != self.doc_type.name:
                print(f"Type de document incorrect : {data.get('doc_type')} au lieu de {self.doc_type.name}")
                return

            self.generated_content = data.get("content", {})
            self.versions = data.get("versions", {})
            return data.get("timestamp", "Inconnu")
        except Exception as e:
            print(f"Erreur lors du chargement du document : {e}")
            return None
