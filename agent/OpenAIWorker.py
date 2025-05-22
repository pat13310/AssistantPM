from PySide6.QtCore import QObject, Signal, Slot
import openai


class OpenAIWorker(QObject):
    partial = Signal(str)   # Emis seulement si stream=True
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, api_key, model, messages, stream=True):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.stream = stream

    @Slot()
    def run(self):
        try:
            client = openai.OpenAI(api_key=self.api_key)
            reply = ""

            if self.stream:
                stream_response = client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True
                )

                for chunk in stream_response:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        part = chunk.choices[0].delta.content
                        reply += part
                        self.partial.emit(part)
            else:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    temperature=0.7,
                    max_tokens=1000,
                    stream=False
                )
                if response.choices:
                    reply = response.choices[0].message.content.strip()
                else:
                    reply = "" # Ou gérer l'absence de réponse

            self.finished.emit(reply)

        except Exception as e:
            self.error.emit(str(e))
