from pathlib import Path
import tkinter as tk

from pressure_model import PressureModel
from pressure_view import PressureView


BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data.txt"
LOG_FILE = BASE_DIR / "errors.log"


def main() -> None:
    root = tk.Tk()
    model = PressureModel()
    PressureView(root, model, DATA_FILE, LOG_FILE)
    root.mainloop()


if __name__ == "__main__":
    main()