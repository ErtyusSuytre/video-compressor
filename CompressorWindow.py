from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow
from CompressorWidget import CompressorWidget
from SettingsWidget import SettingsWindow

class CompressorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Video Compressor")
        self.compressor_widget = CompressorWidget()
        self.setCentralWidget(self.compressor_widget)
        
        file_menu = self.menuBar().addMenu("File")
        
        self.settings = QAction("Settings", self)
        self.settings.triggered.connect(self.openSettings)
        
        file_menu.addAction(self.settings)
        
        
        
    def openSettings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.save_button.clicked.connect(self.compressor_widget.settings_changed)
        self.settings_window.show()