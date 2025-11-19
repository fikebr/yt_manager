from app.core.app import YTManagerApp
from app.ui.main_window import MainWindow

def main():
    app = YTManagerApp()
    root = MainWindow(app)
    root.mainloop()

if __name__ == "__main__":
    main()

