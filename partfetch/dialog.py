from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QRadioButton, QButtonGroup, QPushButton, QProgressBar, QHBoxLayout
from PySide6.QtCore import Signal, Qt

class MainDialog(QDialog):
    closeRequested = Signal()

    def __init__(self, settings_dialog=None):
        super().__init__()
        from PySide6.QtGui import QIcon
        from tray import ICON_PATH
        self.setWindowTitle("PartFetch")
        self.setFixedSize(320, 220)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.settings_dialog = settings_dialog
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # ASCII Art
        ascii_art = "  ____            _   _____    _       _     \n" + \
            "|  _ \ __ _ _ __| |_|  ___|__| |_ ___| |__  \n" + \
            "| |_) / _` | '__| __| |_ / _ \ __/ __| '_ \ \n" + \
            "|  __/ (_| | |  | |_|  _|  __/ || (__| | | |\n" + \
            "|_|   \__,_|_|   \__|_|  \___|\__\___|_| |_|\n"
        
        art_label = QLabel(ascii_art)
        art_label.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 9px;")
        art_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(art_label)

        self.part_input = QLineEdit()
        self.part_input.setPlaceholderText("LCSC Part Number")
        layout.addWidget(self.part_input)

        self.radio_all = QRadioButton("All")
        self.radio_footprint = QRadioButton("Footprint")
        self.radio_symbol = QRadioButton("Schematic")
        self.radio_3d = QRadioButton("3D Model")
        self.radio_all.setChecked(True)

        # Radio layout: 'AllBtn' on one line, others on next line
        radio_all_layout = QHBoxLayout()
        radio_all_layout.addWidget(self.radio_all)
        layout.addLayout(radio_all_layout)

        radio_others_layout = QHBoxLayout()
        radio_others_layout.addWidget(self.radio_footprint)
        radio_others_layout.addWidget(self.radio_symbol)
        radio_others_layout.addWidget(self.radio_3d)
        layout.addLayout(radio_others_layout)

        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        btn_layout.addWidget(self.download_btn)
        self.settings_btn = QPushButton("Settings")
        btn_layout.addWidget(self.settings_btn)
        layout.addLayout(btn_layout)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.hide()
        layout.addWidget(self.progress)

        self.setLayout(layout)

        self.download_btn.clicked.connect(self.start_download)
        self.settings_btn.clicked.connect(self.show_settings)


    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.closeRequested.emit()

    def showEvent(self, event):
        # Position window at bottom right
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        x = screen.x() + screen.width() - self.width() - 20
        y = screen.y() + screen.height() - self.height() - 40
        self.move(x, y)
        super().showEvent(event)

    def show_settings(self):
        if self.settings_dialog:
            self.settings_dialog.show()

    def start_download(self):
        self.progress.show()
        self.status_label.setText("Downloading...")
        self.download_btn.setEnabled(False)
        part_number = self.part_input.text().strip()
        
        if not part_number:
            self.status_label.setText("Please enter a part number.")
            self.progress.hide()
            self.download_btn.setEnabled(True)
            return
        
        # Build CLI args
        args = []
        if self.radio_all.isChecked():
            args += ["--full"]
        else:
            if self.radio_symbol.isChecked():
                args += ["--symbol"]
            if self.radio_footprint.isChecked():
                args += ["--footprint"]
            if self.radio_3d.isChecked():
                args += ["--3d"]
        args += ["--lcsc_id=" + part_number]
        args += ["--overwrite"]  # Always overwrite for now

        # Start CLIWorker in QThread
        from PySide6.QtCore import QThread
        from cli_worker import CLIWorker
        self.worker = CLIWorker(args)
        self.worker_thread = QThread()
        self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_cli_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def on_cli_finished(self, status, output, exit_code):
        self.progress.hide()
        self.status_label.setText(status)
        self.download_btn.setEnabled(True)
        # Optionally show details in a popup
        if exit_code != 0 or "complete" not in status.lower():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "CLI Output", output)
