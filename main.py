from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


DATA_FILE = Path(__file__).with_name("data.txt")
DATE_FORMAT = "%Y.%m.%d"


@dataclass
class PressureMeasurement:
    measurement_date: date
    height: float
    value: int


def parse_pressure_measurement(line: str) -> PressureMeasurement:
    parts = line.split()

    measurement_date = datetime.strptime(parts[1], DATE_FORMAT).date()
    height = float(parts[2])
    value = int(parts[3])

    return PressureMeasurement(
        measurement_date=measurement_date,
        height=height,
        value=value,
    )


def read_measurements_from_file(file_path: Path) -> list[PressureMeasurement]:
    measurements = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                measurements.append(parse_pressure_measurement(line))

    return measurements


def measurement_to_table_row(
    measurement: PressureMeasurement,
) -> tuple[str, str, str]:
    return (
        measurement.measurement_date.strftime(DATE_FORMAT),
        str(measurement.height),
        str(measurement.value),
    )


def create_measurement_from_fields(
    date_text: str,
    height_text: str,
    value_text: str,
) -> PressureMeasurement:
    measurement_date = datetime.strptime(date_text, DATE_FORMAT).date()
    height = float(height_text)
    value = int(value_text)

    return PressureMeasurement(
        measurement_date=measurement_date,
        height=height,
        value=value,
    )


class PressureApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.measurements: list[PressureMeasurement] = []

        self.date_entry: ttk.Entry
        self.height_entry: ttk.Entry
        self.value_entry: ttk.Entry
        self.table: ttk.Treeview

        self.configure_window()
        self.create_widgets()
        self.load_initial_data()

    def configure_window(self) -> None:
        self.root.title("Практическая работа 2 — Измерения давления")
        self.root.geometry("700x450")
        self.root.resizable(False, False)

    def create_widgets(self) -> None:
        title_label = ttk.Label(
            self.root,
            text="Список измерений давления",
            font=("Arial", 16),
        )
        title_label.pack(pady=10)

        self.create_table()
        self.create_input_form()
        self.create_buttons()

    def create_table(self) -> None:
        columns = ("date", "height", "value")

        self.table = ttk.Treeview(
            self.root,
            columns=columns,
            show="headings",
            height=10,
        )

        self.table.heading("date", text="Дата")
        self.table.heading("height", text="Высота")
        self.table.heading("value", text="Значение давления")

        self.table.column("date", width=180, anchor="center")
        self.table.column("height", width=180, anchor="center")
        self.table.column("value", width=220, anchor="center")

        self.table.pack(pady=10)

    def create_input_form(self) -> None:
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Дата:").grid(row=0, column=0, padx=5)
        self.date_entry = ttk.Entry(form_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, "2024.05.20")

        ttk.Label(form_frame, text="Высота:").grid(row=0, column=2, padx=5)
        self.height_entry = ttk.Entry(form_frame, width=15)
        self.height_entry.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="Давление:").grid(row=0, column=4, padx=5)
        self.value_entry = ttk.Entry(form_frame, width=15)
        self.value_entry.grid(row=0, column=5, padx=5)

    def create_buttons(self) -> None:
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)

        add_button = ttk.Button(
            button_frame,
            text="Добавить",
            command=self.add_measurement,
        )
        add_button.grid(row=0, column=0, padx=10)

        delete_button = ttk.Button(
            button_frame,
            text="Удалить выбранный",
            command=self.delete_selected_measurement,
        )
        delete_button.grid(row=0, column=1, padx=10)

        reload_button = ttk.Button(
            button_frame,
            text="Загрузить из файла",
            command=self.load_initial_data,
        )
        reload_button.grid(row=0, column=2, padx=10)

    def load_initial_data(self) -> None:
        self.measurements = read_measurements_from_file(DATA_FILE)
        self.update_table()

    def update_table(self) -> None:
        for row in self.table.get_children():
            self.table.delete(row)

        for measurement in self.measurements:
            self.table.insert(
                "",
                tk.END,
                values=measurement_to_table_row(measurement),
            )

    def add_measurement(self) -> None:
        date_text = self.date_entry.get()
        height_text = self.height_entry.get()
        value_text = self.value_entry.get()

        if not date_text or not height_text or not value_text:
            messagebox.showwarning("Ошибка", "Заполните все поля.")
            return

        try:
            measurement = create_measurement_from_fields(
                date_text,
                height_text,
                value_text,
            )
        except ValueError:
            messagebox.showwarning(
                "Ошибка",
                "Проверьте формат данных: дата гггг.мм.дд, "
                "высота — дробное число, давление — целое число.",
            )
            return

        self.measurements.append(measurement)
        self.update_table()
        self.clear_height_and_value_fields()

    def delete_selected_measurement(self) -> None:
        selected_item = self.table.selection()

        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите строку для удаления.")
            return

        selected_index = self.table.index(selected_item[0])
        del self.measurements[selected_index]

        self.update_table()

    def clear_height_and_value_fields(self) -> None:
        self.height_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)


def main() -> None:
    root = tk.Tk()
    PressureApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
