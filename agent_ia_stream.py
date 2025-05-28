# agent_ia_stream.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
import re
import asyncio
import datetime

app = FastAPI()
# Initialisation du client OpenAI avec la nouvelle API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/health")
async def health_check():
    """Endpoint pour vérifier si le serveur est en cours d'exécution"""
    return {"status": "ok", "timestamp": datetime.datetime.now().isoformat()}

class PromptRequest(BaseModel):
    message: str
    model: str

def parse_stream_chunk(chunk):
    # Extraction ligne à ligne (améliorable)
    return chunk

@app.post("/chat_stream")
async def chat_stream(request: Request):
    try:
        body = await request.json()
        message = body.get("message", "")
        model = body.get("model", "openai").lower()
    except Exception as e:
        return StreamingResponse(
            iter([f"data: {json.dumps({'text': f'Erreur de traitement de la requête: {str(e)}'})}\n\n"]),
            media_type="text/event-stream"
        )

    async def event_generator():
        if model == "openai":
            # Prompt pour structurer la réponse
            prompt = (
                f"Tu es un assistant pour la création d'arborescences. "
                f"Donne ta réponse, puis la liste des actions JSON comme dans l'exemple :\n"
                f"Réponse: Voici ta structure\n"
                f"Actions: [{{'type':'mkdir','path':'src'}}]"
            )
            chat_msgs = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ]
            try:
                # Vérifier si la clé API est définie
                if not os.getenv("OPENAI_API_KEY"):
                    fake_text = "Erreur: Clé API OpenAI non configurée. Veuillez définir la variable d'environnement OPENAI_API_KEY.\nActions: []"
                    for w in fake_text.split():
                        yield f"data: {json.dumps({'text': w+' '})}\n\n"
                        await asyncio.sleep(0.05)
                    return
                    
                # Appel stream OpenAI avec la nouvelle API
                stream = client.chat.completions.create(
                    model="gpt-4",
                    messages=chat_msgs,
                    max_tokens=600,
                    stream=True
                )
                answer = ""
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        part = chunk.choices[0].delta.content
                        answer += part
                        yield f"data: {json.dumps({'text': part})}\n\n"
                        await asyncio.sleep(0)  # Yield to event loop
            except Exception as e:
                # En cas d'erreur avec l'API, renvoyer un message d'erreur
                error_msg = f"Erreur lors de la communication avec OpenAI: {str(e)}\nActions: []"
                for w in error_msg.split():
                    yield f"data: {json.dumps({'text': w+' '})}\n\n"
                    await asyncio.sleep(0.05)
        elif model == "deepseek":
            # À adapter pour DeepSeek : ici, fake streaming mot à mot
            fake_text = "Réponse: Structure DeepSeek générée.\nActions: [{\"type\": \"mkdir\", \"path\": \"deepseek_dir\"}]"
            for w in fake_text.split():
                yield f"data: {json.dumps({'text': w+' '})}\n\n"
                await asyncio.sleep(0.09)
        else:
            yield f"data: {json.dumps({'text': '[Modèle non supporté]'})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    from dotenv import load_dotenv
    
    # Charger les variables d'environnement depuis un fichier .env s'il existe
    load_dotenv()
    
    # Vérifier si la clé API est configurée
    if not os.getenv("OPENAI_API_KEY"):
        print("\033[93mAttention: La clé API OpenAI n'est pas configurée.\033[0m")
        print("Veuillez définir la variable d'environnement OPENAI_API_KEY ou créer un fichier .env avec OPENAI_API_KEY=votre_clé")
        print("Le serveur démarrera quand même, mais les requêtes à OpenAI échoueront.\n")
    
    print("Démarrage du serveur IA sur http://localhost:8000")
    print("Appuyez sur Ctrl+C pour arrêter le serveur")
    
    # Démarrer le serveur avec gestion des erreurs
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"\033[91mErreur lors du démarrage du serveur: {str(e)}\033[0m")
