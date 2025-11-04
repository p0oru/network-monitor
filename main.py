"""
NetScope - Main Entry Point
Network and System Performance Monitor
"""
import sys
import os

# Add netscope to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from netscope.ui.main_window import MainWindow
from netscope import __version__


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("NetScope")
    app.setApplicationVersion(__version__)
    
    # Create and show main window
    window = MainWindow(version=__version__)
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()