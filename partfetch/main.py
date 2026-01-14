import sys
from PySide6.QtWidgets import QApplication
from tray import create_tray

def main():
    app = QApplication(sys.argv)
    tray = create_tray(app)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
