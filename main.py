from tkinterdnd2 import TkinterDnD

from railway_duty import RailwayTrackManager


if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Используем TkinterDnD вместо tk.Tk
    app = RailwayTrackManager(root)
    root.mainloop()

