import datetime
import json
from time import sleep
from СapsuleProcessor import СapsuleProcessor
import unittest
from unittest.mock import Mock
import random

# "Базовое создание, чтение. Только экстренный доступ"
# "opening_days_mode"
MODE = "opening_days_mode"


@unittest.skipIf(MODE != "opening_days_mode", "Тест пропуcкаем")
class Test_opening_days_mode(unittest.TestCase):
    def test_07_create_opening_days_mode_capsule(self):
        """Открытие капсулы, которая открывается практически всегда по opening_days_mode"""
        attrs = {
            "id": 4,
            "read": False,
            "create": [
                "gfbgfb",
                "2025-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": None,
            "opening_days_mode": ["m,t,w,th,f,sa,su", 0, "00:01", "23:59"],
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_08_read_opening_days_mode_capsule(self):
        attrs = {
            "id": 4,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "2")
        self.assertTrue(capsule_processor.final_console_output["text"])

    def test_09_create_opening_days_mode_capsule(self):
        """В случае, если дата открытия не наступила, режим opening_days_mode не срабатывает и капсулу нельзя открыть"""
        attrs = {
            "id": 5,
            "read": False,
            "create": [
                "gfbgfb",
                "2050-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": None,
            "opening_days_mode": ["m,t,w,th,f,sa,su", 0, "00:01", "23:59"],
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_10_read_opening_days_mode_capsule(self):
        attrs = {
            "id": 5,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_11_create_opening_days_mode_capsule(self):
        """Тест недели"""
        num_week_odm = 1
        current_datetime = datetime.datetime.now()
        for i in range(2):
            date_change = (
                current_datetime - datetime.timedelta(days=7 * i + 7 * num_week_odm)
            ).replace(microsecond=0)
            print("date_change", date_change.replace(microsecond=0))
            attrs = {
                "id": 5,
                "read": False,
                "create": [
                    "gfbgfb",
                    "2010-04-26 14:00:00",
                    str(date_change),
                ],
                "emergency": None,
                "opening_days_mode": [
                    "m,t,w,th,f,sa,su",
                    num_week_odm,
                    "00:01",
                    "23:59",
                ],
            }
            args = Mock(**attrs)

            capsule_processor = СapsuleProcessor(args)
            self.assertEqual(capsule_processor.final_console_output["status"], "1")

            attrs = {
                "id": 5,
                "read": True,
                "create": None,
                "emergency": None,
                "opening_days_mode": None,
            }
            args = Mock(**attrs)

            capsule_processor = СapsuleProcessor(args)
            print(capsule_processor.final_console_output)
            if i == 0:
                self.assertEqual(capsule_processor.final_console_output["status"], "2")
                self.assertTrue(
                    capsule_processor.final_console_output["text"], "gfbgfb"
                )

            else:
                self.assertEqual(capsule_processor.final_console_output["status"], "1")


@unittest.skipIf(
    MODE != "Базовое создание, чтение. Только экстренный доступ", "Тест пропуcкаем"
)
class BaseReadCreateAndOnlyEA(unittest.TestCase):
    def test_01_create_open_capsule(self):
        attrs = {
            "id": 1,
            "read": False,
            "create": [
                "gfbgfb",
                "2025-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_02_read_open_capsule(self):
        attrs = {
            "id": 1,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "2")

    def test_03_create_close_capsule(self):
        attrs = {
            "id": 2,
            "read": False,
            "create": [
                "gfbgfb",
                "2050-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_04_read_close_capsule(self):
        attrs = {
            "id": 2,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_05_create_ea_capsule(self):
        attrs = {
            "id": 3,
            "read": False,
            "create": [
                "gfbgfb",
                "2050-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": [
                "false",
                json.dumps([[[0.001, 0.001], "hidden"], [[0.001, 0.001], "open"]]),
            ],
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_06_read_ea_capsule(self):
        attrs = {
            "id": 3,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)
        # Назначено скрытое время
        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "5")
        self.assertEqual(
            capsule_processor.final_console_output["message"],
            "Время скрыто и не показывается",
        )
        # Заход в скрытое время, но он не сбрасывает время
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "4")
        self.assertEqual(
            capsule_processor.final_console_output["message"],
            "Время захода не верное, но время не сбрасывается, т.к оно hidden",
        )
        # После 3.6 получаем уже открытое время
        sleep(4)
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "3")
        self.assertTrue(capsule_processor.final_console_output["start_limit"])
        self.assertTrue(capsule_processor.final_console_output["end_limit"])

        # Заходим в неправильное время и всё сбрасывается
        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "4")
        self.assertEqual(
            capsule_processor.final_console_output["message"],
            "Время захода не верное, но время не сбрасывается, т.к оно hidden",
        )

        # Начинаем занова Т.к hidden время нам уже назначено, то ждём 4 сек
        # После 3.6 получаем уже открытое время
        sleep(4)
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "3")
        self.assertTrue(capsule_processor.final_console_output["start_limit"])
        self.assertTrue(capsule_processor.final_console_output["end_limit"])

        sleep(4)
        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "2")
        self.assertTrue(capsule_processor.final_console_output["text"])


if __name__ == "__main__":
    unittest.main()
