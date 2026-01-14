from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout
from PySide6.QtCore import Qt
import os

class SettingsDialog(QDialog):
    def __init__(self, tool_path, result_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(320, 180)
        self.tool_path = tool_path
        self.result_path = result_path
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Tool version
        version_label = QLabel(f"Tool version: {self.get_tool_version()}")
        layout.addWidget(version_label)

        # Result path
        result_label = QLabel(f"Result path: {self.result_path}")
        layout.addWidget(result_label)

        open_btn = QPushButton("Open Output Folder")
        open_btn.clicked.connect(self.open_output_folder)
        layout.addWidget(open_btn)

        # Credits
        credits = QLabel("PartFetch Utility\nPowered by easyeda2kicad\n© 2026 Kaustubh")
        credits.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(credits)

        self.setLayout(layout)

    def get_tool_version(self):
        # Try to get version from CLI tool
        import subprocess
        try:
            result = subprocess.run([self.tool_path, "--version"], capture_output=True, text=True, timeout=3)
            return result.stdout.strip() or "Unknown"
        except Exception:
            return "Unknown"

    def open_output_folder(self):
        if os.path.exists(self.result_path):
            os.startfile(self.result_path)
        else:
            QFileDialog.getExistingDirectory(self, "Select Output Folder", self.result_path)
