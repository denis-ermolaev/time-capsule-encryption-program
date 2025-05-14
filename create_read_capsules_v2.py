from email import message
import os
import datetime
from cryptography.fernet import Fernet
import argparse
import json
import logging


log_format = (
    "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(lineno)d::  %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=0, format=log_format)

# Тестовый запуск создания
# python create_read_capsules_v2.py 1 --create "gfbgfb" "2025-04-26 14:00:00" "2025-04-26 14:00:00"
# python create_read_capsules_v2.py 2 --create "gfbgfb" "2025-04-17 14:00:00" "2025-04-26 14:00:00" --emergency true '[[[0.1, 0.2], "hidden"], [[0.1, 0.2] , "open"]]'
# python create_read_capsules_v2.py 2 --create "gfbgfb" "2025-04-17 14:00:00" "2025-04-26 14:00:00" --emergency true '[[[0.1, 0.2], "hidden"], [[0.1, 0.2] , "open"]]' --opening_days_mode "m,t,w" 2 "12:00" "13:00"

# Тестовый запуск открытия
# python create_read_capsules_v2.py 1 --read
# python create_read_capsules_v2.py 2 --read

#! Возможные аргументы
# id

# * Либо --read либо --create. В случае с --create, доп аргументы:

# text Текст
# date_open Дата-Время после которых открытие (2025-04-17 14:00:00)
# date_change - Последний, с него считаются недели для opening_days_mode

# * Флаг --emergency
# ea_after_open(true false) ЭД доступен только после времени открытия(Т.е открытие просто так не работает)
# ea_time_separation - [ [ [1, 1], 'hidden'], [ [1, 5] , 'open'], [ [0.5,0.5], 'open'] ] - json
# Работает так, в начале первый запрос экстренного доступа, выбирается случайное число от 1 до 1 часа
# Причём время захода сказано не будет, т.е надо переодически заходить проверять
# Дальше от 1 до 5 часов, нужно подождать, время будет дано конкретное, если зайти в другое, то сброс и так далее


# * Флаг --opening_days_mode
# day_week_odm - m,t,w,th,f,sa,su - дни недели, когда капсулу можно открыть
# num_week_odm - раз в сколько недель. Если 0, то каждую неделю
# time_odm_start - С этого времени 12:00
# time_odm_end - До этого времени 13:00


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
    nargs=3,
    help="text, date_open, date_change",
)
parser.add_argument(
    "--emergency",
    nargs=2,
    help="ea_after_open(true,false) ea_time_separation",
)
parser.add_argument(
    "--opening_days_mode",
    nargs=4,
    help="day_week_odm, num_week_odm, time_odm_start, time_odm_end",
)
group_create.add_argument(
    "--read",
    action="store_true",
    help="Для чтения капсулы --read, для создания --create с 2-тью аргументами и --emergency --opening_days_mode",
)
parser.add_argument(
    "id",
    type=int,
    help="Не зависимо от чтения или создания, нужно id, это имя файла капсулы",
)
args = parser.parse_args()

logger.debug(("Были получены следующие аргументы", args, type(args)))


class СapsuleProcessor:
    capsule_folder = "capsules"
    fernet = Fernet(
        b"6Q22tkQ83AoK6ml7GDS-s4JqErokcX_QpEWys2k9BTQ="
    )  # TODO: нужно вставить ключ (Fernet.generate_key())

    def __init__(self, args: argparse.Namespace) -> None:
        # Namespace(create=['gfbgfb', '2025-04-17 14:00:00', 'True', '1', '3'], read=False, id=12)
        # Namespace(create=None, read=True, id=13)
        self.for_reading = args.read
        self.id = args.id
        if args.create:
            self.create_args = {
                "text": args.create[0],
                "open_time": args.create[1],
                "date_change": args.create[2],
            }
            if args.emergency:
                self.emergency = {
                    "emergency_access": "true",
                    "ea_after_open": args.emergency[0],
                    "ea_time_separation": json.loads(args.emergency[1]),
                }
            else:
                self.emergency = {"emergency_access": "false"}
            if args.opening_days_mode:
                self.opening_days_mode = {
                    "opening_days_mode": "true",
                    "day_week_odm": args.opening_days_mode[0],
                    "num_week_odm": args.opening_days_mode[1],
                    "time_odm_start": args.opening_days_mode[2],
                    "time_odm_end": args.opening_days_mode[3],
                }
            else:
                self.opening_days_mode = {"opening_days_mode": "false"}

        self.current_time = datetime.datetime.now().replace(microsecond=0)
        self.final_console_output = {}

        if not os.path.exists(self.capsule_folder):
            os.mkdir(self.capsule_folder)

        self.process_reading() if self.for_reading else self.process_creation()

    def process_creation(self) -> None:
        """Обработка записи капсулы"""
        logger.debug("Начало записи капсулы в файл")
        save_date_dict = self.create_args.copy()
        save_date_dict |= (
            self.opening_days_mode.copy()
            if self.opening_days_mode
            else {"opening_days_mode": "false"}
        )
        save_date_dict |= (
            self.emergency.copy() if self.emergency else {"emergency": "false"}
        )
        logger.debug(save_date_dict)
        self.write_capsule(save_date_dict=save_date_dict)
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
            logger.debug(("Начало чтения", capsule_date))

            DAYNAMES = [None, "m", "t", "w", "th", "f", "sa", "su"]  # m,t,w,th,f,sa,su
            weekday = DAYNAMES[
                self.current_time.toordinal() % 7 or 7
            ]  # Текущий день недели
            now_time = self.current_time.time()  # Время
            print(capsule_date["day_week_odm"], weekday)

            print(capsule_date["date_change"])
            date_change_weekday = DAYNAMES[
                capsule_date["date_change"].toordinal() % 7 or 7
            ]  # Текущий день недели
            print(date_change_weekday)
            week_index = capsule_date["date_change"].toordinal() % 7 or 7
            # 2025-05-14 среда, 3
            start_count_week = capsule_date["date_change"] - capsule_date[
                "date_change"
            ].replace(day=capsule_date["date_change"].day - (week_index - 1))
            print("start_count_week", start_count_week)
            start_point = capsule_date["date_change"].replace(
                day=capsule_date["date_change"].day - start_count_week.days
            )
            end_point = self.current_time.replace(
                day=self.current_time.day
                - (
                    self.current_time
                    - self.current_time.replace(
                        day=self.current_time.day
                        - ((self.current_time.toordinal() % 7 or 7) - 1)
                    )
                ).days
            )
            x = round(int((end_point - start_point).days) / 7)

            if (
                self.current_time > capsule_date["open_time"]
                and not capsule_date["opening_days_mode"]
                and not capsule_date["ea_after_open"]
            ):
                self.create_console_output(status="2", text=capsule_date["text"])
            elif (
                capsule_date["opening_days_mode"] == True
                and self.current_time > capsule_date["open_time"]
                and not capsule_date["ea_after_open"]
                and weekday in capsule_date["day_week_odm"]
                and now_time >= capsule_date["time_odm_start"]
                and now_time <= capsule_date["time_odm_end"]
            ):
                self.create_console_output(status="2", text=capsule_date["text"])
            elif (
                capsule_date["opening_days_mode"] == True
                and self.current_time > capsule_date["open_time"]
                and capsule_date["ea_after_open"]
                and weekday in capsule_date["day_week_odm"]
                and now_time >= capsule_date["time_odm_start"]
                and now_time <= capsule_date["time_odm_end"]
            ):
                capsule_date["opening_days_mode"] == "ea_turn_on"
                self.run_emergency_access(capsule_date)
            elif (
                capsule_date["emergency_access"]
                and (not capsule_date["ea_after_open"])
                or (
                    capsule_date["ea_after_open"]
                    and self.current_time > capsule_date["open_time"]
                )
            ):
                self.run_emergency_access(capsule_date)

            elif (
                capsule_date["emergency_access"]
                and capsule_date["ea_after_open"]
                and self.current_time < capsule_date["open_time"]
            ):
                self.create_console_output(
                    status="1",
                    message="Экстренный доступ откроется только после даты открытия капсулы",
                )
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
        dct["date_change"] = datetime.datetime.strptime(
            dct["date_change"], "%Y-%m-%d %H:%M:%S"
        )
        dct["opening_days_mode"] = True if dct["opening_days_mode"] == "true" else False
        if dct["opening_days_mode"]:
            dct["day_week_odm"] = dct["day_week_odm"].split(",")
            dct["num_week_odm"] = int(dct["num_week_odm"])
            dct["time_odm_start"] = datetime.datetime.strptime(
                dct["time_odm_start"], "%H:%M"
            ).time()
            dct["time_odm_end"] = datetime.datetime.strptime(
                dct["time_odm_end"], "%H:%M"
            ).time()
        dct["emergency_access"] = True if dct["emergency_access"] == "true" else False
        if dct["emergency_access"]:
            dct["ea_after_open"] = True if dct["ea_after_open"] == "true" else False
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
        dct["date_change"] = str(dct["date_change"])
        if dct["opening_days_mode"]:
            dct["day_week_odm"] = ",".join(dct["day_week_odm"])
            dct["num_week_odm"] = str(dct["num_week_odm"])
            dct["time_odm_start"] = str(dct["num_week_odm"])
            dct["time_odm_end"] = str(dct["time_odm_end"])
        dct["opening_days_mode"] = (
            "true" if dct["opening_days_mode"] == True else "false"
        )

        if dct["emergency_access"]:
            dct["ea_after_open"] = "true" if dct["ea_after_open"] == True else "false"
        dct["emergency_access"] = "true" if dct["emergency_access"] == True else "false"

        if dct.get("start_limit", False):
            dct["start_limit"] = str(dct["start_limit"])
            dct["end_limit"] = str(dct["end_limit"])
            dct["num_access"] = str(dct["num_access"])
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
