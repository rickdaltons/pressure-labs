from dataclasses import dataclass
from datetime import datetime


@dataclass
class PressureMeasurement:
    measurement_date: datetime.date
    height: float
    value: int


def parse_pressure_measurement(line: str) -> PressureMeasurement:
    parts = line.split()

    object_type = parts[0]
    date_text = parts[1]
    height_text = parts[2]
    value_text = parts[3]

    measurement_date = datetime.strptime(date_text, "%Y.%m.%d").date()
    height = float(height_text)
    value = int(value_text)

    return PressureMeasurement(
        measurement_date=measurement_date,
        height=height,
        value=value,
    )


def print_pressure_measurement(measurement: PressureMeasurement) -> None:
    print("Сформирован объект:")
    print(f"Дата: {measurement.measurement_date}")
    print(f"Высота: {measurement.height}")
    print(f"Значение давления: {measurement.value}")


def main() -> None:
    line = input("Введите данные измерения давления: ")

    measurement = parse_pressure_measurement(line)

    print_pressure_measurement(measurement)


if __name__ == "__main__":
    main()
