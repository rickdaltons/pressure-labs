from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
import re


DATE_FORMAT = "%Y.%m.%d"


class PressureParseError(Exception):
    """Ошибка разбора строки с данными измерения давления."""


@dataclass(frozen=True)
class PressureMeasurement:
    measurement_date: date
    height: float
    value: int

    def to_row(self) -> tuple[str, str, str]:
        return (
            self.measurement_date.strftime(DATE_FORMAT),
            str(self.height),
            str(self.value),
        )

    def to_file_line(self) -> str:
        return (
            f"Давление {self.measurement_date.strftime(DATE_FORMAT)} "
            f"{self.height} {self.value}"
        )


class PressureParser:
    LINE_PATTERN = re.compile(
        r"^Давление\s+(\d{4}\.\d{2}\.\d{2})\s+"
        r"([-+]?\d+(?:[.,]\d+)?)\s+([-+]?\d+)\s*$"
    )

    @classmethod
    def parse_line(cls, line: str) -> PressureMeasurement:
        line = line.strip()

        if not line:
            raise PressureParseError("Пустая строка.")

        match = cls.LINE_PATTERN.match(line)

        if not match:
            raise PressureParseError(
                "Строка должна иметь формат: Давление гггг.мм.дд высота значение."
            )

        date_text, height_text, value_text = match.groups()

        return cls.create_measurement(date_text, height_text, value_text)

    @staticmethod
    def create_measurement(
        date_text: str,
        height_text: str,
        value_text: str,
    ) -> PressureMeasurement:
        try:
            measurement_date = datetime.strptime(date_text, DATE_FORMAT).date()
        except ValueError as error:
            raise PressureParseError(
                "Дата должна быть указана в формате гггг.мм.дд."
            ) from error

        try:
            height = float(height_text.replace(",", "."))
        except ValueError as error:
            raise PressureParseError("Высота должна быть дробным числом.") from error

        try:
            value = int(value_text)
        except ValueError as error:
            raise PressureParseError(
                "Значение давления должно быть целым числом."
            ) from error

        return PressureMeasurement(
            measurement_date=measurement_date,
            height=height,
            value=value,
        )


class PressureModel:
    def __init__(self) -> None:
        self._measurements: list[PressureMeasurement] = []

    @property
    def measurements(self) -> list[PressureMeasurement]:
        return self._measurements.copy()

    def load_from_file(self, file_path: Path, log_path: Path) -> int:
        self._measurements.clear()
        invalid_count = 0

        with open(file_path, "r", encoding="utf-8") as input_file, open(
            log_path,
            "w",
            encoding="utf-8",
        ) as log_file:
            for line_number, line in enumerate(input_file, start=1):
                try:
                    measurement = PressureParser.parse_line(line)
                except PressureParseError as error:
                    invalid_count += 1
                    log_file.write(
                        f"Строка {line_number}: {line.strip()} | Ошибка: {error}\n"
                    )
                else:
                    self._measurements.append(measurement)

        return invalid_count

    def add_measurement(
        self,
        date_text: str,
        height_text: str,
        value_text: str,
    ) -> None:
        measurement = PressureParser.create_measurement(
            date_text,
            height_text,
            value_text,
        )
        self._measurements.append(measurement)

    def add_measurement_object(self, measurement: PressureMeasurement) -> None:
        self._measurements.append(measurement)

    def remove_measurement(self, index: int) -> None:
        if index < 0 or index >= len(self._measurements):
            raise IndexError("Некорректный индекс удаляемого объекта.")

        del self._measurements[index]

    def remove_by_condition(self, condition) -> int:
        old_count = len(self._measurements)
        self._measurements = [
            measurement
            for measurement in self._measurements
            if not condition(measurement)
        ]
        return old_count - len(self._measurements)

    def save_to_file(self, file_path: Path) -> None:
        with open(file_path, "w", encoding="utf-8") as file:
            for measurement in self._measurements:
                file.write(measurement.to_file_line() + "\n")

    def get_table_rows(self) -> list[tuple[str, str, str]]:
        return [measurement.to_row() for measurement in self._measurements]