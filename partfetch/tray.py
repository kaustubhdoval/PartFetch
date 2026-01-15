from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from dialog import MainDialog
from settings import SettingsDialog
import sys
import os

APP_NAME = "PartFetch"
ICON_PATH = "partfetch/assets/app.ico"  # Update with actual path

def create_tray(app):
    tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), app)
    menu = QMenu()
    show_action = QAction("Show Window")
    settings_action = QAction("Settings")
    exit_action = QAction("Exit")
    menu.addAction(show_action)
    menu.addAction(settings_action)
    menu.addSeparator()
    menu.addAction(exit_action)
    tray_icon.setContextMenu(menu)

    user_docs = os.path.join(os.path.expanduser("~"), "Documents", "KiCad", "easyeda2kicad") 
    result_path = user_docs  # Output directory for results
    tool_path = "easyeda2kicad"

    settings_dialog = SettingsDialog(tool_path, result_path)

    dialog = MainDialog(settings_dialog)

    show_action.triggered.connect(dialog.show)
    settings_action.triggered.connect(settings_dialog.show)
    exit_action.triggered.connect(app.quit)
    tray_icon.activated.connect(lambda reason: dialog.show() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)

    dialog.closeRequested.connect(dialog.hide)
    tray_icon.show()
    return tray_icon
