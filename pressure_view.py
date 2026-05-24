from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from pressure_model import PressureModel, PressureParseError


class PressureView:
    def __init__(
        self,
        root: tk.Tk,
        model: PressureModel,
        data_path: Path,
        log_path: Path,
    ) -> None:
        self.root = root
        self.model = model
        self.data_path = data_path
        self.log_path = log_path

        self.date_entry: ttk.Entry
        self.height_entry: ttk.Entry
        self.value_entry: ttk.Entry
        self.table: ttk.Treeview

        self.configure_window()
        self.create_widgets()
        self.load_data()

    def configure_window(self) -> None:
        self.root.title("Практическая работа 3 — Измерения давления")
        self.root.geometry("750x470")
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

        ttk.Button(
            button_frame,
            text="Добавить",
            command=self.add_measurement,
        ).grid(row=0, column=0, padx=10)

        ttk.Button(
            button_frame,
            text="Удалить выбранный",
            command=self.delete_selected_measurement,
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            button_frame,
            text="Загрузить из файла",
            command=self.load_data,
        ).grid(row=0, column=2, padx=10)

    def load_data(self) -> None:
        invalid_count = self.model.load_from_file(self.data_path, self.log_path)
        self.update_table()

        if invalid_count > 0:
            messagebox.showinfo(
                "Загрузка данных",
                f"Некорректных строк пропущено: {invalid_count}.\n"
                f"Информация записана в файл: {self.log_path.name}",
            )

    def update_table(self) -> None:
        for row in self.table.get_children():
            self.table.delete(row)

        for row in self.model.get_table_rows():
            self.table.insert("", tk.END, values=row)

    def add_measurement(self) -> None:
        date_text = self.date_entry.get()
        height_text = self.height_entry.get()
        value_text = self.value_entry.get()

        try:
            self.model.add_measurement(date_text, height_text, value_text)
        except PressureParseError as error:
            messagebox.showwarning("Ошибка", str(error))
            return

        self.update_table()
        self.clear_height_and_value_fields()

    def delete_selected_measurement(self) -> None:
        selected_item = self.table.selection()

        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите строку для удаления.")
            return

        selected_index = self.table.index(selected_item[0])

        try:
            self.model.remove_measurement(selected_index)
        except IndexError as error:
            messagebox.showwarning("Ошибка", str(error))
            return

        self.update_table()

    def clear_height_and_value_fields(self) -> None:
        self.height_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)