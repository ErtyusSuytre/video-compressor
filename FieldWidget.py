from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel

class FieldWidget(QWidget):
    def __init__(self, left_label: Optional[str] = None, right_label: Optional[str] = None):
        """
        Initializes a ButtonWidget.

        Args:
            left_label (Optional[str]): The label on the left side of the field with a colon.
            right_label (Optional[str]): The label on the right side of the field.

        """
        super().__init__()
        
        self.field_layout = QHBoxLayout()
        
        if left_label is not None:
            self.left_label = QLabel(f"{left_label}: ")
            
        self.field = QLineEdit()
        
        if left_label is not None:
            self.field_layout.addWidget(self.left_label)
        self.field_layout.addWidget(self.field)
        if right_label is not None:
            self.right_label = QLabel(f"{right_label}")
            self.field_layout.addWidget(self.right_label)
        
        self.setLayout(self.field_layout)