import os
import datetime
from cryptography.fernet import Fernet
import argparse
import json

# Тестовый запуск создания
# python create_read_capsules.py 12 --create "gfbgfb" "2025-04-26 14:00:00" True 1 3
# python create_read_capsules.py 13 --create "gfbgfb" "2025-05-17 14:00:00" True 2 2

# Тестовый запуск открытия
# python create_read_capsules.py 12 --read
# python create_read_capsules.py 13 --read

# Работа с argparse, парсингом аргументов запуска программы
# type=int, choices=[0, 1, 2], action="store_true"
parser = argparse.ArgumentParser(
    description="Создание/Чтение капсул времени, можно использовать либо --read, либо --create",
    usage="""
                                 Позволяет создать или открыть зашифрованную капсулу времени
                                 Доступ к капсуле можно получить, после даты-времени открытия, если доступ
                                 запрашивается раньше, тогда проверяется экстренный доступ, если он False, тогда доступ к капсуле
                                 раньше времени получить нельзя, если True, то действует следующая система:
                                 1. После запроса экстренного доступа, нужно запустить программу с запросом чтения капсулы ещё раз в определённые часы
                                 2. Если следующий запрос произведён в неверные часы, то процесс экстренного доступа сбрасывается
                                 3. Если в верные, то назначается новое время следующего запроса экстренного доступа
                                 4. В итоге доступ к капсуле будет получен, когда кол-во запросов будет равно число разрывов при создании капсулы
                                 
                                 Пример:
                                 create_read_capsules.py 12 --create "gfbgfb" "2025-04-17 14:00:00" True 1 3
                                 create_read_capsules.py 13 --read
                                 """,
)
group_create = parser.add_mutually_exclusive_group()
group_create.add_argument(
    "--create",
    nargs=5,
    help="5 аргументов: Текст, Дата-Время после которых открытие (2025-04-17 14:00:00), Экстренный доступ(True/False), Кол-во часов(number), Разрывы(number)",
)
group_create.add_argument(
    "--read",
    action="store_true",
    help="Для чтения капсулы --read, для создания --create с 5-тью аргументами",
)
parser.add_argument(
    "id",
    type=int,
    help="Не зависимо от чтения или создания, нужно id, это имя файла капсулы",
)
args = parser.parse_args()


class СapsuleProcessor:
    capsule_folder = "capsules"
    fernet = Fernet(b"")  # TODO: нужно вставить ключ (Fernet.generate_key())

    def __init__(self, args: argparse.Namespace) -> None:
        # Namespace(create=['gfbgfb', '2025-04-17 14:00:00', 'True', '1', '3'], read=False, id=12)
        # Namespace(create=None, read=True, id=13)
        self.for_reading = args.read
        self.id = args.id
        if args.create:
            self.create_args = {
                "text": args.create[0],
                "open_time": args.create[1],
                "emergency_access": args.create[2],
                "time_for_ea": args.create[3],
                "time_break": args.create[4],
            }
        self.current_time = datetime.datetime.now().replace(microsecond=0)
        self.final_console_output = {}

        if not os.path.exists(self.capsule_folder):
            os.mkdir(self.capsule_folder)

        (
            self.process_reading() if self.for_reading else self.process_creation()
        )  # Запуск обработки

    def process_creation(self) -> None:
        """Обработка записи капсулы"""
        self.write_capsule(self.create_args)
        self.create_console_output(status="1")

    def process_reading(self) -> None:
        """Обработка чтения капсулы, в случае экстренного доступа запуск ф-и run_emergency_access"""
        with open(f"{self.capsule_folder}/{str(self.id)}", "rb") as file:
            decrypted_data = self.fernet.decrypt(file.read()).decode()
            # {'text': 'gfbgfb', 'open_time': '2025-04-17 14:00:00', 'emergency_access': True, 'time_for_ea': 1, 'time_break': 3}
            # {'text': 'gfbgfb', 'open_time': '2025-04-26 14:00:00', 'emergency_access': True, 'time_for_ea': 1, 'time_break': 3, 'start_limit': '2025-04-25 23:00:00', 'end_limit': '2025-04-25 23:14:00', 'num_access': 0}
            json_loads = json.loads(decrypted_data)
            capsule_date = self.format_dictionary(
                json_loads
            )  # loads - из строки, load из файла, аналогично dumps и dump
            if self.current_time > capsule_date["open_time"]:
                self.create_console_output(status="2", text=capsule_date["text"])
            elif capsule_date["emergency_access"]:
                self.run_emergency_access(capsule_date)
            else:
                self.create_console_output(status="1")

    def run_emergency_access(self, capsule_date: dict) -> None:
        """Обработка экстренного доступа"""

        def set_start_and_end_time(
            first_time: datetime.datetime, second_time: datetime.datetime = None
        ) -> None:
            if second_time is None:
                second_time = first_time
            UPDATE_START_AND_END_TIME = (
                capsule_date["time_for_ea"] / capsule_date["time_break"]
            )
            capsule_date["start_limit"] = first_time + datetime.timedelta(
                hours=UPDATE_START_AND_END_TIME
            )
            capsule_date["end_limit"] = second_time + datetime.timedelta(
                hours=UPDATE_START_AND_END_TIME, minutes=15
            )

        if capsule_date.get("start_limit", False):
            if (
                self.current_time > capsule_date["start_limit"]
                and self.current_time < capsule_date["end_limit"]
            ):  # Правильное Время
                capsule_date["num_access"] += 1
                if (
                    capsule_date["num_access"] == capsule_date["time_break"]
                ):  # Капсула открыта т.к собралось нужное кол-во запросов
                    self.create_console_output(status="2", text=capsule_date["text"])
                    del (
                        capsule_date["num_access"],
                        capsule_date["start_limit"],
                        capsule_date["end_limit"],
                    )
                else:  # Нужны ещё попытки захода, назначены новые времена захода
                    set_start_and_end_time(
                        capsule_date["start_limit"], capsule_date["end_limit"]
                    )
                    self.create_console_output(status="3")
                    self.create_console_output(
                        num_access=capsule_date["num_access"],
                        start_limit=capsule_date["start_limit"],
                        end_limit=capsule_date["end_limit"],
                    )
            else:  # Правильное время пропущено, Новые дата начала и дата конца
                set_start_and_end_time(self.current_time)
                capsule_date["num_access"] = 0
                self.create_console_output(status="4")
                self.create_console_output(
                    num_access=capsule_date["num_access"],
                    start_limit=capsule_date["start_limit"],
                    end_limit=capsule_date["end_limit"],
                )
        else:  # Назначены первоначальные времена захода
            set_start_and_end_time(self.current_time)
            capsule_date["num_access"] = 0
            self.create_console_output(status="5")
            self.create_console_output(
                num_access=capsule_date["num_access"],
                start_limit=capsule_date["start_limit"],
                end_limit=capsule_date["end_limit"],
            )
        capsule_date = self.deformat_dictionary(capsule_date)
        self.write_capsule(capsule_date)

    def create_console_output(self, **kwargs) -> None:
        self.final_console_output |= kwargs

    def format_dictionary(self, dct: dict) -> None:
        dct = dct.copy()
        dct["open_time"] = datetime.datetime.strptime(
            dct["open_time"], "%Y-%m-%d %H:%M:%S"
        )
        dct["emergency_access"] = True if dct["emergency_access"] == "True" else False
        dct["time_for_ea"] = int(dct["time_for_ea"])
        dct["time_break"] = int(dct["time_break"])
        if dct.get("start_limit", False):
            dct["start_limit"] = datetime.datetime.strptime(
                dct["start_limit"], "%Y-%m-%d %H:%M:%S"
            )
            dct["end_limit"] = datetime.datetime.strptime(
                dct["end_limit"], "%Y-%m-%d %H:%M:%S"
            )
            dct["num_access"] = int(dct["num_access"])
        return dct

    def deformat_dictionary(self, dct: dict) -> None:
        dct = dct.copy()
        dct["open_time"] = str(dct["open_time"])
        dct["emergency_access"] = "True" if dct["emergency_access"] == True else "False"
        if dct.get("start_limit", False):
            dct["start_limit"] = str(dct["start_limit"])
            dct["end_limit"] = str(dct["end_limit"])
        return dct

    def write_capsule(self, save_date_dict: dict) -> None:
        with open(f"{self.capsule_folder}/{str(self.id)}", "wb") as file:
            json_str = json.dumps(save_date_dict)
            encrypted_message = self.fernet.encrypt(json_str.encode())
            file.write(encrypted_message)

    def show_final_console_output(self) -> None:
        """
        Первая строка, статус
        1 - Доступ запрещён, капсула не открыта ИЛИ успешное создание капсулы
        2 - Текст получен, по времени или экстренному доступу
        3 - Экстренный доступ, + 1 попытка
        4 - время захода не правильное
        5 - экстренный доступ запрошен, время назначено
        """
        if self.final_console_output["status"] == "1":
            print("1")
        elif self.final_console_output["status"] == "2":
            print("2")
            print(self.final_console_output["text"])
        elif self.final_console_output["status"] == "3":
            print("3")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])
        elif self.final_console_output["status"] == "4":
            print("4")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])
        elif self.final_console_output["status"] == "5":
            print("5")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])


capsule_processor = СapsuleProcessor(args)
capsule_processor.show_final_console_output()
