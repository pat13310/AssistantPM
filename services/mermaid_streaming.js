// Script pour gérer les diagrammes Mermaid en mode streaming
function initMermaid() {
    if (typeof mermaid !== 'undefined') {
        try {
            // Réinitialiser Mermaid pour traiter les nouveaux diagrammes
            mermaid.contentLoaded();
            
            // Redimensionner les SVG après l'initialisation
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
function loadMermaid() {
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
}

// Observer pour détecter les changements dans le DOM (utile pour le streaming)
function setupMermaidObserver() {
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
}

// Initialiser tout
loadMermaid();
setupMermaidObserver();
