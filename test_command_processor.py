from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from command_processor import CommandError, CommandProcessor
from pressure_model import PressureModel


class TestCommandProcessor(unittest.TestCase):
    def test_add_command(self) -> None:
        model = PressureModel()
        processor = CommandProcessor(model, Path("."))

        processor.execute_line("ADD Давление;2024.06.01;130.5;765")

        self.assertEqual(len(model.measurements), 1)
        self.assertEqual(model.measurements[0].height, 130.5)
        self.assertEqual(model.measurements[0].value, 765)

    def test_add_command_without_object_type(self) -> None:
        model = PressureModel()
        processor = CommandProcessor(model, Path("."))

        processor.execute_line("ADD 2024.06.01;130.5;765")

        self.assertEqual(len(model.measurements), 1)
        self.assertEqual(model.measurements[0].height, 130.5)

    def test_remove_by_value_condition(self) -> None:
        model = PressureModel()
        model.add_measurement("2024.03.28", "120.5", "760")
        model.add_measurement("2024.04.10", "135.2", "740")

        processor = CommandProcessor(model, Path("."))
        processor.execute_line("REM value < 750")

        self.assertEqual(len(model.measurements), 1)
        self.assertEqual(model.measurements[0].value, 760)

    def test_remove_by_height_condition(self) -> None:
        model = PressureModel()
        model.add_measurement("2024.03.28", "120.5", "760")
        model.add_measurement("2024.04.10", "250.0", "730")

        processor = CommandProcessor(model, Path("."))
        processor.execute_line("REM height > 200")

        self.assertEqual(len(model.measurements), 1)
        self.assertEqual(model.measurements[0].height, 120.5)

    def test_remove_by_date_condition(self) -> None:
        model = PressureModel()
        model.add_measurement("2024.03.28", "120.5", "760")
        model.add_measurement("2024.05.01", "210.0", "745")

        processor = CommandProcessor(model, Path("."))
        processor.execute_line("REM date < 2024.04.01")

        self.assertEqual(len(model.measurements), 1)
        self.assertEqual(model.measurements[0].measurement_date.year, 2024)
        self.assertEqual(model.measurements[0].measurement_date.month, 5)

    def test_save_command(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            model = PressureModel()
            model.add_measurement("2024.03.28", "120.5", "760")

            processor = CommandProcessor(model, base_dir)
            processor.execute_line("SAVE result.txt")

            result_path = base_dir / "result.txt"
            self.assertTrue(result_path.exists())
            self.assertIn("Давление", result_path.read_text(encoding="utf-8"))

    def test_execute_file(self) -> None:
        with TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            command_path = base_dir / "commands.txt"

            command_path.write_text(
                "ADD Давление;2024.06.01;130.5;765\n"
                "ADD Давление;2024.06.05;250.0;730\n"
                "REM value < 750\n"
                "SAVE result.txt\n",
                encoding="utf-8",
            )

            model = PressureModel()
            processor = CommandProcessor(model, base_dir)
            messages = processor.execute_file(command_path)

            self.assertEqual(len(model.measurements), 1)
            self.assertEqual(model.measurements[0].value, 765)
            self.assertTrue((base_dir / "result.txt").exists())
            self.assertEqual(len(messages), 4)

    def test_unknown_command(self) -> None:
        model = PressureModel()
        processor = CommandProcessor(model, Path("."))

        with self.assertRaises(CommandError):
            processor.execute_line("EDIT something")


if __name__ == "__main__":
    unittest.main()