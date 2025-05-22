import os
import re

def render_html(content, skip_title=False):
    """
    Transforme le contenu HTML brut en page HTML complète.
    Ajoute le support pour les diagrammes Mermaid et autres fonctionnalités.
    
    Args:
        content (str): Le contenu HTML à transformer
        skip_title (bool): Si True, ne pas ajouter de titre h1 même si aucun n'est présent
    """
    # Nettoyer le contenu des guillemets triples et autres problèmes potentiels qui pourraient s'afficher
    content = content.replace('"""', '')
    
    # Fonction pour nettoyer les balises de code Markdown imbriquées
    def clean_code_blocks(text):
        # Nettoyer les balises de code au début
        text = re.sub(r'^\s*```+\s*html\s*', '', text)
        text = re.sub(r'^\s*``+\s*html\s*', '', text)
        
        # Nettoyer les balises de code à la fin
        text = re.sub(r'```+\s*$', '', text)
        text = re.sub(r'``+\s*$', '', text)
        
        # Nettoyer les balises de code imbriquées dans le texte
        # Rechercher des motifs comme <pre>``html ... `` et les nettoyer
        text = re.sub(r'<pre>\s*``+\s*html\s*', '<pre>', text)
        text = re.sub(r'``+\s*</pre>', '</pre>', text)
        
        # Nettoyer les balises de code imbriquées dans les balises pre et code
        text = re.sub(r'<pre>\s*<code>\s*``+\s*', '<pre><code>', text)
        text = re.sub(r'``+\s*</code>\s*</pre>', '</code></pre>', text)
        
        # Supprimer les sections de code répétées dans les balises pre
        pattern = r'(<pre>[\s\S]{50,}?</pre>)[\s\S]*?\1'
        while re.search(pattern, text):
            text = re.sub(pattern, r'\1', text)
        
        # Supprimer les sections de code HTML dupliquées
        # Rechercher des sections qui se répètent (souvent dans les exemples de code)
        def remove_duplicated_sections(content):
            # Rechercher des sections HTML de plus de 100 caractères qui se répètent
            pattern = r'(<section[\s\S]{100,}?</section>)[\s\S]*?\1'
            while re.search(pattern, content):
                content = re.sub(pattern, r'\1', content)
            return content
        
        text = remove_duplicated_sections(text)
        
        return text
    
    # Appliquer le nettoyage des blocs de code
    content = clean_code_blocks(content)
    
    # Supprimer les mentions de "html" au début du texte
    content = re.sub(r'^\s*html\s*', '', content)
    
    # Nettoyer les caractères d'échappement qui pourraient causer des problèmes
    content = content.replace('\\', '\\')
    
    # S'assurer que le contenu n'a pas de balises html ou body supplémentaires
    content = content.replace('<html>', '').replace('</html>', '')
    content = content.replace('<body>', '').replace('</body>', '')
    
    # CSS personalisé pour améliorer l'apparence
    css = """
    body, h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', 'Helvetica', sans-serif;
        line-height: 1.6;
        color: #333;
    }
    
    body {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background-color: #fafafa;
    }
    
    /* Conteneur principal avec une ombre légère */
    .content-container {
        background-color: white;
        padding: 25px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Style pour le titre de navigation */
    .page-title {
        font-family: 'Segoe UI', 'Helvetica', sans-serif;
        font-size: 1.4em;
        font-weight: 600;
        color: #444;
        margin-bottom: 1em;
        padding-bottom: 0.3em;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
    }
    
    /* Style pour le contenu de la page */
    .page-content {
        font-family: 'Segoe UI', 'Helvetica', sans-serif;
        line-height: 1.6;
        color: #333;
        margin-top: 1em;
    }
    
    /* Style pour les icônes de navigation */
    .nav-icon {
        display: inline-block;
        width: 16px;
        height:16px;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" fill="%23666" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M4.646 1.646a.5.5 0 0 1 .708 0l6 6a.5.5 0 0 1 0 .708l-6 6a.5.5 0 0 1-.708-.708L10.293 8 4.646 2.354a.5.5 0 0 1 0-.708z"/></svg>');
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        margin: 0 3px;
        vertical-align: middle;
        opacity: 0.7;
        font-weight: 600;
    }
    
    /* Style pour les sections (basé sur les h2) */
    h2 {
        margin-top: 30px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
        display: flex;
        align-items: center;
    }
    
    h2:last-of-type {
        border-bottom: none;
    }
    
    /* Ajouter un espacement entre les sections */
    h2 ~ p, h2 ~ pre, h2 ~ div {
        margin-bottom: 20px;
    }
    
    /* Styles pour les icônes SVG dans les titres */
    h1 svg, h2 svg, h3 svg, h4 svg, h5 svg, h6 svg,
    p svg, li svg, td svg, th svg {
        width: 1em;
        height: 1em;
        vertical-align: -0.125em;
        margin-right: 0.4em;
    }
    
    /* Indicateur de frappe pour le mode streaming */
    .typing-indicator {
        display: inline-block;
        position: relative;
        margin-left: 5px;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.3; }
        100% { opacity: 1; }
    }
    
    /* Style pour les titres de section */
    section h2 {
        display: flex;
        align-items: center;
        color: #333;
        font-size: 1.5em;
        margin-bottom: 15px;
    }
    
    /* Style amélioré pour les diagrammes Mermaid */
    .mermaid {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
        text-align: center;
    }
    
    /* Style amélioré pour les blocs de code */
    pre {
        background-color: #f6f8fa;
        border-radius: 5px;
        padding: 15px;
        overflow: auto;
        line-height: 1.45;
        margin: 20px 0;
        border: 1px solid #e1e4e8;
    }
    
    code {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 0.9em;
    }
    
    /* Effet au survol des icônes */
    a:hover .nav-icon {
        opacity: 1;
    }
    
    h1, h2, h3, h4, h5, h6 {
        margin-top: 1.5em;
        margin-bottom: 0.5em;
        font-weight: 600;
        color: #2c3e50;
    }
    
    h1 { font-size: 2.2em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
    h2 { font-size: 1.8em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
    h3 { font-size: 1.5em; }
    h4 { font-size: 1.3em; }
    
    p {
        margin-bottom: 1em;
    }
    
    a {
        color: #0366d6;
        text-decoration: none;
    }
    
    a:hover {
        text-decoration: underline;
    }
    
    code {
        font-family: 'Consolas', 'Monaco', monospace;
        background-color: #f6f8fa;
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-size: 0.9em;
    }
    
    pre {
        background-color: #f6f8fa;
        border-radius: 3px;
        padding: 16px;
        overflow: auto;
        line-height: 1.45;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
    }
    
    blockquote {
        border-left: 3px solid #dfe2e5;
        margin-left: 0;
        padding-left: 1em;
        color: #666;
    }
    
    table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 1em;
    }
    
    table, th, td {
        border: 1px solid #dfe2e5;
    }
    
    th, td {
        padding: 8px 16px;
        text-align: left;
    }
    
    th {
        background-color: #f6f8fa;
        font-weight: 600;
    }
    
    tr:nth-child(even) {
        background-color: #f8f8f8;
    }
    
    img {
        max-width: 100%;
        height: auto;
    }
    
    /* Styles spécifiques pour Mermaid */
    .mermaid {
        display: block;
        width: 100% !important;
        min-width: 500px;
        max-width: 100%;
        margin: 20px auto;
        font-size: 16px;
        text-align: center;
    }
    
    .mermaid svg {
        width: 100% !important;
        height: auto !important;
        min-height: 400px;
    }
    
    .mermaid .label {
        font-size: 16px !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
    
    .mermaid .node rect, 
    .mermaid .node circle, 
    .mermaid .node ellipse, 
    .mermaid .node polygon, 
    .mermaid .node path {
        stroke-width: 2px !important;
    }
    
    .mermaid .edgePath .path {
        stroke-width: 2px !important;
    }
"""

# JavaScript pour Mermaid avec support du streaming
mermaid_js = """
<script>
    function initMermaid() {
        if (typeof mermaid !== 'undefined') {
            try {
                mermaid.contentLoaded();
                setTimeout(function() {
                    var svgs = document.querySelectorAll('.mermaid svg');
                    for (var i = 0; i < svgs.length; i++) {
                        var svg = svgs[i];
                        svg.style.width = '100%';
                        svg.style.height = 'auto';
                        svg.style.minHeight = '300px';
                    }
                }, 300);
            } catch (e) {
                console.error('Erreur lors de la réinitialisation de Mermaid:', e);
                // Fallback en cas d'erreur
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose',
                    flowchart: { useMaxWidth: false, htmlLabels: true },
                    sequence: { useMaxWidth: false },
                    gantt: { useMaxWidth: false }
                });
            }
        }
    }
    
    // Charger Mermaid si nécessaire
    if (typeof mermaid === 'undefined') {
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js';
        script.onload = function() {
            mermaid.initialize({
                startOnLoad: true,
                theme: 'default',
                securityLevel: 'loose',
                flowchart: { useMaxWidth: false, htmlLabels: true },
                sequence: { useMaxWidth: false },
                gantt: { useMaxWidth: false }
            });
            initMermaid();
        };
        document.head.appendChild(script);
    } else {
        initMermaid();
    }
    
    // Observer pour détecter les changements dans le DOM (utile pour le streaming)
    document.addEventListener('DOMContentLoaded', function() {
        if (typeof MutationObserver !== 'undefined') {
            const observer = new MutationObserver(function(mutations) {
                if (typeof mermaid !== 'undefined' && document.querySelectorAll('.mermaid').length > 0) {
                    initMermaid();
                }
            });
            
            // Démarrer l'observation du contenu
            observer.observe(document.body, { childList: true, subtree: true });
        }
    });
</script>
"""

def render_html(content, css=None, skip_title=False):
    # Utiliser le CSS par défaut si aucun n'est fourni
    if css is None:
        css = """body, h1, h2, h3, h4, h5, h6 {
            font-family: 'Segoe UI', 'Helvetica', sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        body {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fafafa;
        }
        
        /* Conteneur principal avec une ombre légère */
        .content-container {
            background-color: white;
            padding: 25px;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }
        
        /* Style pour le titre de navigation */
        .page-title {
            font-family: 'Segoe UI', 'Helvetica', sans-serif;
            font-size: 1.4em;
            font-weight: 600;
            color: #444;
            margin-bottom: 1em;
            padding-bottom: 0.3em;
            border-bottom: 1px solid #eee;
            display: flex;
            align-items: center;
        }
        
        /* Style pour les diagrammes Mermaid */
        .mermaid {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }
        """
    # Nettoyer le contenu pour éviter les redondances
    # Vérifier si le contenu contient déjà un titre h1
    has_h1 = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL) is not None

    # Détecter le titre du document dans un h2 (pour éviter la duplication)
    first_h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
    first_h2_title = first_h2_match.group(1).strip() if first_h2_match else None

    # Si nous avons déjà un h1 et un h2 avec le même contenu, supprimer le h2
    if has_h1 and first_h2_title:
        h1_content_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.DOTALL)
        if h1_content_match:
            h1_content = h1_content_match.group(1).strip()
            # Si le contenu du h1 et du premier h2 sont similaires, supprimer le h2
            if h1_content.lower() == first_h2_title.lower() or \
               h1_content.lower() in first_h2_title.lower() or \
               first_h2_title.lower() in h1_content.lower():
                content = re.sub(r'<h2[^>]*>' + re.escape(first_h2_title) + r'</h2>', '', content, count=1)

    # Ajouter un titre principal si nécessaire et si skip_title est False
    if not has_h1 and not skip_title:
        # Détecter si le contenu est une page de navigation
        nav_title_match = re.search(r'^([^<]+)(?:<i[^>]*></i>.*)?$', content.strip().split('\n')[0], re.DOTALL)
        
        # Essayer de détecter un titre dans une balise h2
        title_match = re.search(r'<h2[^>]*>(.*?)</h2>', content, re.DOTALL)
        
        if nav_title_match and len(nav_title_match.group(0)) < 200:
            # C'est probablement un titre de navigation
            nav_title = nav_title_match.group(0)
            # Remplacer les balises d'icônes par une icône visuelle
            clean_title = re.sub(r'<i[^>]*></i>', '<span class="nav-icon"></span>', nav_title)
            content = f'<h1 class="page-title">{clean_title}</h1>\n{content}'
        elif title_match:
            # Utiliser le titre h2 existant comme titre principal
            title = title_match.group(1)
            # Remplacer les symboles > par des icônes dans le titre
            title = re.sub(r'\s*>\s*', ' <i class="nav-icon"></i> ', title)
            # Supprimer le h2 pour éviter la redondance
            content = re.sub(r'<h2[^>]*>(.*?)</h2>', '', content, count=1)
            content = f'<h1 class="page-title">{title}</h1>\n{content}'
        else:
            # Utiliser la première ligne comme titre si elle n'est pas trop longue
            first_line = content.strip().split('\n')[0] if content.strip() else 'Documentation'
            title = first_line if len(first_line) < 100 else 'Documentation'
            # Remplacer les symboles > par des icônes dans le titre
            title = re.sub(r'\s*>\s*', ' <i class="nav-icon"></i> ', title)
            content = f'<h1 class="page-title">{title}</h1>\n{content}'

    # Structurer le contenu en sections
    def wrap_sections_with_tags(html_content):
        """
        Enveloppe chaque section (définie par un h2) dans des balises <section>
        pour améliorer la structure HTML et faciliter le styling.
        """
        # Utiliser une expression régulière pour trouver tous les h2 et leur contenu associé
        pattern = r'(<h2[^>]*>.*?</h2>)(.*?)(?=<h2|$)'
        
        def replacement(match):
            h2_tag = match.group(1)
            content = match.group(2)
            return f'<section class="doc-section">{h2_tag}{content}</section>'
        
        # Remplacer chaque section par une version enveloppée
        result = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        return result
    
    # Appliquer la structuration en sections
    content = wrap_sections_with_tags(content)

    # Construire la page HTML complète
    html = f"""<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Documentation</title>
        <style>
        {css}
        </style>
    </head>
    <body>
        <div class="content-container">
            <div class="page-content">
                {content}
            </div>
        </div>
        {mermaid_js}
        <script>
            // Ajuster la taille des icônes SVG dans les titres
            document.addEventListener('DOMContentLoaded', function() {{
                var headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                for (var i = 0; i < headings.length; i++) {{
                    var heading = headings[i];
                    // Ajuster la taille des icônes SVG dans les titres
                    var svgs = heading.querySelectorAll('svg');
                    for (var j = 0; j < svgs.length; j++) {{
                        var svg = svgs[j];
                        svg.style.height = '1.2em';
                        svg.style.verticalAlign = 'middle';
                    }}
                }}
            }});
        </script>
    </body>
</html>
"""

    return html
