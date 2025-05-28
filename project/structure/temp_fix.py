def add_topic_cards_bubble(self):
    """Affiche des bulles individuelles pour chaque rubrique d'aide"""
    # Définir les rubriques disponibles
    topics = [
        {
            "title": "Création de projet",
            "description": "Créer un nouveau squelette de projet avec différentes technologies",
            "icon": "code",
        },
        {
            "title": "Navigation fichiers",
            "description": "Explorer et interagir avec les fichiers de votre projet",
            "icon": "folder-code",
        },
        {
            "title": "Aide au codage",
            "description": "Obtenir de l'aide pour résoudre des problèmes de code",
            "icon": "circle-help",
        },
        {
            "title": "Suggestions d'amélioration",
            "description": "Recevoir des suggestions pour améliorer votre code",
            "icon": "brain",
        },
        {
            "title": "Documentation",
            "description": "Générer de la documentation pour votre code",
            "icon": "file-text",
        },
    ]

    # Ajouter un titre pour les options d'aide
    title_bubble = ChatBubble(
        "<b>Comment puis-je vous aider aujourd'hui ?</b>", is_user=False
    )
    title_layout = QHBoxLayout()
    title_layout.setContentsMargins(0, 0, 0, 0)
    title_layout.addWidget(title_bubble)
    title_layout.addStretch(1)  # Espace à droite pour aligner à gauche

    title_container = QWidget()
    title_container.setLayout(title_layout)
    self.chat_layout.addWidget(title_container)

    # Créer un conteneur principal pour toutes les bulles de topics
    main_container = QWidget()
    main_layout = QVBoxLayout(main_container)  # Layout vertical pour empiler les cartes
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(8)

    # Créer une bulle pour chaque topic
    for topic in topics:
        # Créer une carte pour le topic
        icon_name = topic.get("icon", "circle-help")
        
        # Chemin vers le fichier SVG original
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "assets", "icons", f"{icon_name}.svg")
        
        # Créer un fichier SVG temporaire coloré en vert
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        temp_svg_path = os.path.join(temp_dir, f"temp_{icon_name}.svg")
        
        # Charger et colorer le SVG en vert
        import re
        svg_content = ""
        with open(icon_path, "r") as f:
            svg_content = f.read()
        
        # Remplacer toutes les couleurs par du vert
        svg_content = re.sub(r'fill="#[0-9A-Fa-f]{3,6}"', 'fill="#22D47A"', svg_content)
        svg_content = re.sub(r'stroke="#[0-9A-Fa-f]{3,6}"', 'stroke="#22D47A"', svg_content)
        
        # Ajouter un attribut fill par défaut si nécessaire
        if '<svg' in svg_content and 'fill="' not in svg_content.split('<svg')[1].split('>')[0]:
            svg_content = svg_content.replace('<svg', '<svg fill="#22D47A"', 1)
        
        # Écrire le fichier SVG temporaire
        with open(temp_svg_path, "w") as f:
            f.write(svg_content)
        
        # Créer la carte avec l'icône SVG verte
        card = TopicCard(
            title=topic["title"],
            description=topic["description"],
            icon_pixmap=temp_svg_path
        )
        
        card.clicked.connect(
            lambda checked=False, t=topic["title"]: self.handle_topic_selection(t)
        )

        # Conteneur horizontal pour centrer la bulle
        card_layout = QHBoxLayout()
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.addStretch(1)  # Espace à gauche pour centrer
        card_layout.addWidget(card)
        card_layout.addStretch(1)  # Espace à droite pour centrer

        # Ajouter le layout horizontal au layout principal
        card_container = QWidget()
        card_container.setLayout(card_layout)
        main_layout.addWidget(card_container)

    # Ajouter le conteneur principal au chat
    self.chat_layout.addWidget(main_container)

    # Faire défiler vers le bas
    QTimer.singleShot(50, self.scroll_to_bottom)

    return main_container
