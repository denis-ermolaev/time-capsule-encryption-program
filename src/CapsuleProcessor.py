import os
import datetime
from typing import (
    Any,
    Literal,
    NotRequired,
    Protocol,
    TypedDict,
    Unpack,
)
from cryptography.fernet import Fernet
import json
import logging
from math import ceil
import random

log_format = (
    "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(lineno)d::  %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=0, format=log_format)


class ArgsProto(Protocol):
    def __init__(self):
        self.id: int
        self.read: bool
        self.create: list[str] | None
        self.emergency: list[str] | None
        self.opening_days_mode: list[str | int] | None
        super().__init__()


class UnformatData(TypedDict):
    text: str
    open_time: str
    date_change: str
    emergency_access: str
    ea_after_open: NotRequired[str]
    ea_time_separation: NotRequired[
        list[list[list[float] | Literal["open"] | Literal["hidden"]]]
    ]
    opening_days_mode: str | Literal["ea_turn_on"]
    day_week_odm: NotRequired[str]
    num_week_odm: NotRequired[str]
    time_odm_start: NotRequired[str]
    time_odm_end: NotRequired[str]

    num_access: NotRequired[str]
    start_limit: NotRequired[str]
    end_limit: NotRequired[str]


class FormatData(TypedDict):
    text: str
    open_time: datetime.datetime
    date_change: datetime.datetime
    emergency_access: bool
    ea_after_open: NotRequired[bool]
    ea_time_separation: NotRequired[
        list[list[list[float] | Literal["open"] | Literal["hidden"]]]
    ]
    opening_days_mode: bool | Literal["ea_turn_on"]
    day_week_odm: NotRequired[list[str]]
    num_week_odm: NotRequired[int]
    time_odm_start: NotRequired[datetime.time]
    time_odm_end: NotRequired[datetime.time]

    num_access: NotRequired[int]
    start_limit: NotRequired[datetime.datetime]
    end_limit: NotRequired[datetime.datetime]


class FunalOutputType(TypedDict):
    status: str
    text: NotRequired[str]
    num_access: NotRequired[int]
    start_limit: NotRequired[str]
    end_limit: NotRequired[str]


type day_week_tuple_type = tuple[
    None,
    Literal["m"],
    Literal["t"],
    Literal["w"],
    Literal["th"],
    Literal["f"],
    Literal["sa"],
    Literal["su"],
]

type day_week_type = None | Literal["m"] | Literal["t"] | Literal["w"] | Literal[
    "th"
] | Literal["f"] | Literal["sa"] | Literal["su"]


class СapsuleProcessor:
    capsule_folder = "capsules"
    fernet = Fernet(
        b"2eVh78Xw4idGoMzrZcKVdesQzwKH3HVMIVfVVBqd2ME="
    )  # TODO: нужно вставить ключ (Fernet.generate_key())

    def __init__(self, args: ArgsProto) -> None:
        # Namespace(create=['gfbgfb', '2025-04-17 14:00:00', 'True', '1', '3'], read=False, id=12)
        # Namespace(create=None, read=True, id=13)
        if args.create:
            self.create_capsule: UnformatData = {
                "text": args.create[0],
                "open_time": args.create[1],
                "date_change": args.create[2],
                "emergency_access": "true" if args.emergency else "false",
                "opening_days_mode": "true" if args.opening_days_mode else "false",
            }
            if args.emergency:
                self.create_capsule["ea_after_open"] = args.emergency[0]
                self.create_capsule["ea_time_separation"] = json.loads(
                    args.emergency[1]
                )
            if args.opening_days_mode:
                self.create_capsule["day_week_odm"] = str(args.opening_days_mode[0])
                self.create_capsule["num_week_odm"] = str(args.opening_days_mode[1])
                self.create_capsule["time_odm_start"] = str(args.opening_days_mode[2])
                self.create_capsule["time_odm_end"] = str(args.opening_days_mode[3])
        self.for_reading = args.read
        self.id = args.id

        self.current_time = datetime.datetime.now().replace(microsecond=0)
        self.final_console_output: dict[str, Any] = {}

        if not os.path.exists(self.capsule_folder):
            os.mkdir(self.capsule_folder)

        self.process_reading() if self.for_reading else self.process_creation()

    def process_creation(self) -> None:
        """Обработка записи капсулы"""
        logger.debug("Начало записи капсулы в файл")
        self.write_capsule(self.create_capsule)
        self.create_console_output(status="1")

    def process_reading(self) -> None:
        """Обработка чтения капсулы, в случае экстренного доступа запуск ф-и run_emergency_access"""
        with open(f"{self.capsule_folder}/{str(self.id)}", "rb") as file:

            decrypted_data = self.fernet.decrypt(file.read()).decode()
            json_loads: UnformatData = json.loads(decrypted_data)
            capsule_date = self.format_dictionary(
                json_loads
            )  # loads - из строки, load из файла, аналогично dumps и dump
            logger.debug(("Начало чтения", capsule_date))

            if (
                self.current_time > capsule_date["open_time"]
                and capsule_date["opening_days_mode"] == False
                and capsule_date["emergency_access"] == False
            ):
                logger.debug("Капсула открылась по времени, других режимов нет")
                self.create_console_output(status="2", text=capsule_date["text"])
            elif (
                capsule_date["opening_days_mode"] == False
                and capsule_date["emergency_access"] == True
                and (
                    self.current_time > capsule_date["open_time"]
                    or (
                        "ea_after_open" in capsule_date
                        and capsule_date["ea_after_open"] == False
                    )
                )
            ):
                logger.debug("Запущен экстренных доступ, режима odm нет")
                self.run_emergency_access(capsule_date)
            elif (
                self.current_time > capsule_date["open_time"]
                and capsule_date["opening_days_mode"] == True
                and capsule_date["emergency_access"] == False
            ):
                logger.debug("Запущен режим получения доступа в определённые дни(odm)")
                self.run_opening_days_mode(capsule_date)

            elif (
                capsule_date["opening_days_mode"] == True
                and capsule_date["emergency_access"] == True
            ):
                logger.debug("Есть оба режима, запущен их обработчик")
                self.run_opening_days_mode_emergency_access(capsule_date)

            else:
                logger.debug("Капсула открыть нельзя")
                self.create_console_output(status="1")

    def run_opening_days_mode_emergency_access(self, capsule_date: FormatData) -> None:
        if capsule_date["opening_days_mode"] == "ea_turn_on":
            logger.debug(
                "Подтверждение экстренного доступа (Т.к opening_days_mode == ea_turn_on)"
            )
            self.run_emergency_access(capsule_date)
        elif "ea_after_open" in capsule_date and capsule_date["ea_after_open"] == False:
            logger.debug(
                "Если текст не будет получен по odm, он будет получен по экстренному доступу(Нет флага ea_after_open)"
            )
            self.run_opening_days_mode(capsule_date)
            if self.final_console_output.get("status") != "2":
                self.run_emergency_access(capsule_date)
        else:
            logger.debug("Запустится odm, а после него экстренный доступ")
            self.run_opening_days_mode(capsule_date)
            if (
                self.current_time > capsule_date["open_time"]
                and self.final_console_output.get("status") == "2"
            ):
                del self.final_console_output["text"]
                capsule_date["opening_days_mode"] = "ea_turn_on"
                self.run_emergency_access(capsule_date)

    def run_opening_days_mode(self, capsule_date: FormatData) -> None:
        if capsule_date["opening_days_mode"] != True:
            raise AssertionError(
                "Для вызова метода run_opening_days_mode, opening_days_mode должен быть True"
            )
        if (
            "opening_days_mode" in capsule_date
            and "day_week_odm" in capsule_date
            and "num_week_odm" in capsule_date
            and "time_odm_start" in capsule_date
            and "time_odm_end" in capsule_date
        ):
            now_time = self.current_time.time().replace(
                second=0, microsecond=0
            )  # Время
            DAYNAMES: day_week_tuple_type = (
                None,
                "m",
                "t",
                "w",
                "th",
                "f",
                "sa",
                "su",
            )  # m,t,w,th,f,sa,su
            weekday = DAYNAMES[
                self.current_time.toordinal() % 7 or 7
            ]  # Текущий день недели

            start_point = capsule_date["date_change"] - datetime.timedelta(
                days=(capsule_date["date_change"].toordinal() % 7 or 7) - 1
            )
            end_point = self.current_time - datetime.timedelta(
                days=(self.current_time.toordinal() % 7 or 7) - 1
            )
            is_correct_week = (
                (ceil(int((end_point - start_point).days) / 7) + 1)
                % (capsule_date["num_week_odm"] + 1)
            ) == 0  # Неделя для открытия по opening_days_mode
            if (
                self.current_time > capsule_date["open_time"]
                and capsule_date["opening_days_mode"] == True
                and weekday in capsule_date["day_week_odm"]
                and is_correct_week
                and now_time >= capsule_date["time_odm_start"]
                and now_time <= capsule_date["time_odm_end"]
            ):
                logger.debug("Текст получен входе проверки odm")
                self.create_console_output(status="2", text=capsule_date["text"])
            else:
                logger.debug(
                    "Текст не получен после odm, время или день или неделя не те"
                )
                self.create_console_output(status="1")
        else:
            raise AssertionError(
                (
                    "Ключи opening_days_mode, day_week_odm"
                    "num_week_odm,time_odm_start, time_odm_end должны быть определены",
                    capsule_date,
                )
            )

    def run_emergency_access(self, capsule_date: FormatData) -> None:
        """Обработка экстренного доступа"""

        def set_start_and_end_time(
            first_time: datetime.datetime, second_time: datetime.datetime | None = None
        ) -> None:
            if second_time is None:
                second_time = first_time
            if "ea_time_separation" in capsule_date and len(
                capsule_date["ea_time_separation"]
            ) > capsule_date.get("num_access", 0):
                settings_num_access = capsule_date["ea_time_separation"][
                    capsule_date.get("num_access", 0)
                ]
                if isinstance(settings_num_access[0][0], int | float) and isinstance(
                    settings_num_access[0][1], int | float
                ):
                    hours = random.uniform(
                        settings_num_access[0][0],
                        settings_num_access[0][1],
                    )
                    capsule_date["start_limit"] = (
                        first_time + datetime.timedelta(hours=hours)
                    ).replace(microsecond=0)
                    capsule_date["end_limit"] = (
                        second_time + datetime.timedelta(hours=hours, minutes=10)
                    ).replace(microsecond=0)
            else:
                raise AssertionError(
                    "Ошибка в структуре ea_time_separation", capsule_date
                )

        if (
            "num_access" in capsule_date
            and "start_limit" in capsule_date
            and "end_limit" in capsule_date
        ):
            logger.debug(
                "Уже второе подтверждение экстренного доступа, уже есть назначенное время"
            )
            if (
                self.current_time > capsule_date["start_limit"]
                and self.current_time < capsule_date["end_limit"]
            ):  # Правильное Время
                capsule_date["num_access"] += 1
                if capsule_date["num_access"] == len(
                    capsule_date.get("ea_time_separation", [])
                ):  # Капсула открыта т.к собралось нужное кол-во запросов
                    logger.debug(
                        "Число подтверждений собрано, доступ к тексту открыт по ЭД"
                    )
                    self.create_console_output(status="2", text=capsule_date["text"])
                    if capsule_date.get("opening_days_mode") == "ea_turn_on":
                        capsule_date["opening_days_mode"] = True
                    del (
                        capsule_date["num_access"],
                        capsule_date["start_limit"],
                        capsule_date["end_limit"],
                    )
                else:  # Нужны ещё попытки захода, назначены новые времена захода
                    logger.debug("Нужно ещё собрать подтверждений экстренного доступа")
                    set_start_and_end_time(
                        capsule_date["start_limit"], capsule_date["end_limit"]
                    )
                    if (
                        "ea_time_separation" in capsule_date
                        and capsule_date["ea_time_separation"][
                            capsule_date.get("num_access", 0)
                        ][1]
                        == "hidden"
                    ):
                        logger.debug(
                            "Т.к время скрыто, не показываем его для нового цикла подтверждения ЭД"
                        )
                        self.create_console_output(
                            status="4", num_access=capsule_date["num_access"]
                        )
                    else:
                        logger.debug(
                            "Показываем время для нового цикла подтверждения ЭД"
                        )
                        self.create_console_output(
                            status="3",
                            num_access=capsule_date["num_access"],
                            start_limit=str(capsule_date["start_limit"]),
                            end_limit=str(capsule_date["end_limit"]),
                        )
            elif (
                "ea_time_separation" in capsule_date
                and capsule_date["ea_time_separation"][
                    capsule_date.get("num_access", 0)
                ][1]
                == "hidden"
            ):
                logger.debug(
                    "Время захода не правильное, но так как оно скрытое, это не сбрасывает его на новые, а оставляет предыдущие, нужно просто зайти позже"
                )
                self.create_console_output(
                    status="9", num_access=capsule_date["num_access"]
                )
            else:  # Правильное время пропущено, Новые дата начала и дата конца
                # Не может случится для скрытого времени т.к оно не сбрасываемое
                logger.debug("Время подтверждения не верное, назначается новое время")
                set_start_and_end_time(self.current_time)
                capsule_date["num_access"] = 0
                if capsule_date.get("opening_days_mode") == "ea_turn_on":
                    # Ждите следующего окна по opening_days_mode
                    logger.debug(
                        "В случае с odm + ea, если не подтвердить вовремя, до экстренный доступ не повторить"
                    )
                    capsule_date["opening_days_mode"] = True
                    self.create_console_output(status="8")
                else:
                    self.create_console_output(
                        status="7",
                        num_access=capsule_date["num_access"],
                        start_limit=str(capsule_date["start_limit"]),
                        end_limit=str(capsule_date["end_limit"]),
                    )
        else:  # Назначены первоначальные времена захода
            logger.debug("Назначаем первичные время для повторного подтверждения")
            set_start_and_end_time(self.current_time)
            capsule_date["num_access"] = 0
            if (
                "ea_time_separation" in capsule_date
                and capsule_date["ea_time_separation"][
                    capsule_date.get("num_access", 0)
                ][1]
                == "hidden"
            ):
                self.create_console_output(
                    status="6", num_access=capsule_date["num_access"]
                )
            elif "start_limit" in capsule_date and "end_limit" in capsule_date:
                self.create_console_output(
                    status="5",
                    num_access=capsule_date["num_access"],
                    start_limit=str(capsule_date["start_limit"]),
                    end_limit=str(capsule_date["end_limit"]),
                )
        logger.debug(
            "Перезаписываем капсулу(Т.к у нас могло изменится время, попытки, odm)"
        )
        self.write_capsule(self.deformat_dictionary(capsule_date))

    def create_console_output(self, **kwargs: Unpack[FunalOutputType]) -> None:
        self.final_console_output |= kwargs

    def format_dictionary(self, dct_unformat: UnformatData) -> FormatData:
        dct_format: FormatData = {
            "text": dct_unformat["text"],
            "open_time": datetime.datetime.strptime(
                dct_unformat["open_time"], "%Y-%m-%d %H:%M:%S"
            ),
            "date_change": datetime.datetime.strptime(
                dct_unformat["date_change"], "%Y-%m-%d %H:%M:%S"
            ),
            "emergency_access": (
                True if dct_unformat["emergency_access"] == "true" else False
            ),
            "opening_days_mode": (
                True if dct_unformat["opening_days_mode"] == "true" else False
            ),
        }

        if "day_week_odm" in dct_unformat:
            dct_format["day_week_odm"] = dct_unformat["day_week_odm"].split(",")

        if "num_week_odm" in dct_unformat:
            dct_format["num_week_odm"] = int(dct_unformat["num_week_odm"])

        if "time_odm_start" in dct_unformat:
            dct_format["time_odm_start"] = datetime.datetime.strptime(
                dct_unformat["time_odm_start"], "%H:%M"
            ).time()

        if "time_odm_end" in dct_unformat:
            dct_format["time_odm_end"] = datetime.datetime.strptime(
                dct_unformat["time_odm_end"], "%H:%M"
            ).time()

        dct_format["ea_after_open"] = (
            True if dct_unformat.get("ea_after_open") == "true" else False
        )

        if "ea_time_separation" in dct_unformat:
            dct_format["ea_time_separation"] = dct_unformat["ea_time_separation"]

        if "start_limit" in dct_unformat:
            dct_format["start_limit"] = datetime.datetime.strptime(
                dct_unformat["start_limit"], "%Y-%m-%d %H:%M:%S"
            )

        if "end_limit" in dct_unformat:
            dct_format["end_limit"] = datetime.datetime.strptime(
                dct_unformat["end_limit"], "%Y-%m-%d %H:%M:%S"
            )
        if "num_access" in dct_unformat:
            dct_format["num_access"] = int(dct_unformat["num_access"])
        return dct_format

    def deformat_dictionary(self, dct_format: FormatData) -> UnformatData:
        dct_unformat: UnformatData = {
            "text": dct_format["text"],
            "open_time": str(dct_format["open_time"]),
            "date_change": str(dct_format["date_change"]),
            "emergency_access": (
                "true" if dct_format["emergency_access"] == True else "false"
            ),
            "opening_days_mode": (
                "true" if dct_format["opening_days_mode"] == True else "false"
            ),
        }

        if "day_week_odm" in dct_format:
            dct_unformat["day_week_odm"] = ",".join(dct_format["day_week_odm"])

        if "num_week_odm" in dct_format:
            dct_unformat["num_week_odm"] = str(dct_format["num_week_odm"])

        if "time_odm_start" in dct_format:
            dct_unformat["time_odm_start"] = str(dct_format["time_odm_start"])[:-3]

        if "time_odm_end" in dct_format:
            dct_unformat["time_odm_end"] = str(dct_format["time_odm_end"])[:-3]

        dct_unformat["ea_after_open"] = (
            "true" if dct_format.get("ea_after_open") == True else "false"
        )

        if "ea_time_separation" in dct_format:
            dct_unformat["ea_time_separation"] = dct_format["ea_time_separation"]

        if "start_limit" in dct_format:
            dct_unformat["start_limit"] = str(dct_format["start_limit"])

        if "end_limit" in dct_format:
            dct_unformat["end_limit"] = str(dct_format["end_limit"])

        if "num_access" in dct_format:
            dct_unformat["num_access"] = str(dct_format["num_access"])
        return dct_unformat

    def write_capsule(self, save_date_dict: UnformatData) -> None:
        with open(f"{self.capsule_folder}/{str(self.id)}", "wb") as file:
            json_str = json.dumps(save_date_dict)
            encrypted_message = self.fernet.encrypt(json_str.encode())
            file.write(encrypted_message)

    def show_final_console_output(self) -> None:
        """
        Первая строка, статус
        1 - Доступ запрещён, капсула не открыта ИЛИ успешное создание капсулы
        2 - Текст получен
        3 - Экстренный доступ, + 1 попытка, время открыто
        4 - Экстренный доступ, + 1 попытка, время скрыто
        5 - Экстренный доступ запрошен, время назначено(В первый раз)
        6 - Экстренный доступ запрошен, время скрыто и не показывается(В случае hidden) - Повторный запрос не сбрасывает время(В первый раз)
        7 - Экстренный доступ сброшен время захода не правильное. Новое время назначено
        8 - Экстренный доступ сброшен, ЭД не реализовался при режиме opening_days_mode, придётся ждать следующего времени входа по opening_days_mode
        9 - Время захода не правильное, но оно скрытое, а поэтому не сбрасывается
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
        elif self.final_console_output["status"] == "5":
            print("5")
            print(self.final_console_output["num_access"])
            print(self.final_console_output["start_limit"])
            print(self.final_console_output["end_limit"])
        elif self.final_console_output["status"] == "6":
            print("6")
            print(self.final_console_output["num_access"])
        elif self.final_console_output["status"] == "7":
            print("7")
        elif self.final_console_output["status"] == "8":
            print("8")
        elif self.final_console_output["status"] == "9":
            print("9")
            print(self.final_console_output["num_access"])
