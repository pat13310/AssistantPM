def on_interactive_choice(self, bubble_type, choice):
    """Gère la sélection d'une option dans une bulle interactive"""
    # Ajouter le choix de l'utilisateur comme message
    self.add_chat_bubble(f"J'ai choisi: {choice}", is_user=True)

    if bubble_type == "confirm_path":
        # L'utilisateur a répondu à la confirmation du chemin
        self.on_path_confirmation(choice)
        
    elif bubble_type == "technology":
        # L'utilisateur a choisi une technologie, proposer les types d'applications
        app_types = self.get_app_types_for_technology(choice)
        self.add_chat_bubble(
            f"Pour la technologie <b>{choice}</b>, voici les types d'applications possibles :",
            is_user=False,
        )
        self.add_interactive_bubble(
            f"Quel type d'application {choice} souhaitez-vous créer ?",
            app_types,
            bubble_type="app_type",
        )

    elif bubble_type == "app_type":
        # L'utilisateur a choisi un type d'application, proposer des fonctionnalités
        features = self.get_features_for_app_type(choice)
        self.add_chat_bubble(
            f"Pour une application de type <b>{choice}</b>, voici les fonctionnalités que je peux inclure :",
            is_user=False,
        )
        self.add_interactive_bubble(
            f"Quelles fonctionnalités souhaitez-vous inclure dans votre {choice} ?",
            features,
            bubble_type="features",
        )

    elif bubble_type == "features":
        # L'utilisateur a choisi des fonctionnalités, générer un résumé
        self.add_chat_bubble(
            "Je vais maintenant générer un squelette d'application basé sur vos choix. "
            "Veuillez patienter un instant...",
            is_user=False,
        )
        # Simuler un délai pour la génération
        QTimer.singleShot(1500, self.generate_app_skeleton)
