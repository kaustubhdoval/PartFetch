from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QCursor
from PySide6.QtCore import Qt
from dialog import MainDialog
from settings import SettingsDialog
import os
import sys

APP_NAME = "PartFetch"

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    # Running in Dev Mode
    base_path = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(base_path, "assets", "PartFetchLogo.ico")

def create_tray(app):

    app.setQuitOnLastWindowClosed(False)


    # Check if icon exists and warn if not
    if not os.path.exists(ICON_PATH):
        print(f"WARNING: Tray icon not found at {ICON_PATH}")
    icon_obj = QIcon(ICON_PATH) if os.path.exists(ICON_PATH) else QIcon()
    app.tray_icon = QSystemTrayIcon(icon_obj)
    tray_icon = app.tray_icon

    app.tray_menu = QMenu()
    tray_menu = app.tray_menu
    tray_menu.setTitle("Hello Nerd :)")

    # Set Paths
    user_docs = os.path.join(os.path.expanduser("~"), "Documents", "KiCad", "easyeda2kicad") 
    result_path = user_docs  # Output directory for results
    tool_path = "easyeda2kicad"

    open_action = QAction("Open", tray_menu)
    settings_action = QAction("Settings", tray_menu)
    quit_action = QAction("Quit", tray_menu)

    tray_menu.addAction(open_action)
    tray_menu.addAction(settings_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)

    tray_icon.setContextMenu(tray_menu)

    settings_dialog = SettingsDialog(tool_path, result_path)
    dialog = MainDialog(settings_dialog)

    dialog.setWindowFlags(Qt.WindowType.Window)
    settings_dialog.setWindowFlags(Qt.WindowType.Window)

    open_action.triggered.connect(dialog.show)
    settings_action.triggered.connect(settings_dialog.show)
    quit_action.triggered.connect(app.quit)

    tray_icon.activated.connect(
        lambda r: dialog.show() if r == QSystemTrayIcon.ActivationReason.Trigger else None
    )

    tray_icon.show()
    return tray_icon

