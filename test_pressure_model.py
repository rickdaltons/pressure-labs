from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from pressure_model import PressureModel, PressureParseError, PressureParser


class TestPressureParser(unittest.TestCase):
    def test_parse_correct_line(self) -> None:
        measurement = PressureParser.parse_line("Давление 2024.03.28 120.5 760")

        self.assertEqual(measurement.measurement_date, date(2024, 3, 28))
        self.assertEqual(measurement.height, 120.5)
        self.assertEqual(measurement.value, 760)

    def test_parse_height_with_comma(self) -> None:
        measurement = PressureParser.parse_line("Давление 2024.04.10 135,2 755")

        self.assertEqual(measurement.height, 135.2)
        self.assertEqual(measurement.value, 755)

    def test_parse_invalid_date(self) -> None:
        with self.assertRaises(PressureParseError):
            PressureParser.parse_line("Давление 2024.99.28 120.5 760")

    def test_parse_invalid_height(self) -> None:
        with self.assertRaises(PressureParseError):
            PressureParser.parse_line("Давление 2024.03.28 ошибка 760")

    def test_parse_invalid_value(self) -> None:
        with self.assertRaises(PressureParseError):
            PressureParser.parse_line("Давление 2024.03.28 120.5 семьсот")

    def test_parse_invalid_object_type(self) -> None:
        with self.assertRaises(PressureParseError):
            PressureParser.parse_line("Температура 2024.03.28 120.5 760")


class TestPressureModel(unittest.TestCase):
    def test_add_measurement(self) -> None:
        model = PressureModel()

        model.add_measurement("2024.03.28", "120.5", "760")

        self.assertEqual(len(model.measurements), 1)
        self.assertEqual(model.measurements[0].height, 120.5)
        self.assertEqual(model.measurements[0].value, 760)

    def test_remove_measurement(self) -> None:
        model = PressureModel()
        model.add_measurement("2024.03.28", "120.5", "760")

        model.remove_measurement(0)

        self.assertEqual(len(model.measurements), 0)

    def test_remove_measurement_with_wrong_index(self) -> None:
        model = PressureModel()

        with self.assertRaises(IndexError):
            model.remove_measurement(0)

    def test_get_table_rows(self) -> None:
        model = PressureModel()
        model.add_measurement("2024.03.28", "120.5", "760")

        rows = model.get_table_rows()

        self.assertEqual(rows, [("2024.03.28", "120.5", "760")])

    def test_load_from_file_skips_invalid_lines(self) -> None:
        with TemporaryDirectory() as temp_dir:
            data_path = Path(temp_dir) / "data.txt"
            log_path = Path(temp_dir) / "errors.log"

            data_path.write_text(
                "Давление 2024.03.28 120.5 760\n"
                "Давление 2024.99.28 120.5 760\n"
                "Давление 2024.04.10 135.2 755\n",
                encoding="utf-8",
            )

            model = PressureModel()
            invalid_count = model.load_from_file(data_path, log_path)

            self.assertEqual(len(model.measurements), 2)
            self.assertEqual(invalid_count, 1)
            self.assertTrue(log_path.exists())
            self.assertIn("Ошибка", log_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()