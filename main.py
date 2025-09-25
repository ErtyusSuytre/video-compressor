from PySide6.QtWidgets import QApplication

from CompressorWindow import CompressorWindow
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication()
    compressor = CompressorWindow()
    compressor.show()
    app.exec()