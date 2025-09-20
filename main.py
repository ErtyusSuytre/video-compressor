from PySide6.QtWidgets import QApplication

from WidgetCompressor import WidgetCompressor
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication()
    compressor = WidgetCompressor()
    compressor.show()
    app.exec()