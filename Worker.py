from PySide6.QtCore import QRunnable, QObject, Signal
import logging

class WorkerSignals(QObject):
    finished = Signal()
    result = Signal(object)
    error = Signal()

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    def run(self):
        try:
            logging.info("Running worker...")
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            logging.error(e)
            self.signals.error.emit()
            return
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()