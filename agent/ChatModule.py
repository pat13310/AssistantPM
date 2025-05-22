from PySide6.QtCore import QThread
from agent.BaseModule import BaseModule
from agent.OpenAIWorker import OpenAIWorker

class ChatModule(BaseModule):
    name = "chat"

    def __init__(self, api_key, model="gpt-3.5-turbo", stream=True):
        self.api_key = api_key
        self.model = model
        self.stream = stream

    def can_handle(self, task: str) -> bool:
        return True

    def handle_async(self, task: str, callback, error_callback, partial_callback=None):
        self.thread = QThread()
        self.worker = OpenAIWorker(
            api_key=self.api_key,
            model=self.model,
            messages=[{"role": "user", "content": task}],
            stream=self.stream
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(callback)
        self.worker.error.connect(error_callback)

        if self.stream and partial_callback:
            self.worker.partial.connect(partial_callback)

        # Note: The primary connections for callback and error_callback are made earlier.
        # The connections below are for thread and worker lifecycle management.

        # Setup thread and worker cleanup
        # QThread.finished is emitted after the event loop has finished.
        self.thread.finished.connect(self.worker.deleteLater) 
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Ensure thread quits when worker is done or errors out
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.start()
