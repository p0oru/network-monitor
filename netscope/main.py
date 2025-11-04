"""
NetScope - Network and System Performance Monitor
Main entry point for the application.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("NetScope")
    app.setOrganizationName("NetScope")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
