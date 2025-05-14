import datetime
import json
from math import ceil
from time import sleep
from src.CapsuleProcessor import СapsuleProcessor
import unittest
from unittest.mock import Mock
import random
import tqdm

# "BaseReadCreateAndOnlyEA"
# "opening_days_mode"
test_opening_days_mode = True
baseReadCreateAndOnlyEA = True
test_opening_days_mode_and_ea = True
num_iterations = 30000


@unittest.skipIf(not test_opening_days_mode, "Тест пропуcкаем")
class Test_opening_days_mode_and_ea(unittest.TestCase):
    def test_12_create_close_days_mode_and_ea(self):
        """В определённые дни opening_days_mode, если включен ea_after_open,
        это означает, что только в определённые дни можно запросить экстренный доступ"""
        attrs = {
            "id": 7,
            "read": False,
            "create": [
                "gfbgfb",
                "2050-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": [
                "true",
                json.dumps([[[0.001, 0.001], "hidden"], [[0.001, 0.001], "open"]]),
            ],
            "opening_days_mode": ["m,t,w,th,f,sa,su", 0, "00:01", "23:59"],
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_13_open_close_days_mode_and_ea(self):
        attrs = {
            "id": 7,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "8")

    def test_14_create_days_mode_and_ea(self):
        """В определённые дни opening_days_mode, если включен ea_after_open,
        это означает, что только в определённые дни можно запросить экстренный доступ"""
        attrs = {
            "id": 8,
            "read": False,
            "create": [
                "gfbgfb",
                "2010-04-26 14:00:00",
                "2025-04-26 14:00:00",
            ],
            "emergency": [
                "true",
                json.dumps([[[0.001, 0.001], "hidden"], [[0.001, 0.001], "open"]]),
            ],
            "opening_days_mode": ["m,t,w,th,f,sa,su", 0, "00:01", "23:59"],
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "1")

    def test_15_open_days_mode_and_ea(self):
        attrs = {
            "id": 8,
            "read": True,
            "create": None,
            "emergency": None,
            "opening_days_mode": None,
        }
        args = Mock(**attrs)

        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)

        # Заход в скрытое время, но он не сбрасывает время
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "6")
        # После 3.6 получаем уже открытое время
        sleep(4)
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "3")
        self.assertTrue(capsule_processor.final_console_output["start_limit"])
        self.assertTrue(capsule_processor.final_console_output["end_limit"])

        # Заходим в неправильное время и всё сбрасывается
        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "6")

        # Начинаем заново Т.к hidden время нам уже назначено, то ждём 4 сек
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


@unittest.skipIf(not test_opening_days_mode, "Тест пропуcкаем")
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

    def test_11_opening_days_mode_capsule(self):
        """Комплексный тест режима opening_days_mode"""
        for i in tqdm.tqdm(range(num_iterations)):
            current_datetime = datetime.datetime.now()
            num_week_odm = random.randint(0, 100)
            day_week_odm = ",".join(
                [i for i in "m,t,w,th,f,sa,su".split(",") if random.randint(0, 1)]
            )
            date_change = datetime.datetime(
                year=current_datetime.year - 1,
                month=random.randint(1, 12),
                day=random.randint(1, 25),
                hour=random.randint(0, 23),  # Как легко сформировать случайную дату?
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0,
            )
            time_odm_start = datetime.time(
                hour=random.randint(0, 21), minute=random.randint(0, 59)
            )
            time_odm_end = time_odm_start.replace(hour=time_odm_start.hour + 1)
            attrs = {
                "id": 6,
                "read": False,
                "create": [
                    "gfbgfb",
                    "2010-04-26 14:05:05",
                    str(date_change),
                ],
                "emergency": None,
                "opening_days_mode": [
                    day_week_odm,
                    num_week_odm,
                    str(time_odm_start)[:-3],
                    str(time_odm_end)[:-3],
                ],
            }
            args = Mock(**attrs)

            capsule_processor = СapsuleProcessor(args)
            self.assertEqual(capsule_processor.final_console_output["status"], "1")

            attrs = {
                "id": 6,
                "read": True,
                "create": None,
                "emergency": None,
                "opening_days_mode": None,
            }
            args = Mock(**attrs)

            capsule_processor = СapsuleProcessor(args)

            DAYNAMES = [
                None,
                "m",
                "t",
                "w",
                "th",
                "f",
                "sa",
                "su",
            ]  # m,t,w,th,f,sa,su
            weekday = DAYNAMES[
                current_datetime.toordinal() % 7 or 7
            ]  # Текущий день недели
            now_time = current_datetime.time().replace(second=0, microsecond=0)  # Время

            start_point = date_change - datetime.timedelta(
                days=(date_change.toordinal() % 7 or 7) - 1
            )
            end_point = current_datetime - datetime.timedelta(
                days=(current_datetime.toordinal() % 7 or 7) - 1
            )

            is_correct_week = (
                (ceil(int((end_point - start_point).days) / 7) + 1) % (num_week_odm + 1)
            ) == 0  # Неделя для открытия по opening_days_mode

            if (
                weekday in day_week_odm
                and is_correct_week
                and now_time >= time_odm_start
                and now_time <= time_odm_end
            ):
                self.assertEqual(
                    capsule_processor.final_console_output["status"],
                    "2",
                    msg={
                        "attrs": attrs,
                        "now_time": now_time,
                        "time_odm_start": time_odm_start,
                        "time_odm_end": time_odm_end,
                        "is_correct_week": is_correct_week,
                        "weekday": weekday,
                        "num_week_odm": num_week_odm,
                        "day_week_odm": day_week_odm,
                        "date_change": date_change,
                        "capsule_processor.final_console_output": capsule_processor.final_console_output,
                    },
                )
                self.assertTrue(capsule_processor.final_console_output["text"])
                print(
                    "capsule_processor.final_console_output",
                    capsule_processor.final_console_output,
                )
            else:
                self.assertEqual(
                    capsule_processor.final_console_output["status"],
                    "1",
                    msg={
                        "attrs": attrs,
                        "now_time": now_time,
                        "time_odm_start": time_odm_start,
                        "time_odm_end": time_odm_end,
                        "is_correct_week": is_correct_week,
                        "weekday": weekday,
                        "num_week_odm": num_week_odm,
                        "day_week_odm": day_week_odm,
                        "date_change": date_change,
                        "capsule_processor.final_console_output": capsule_processor.final_console_output,
                    },
                )


@unittest.skipIf(not baseReadCreateAndOnlyEA, "Тест пропуcкаем")
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
        self.assertEqual(capsule_processor.final_console_output["status"], "6")
        # Заход в скрытое время, но он не сбрасывает время
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "6")
        # После 3.6 получаем уже открытое время
        sleep(4)
        capsule_processor = СapsuleProcessor(args)
        self.assertEqual(capsule_processor.final_console_output["status"], "3")
        self.assertTrue(capsule_processor.final_console_output["start_limit"])
        self.assertTrue(capsule_processor.final_console_output["end_limit"])

        # Заходим в неправильное время и всё сбрасывается
        capsule_processor = СapsuleProcessor(args)
        print(capsule_processor.final_console_output)
        self.assertEqual(capsule_processor.final_console_output["status"], "6")

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
