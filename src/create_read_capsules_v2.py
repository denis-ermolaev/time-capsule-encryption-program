import argparse
from СapsuleProcessor import СapsuleProcessor, logger

# Тестовый запуск создания
# python src/create_read_capsules_v2.py 1 --create "gfbgfb" "2025-04-26 14:00:00" "2025-04-26 14:00:00"
# python src/create_read_capsules_v2.py 2 --create "gfbgfb" "2025-04-17 14:00:00" "2025-04-26 14:00:00" --emergency true '[[[0.1, 0.2], "hidden"], [[0.1, 0.2] , "open"]]'
# python src/create_read_capsules_v2.py 2 --create "gfbgfb" "2025-04-17 14:00:00" "2025-04-26 14:00:00" --emergency true '[[[0.1, 0.2], "hidden"], [[0.1, 0.2] , "open"]]' --opening_days_mode "m,t,w" 2 "12:00" "13:00"

# Тестовый запуск открытия
# python src/create_read_capsules_v2.py 1 --read
# python src/create_read_capsules_v2.py 2 --read

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


capsule_processor = СapsuleProcessor(args)
capsule_processor.show_final_console_output()
