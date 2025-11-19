from app.core.app import YTManagerApp
from app.ui.video_queue import MainWindow

def main():
    app = YTManagerApp()
    root = MainWindow(app)
    root.mainloop()

if __name__ == "__main__":
    main()

