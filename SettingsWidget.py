from PySide6.QtWidgets import QLabel, QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import QSettings

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Settings")
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        
        # Label
        label = QLabel("Select Unit:")
        
        # Dropdown
        self.drop_down = QComboBox()
        self.drop_down.addItems(["Bytes", "KiloBytes", "MegaBytes", "KibiBytes", "MebiBytes"])
        
        # Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.saveSettings)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        
        
        layout = QVBoxLayout()
        layout.addWidget(self.drop_down)
        layout.addWidget(label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def saveSettings(self):
        print(self.drop_down.currentText())
        self.settings.setValue("Estimated Size Unit", self.drop_down.currentText())
        self.close()