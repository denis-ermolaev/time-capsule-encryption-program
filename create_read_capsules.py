import os
import datetime
from cryptography.fernet import Fernet
import argparse
import json

# Папка, в которой хранятся капсулы времени
capsule_folder = "capsules"

# Проверяем, существует ли папка для капсул времени, и создаем ее, если она отсутствует
if not os.path.exists(capsule_folder):
    os.mkdir(capsule_folder)

key = b''
cipher_suite = Fernet(key)

# type=int, choices=[0, 1, 2], action="store_true"
parser = argparse.ArgumentParser(description="""
                                 Позволяет создать или открыть зашифрованную капсулу времени
                                 Доступ к капсуле можно получить, после даты-времени открытия, если доступ
                                 запрашивается раньше, тогда проверяется экстренный доступ, если он False, тогда доступ к капсуле
                                 раньше времени получить нельзя, если True, то действует следующая система:
                                 1. После запроса экстренного доступа, нужно запустить программу с запросом чтения капсулы ещё раз в определённые часы
                                 2. Если следующий запрос произведён не в нужные часы, то процесс экстренного доступа сбрасывается
                                 3. Если в нужные, то назначается новое время следующего запроса экстренного доступа
                                 4. В итоге доступ к капсуле будет получен, когда кол-во запросов будет равно число Разрывов при создании капсулы
                                 """)

# Тестовый запуск создания
# python main.py 12 --create "gfbgfb" "2025-04-17 14:00:00" True 1 3
# python main.py 13 --create "gfbgfb" "2025-05-17 14:00:00" True 2 2

# Тестовый запуск открытия
# python main.py 12 --read
# python main.py 13 --read

group_create = parser.add_mutually_exclusive_group()

# Тест, Время после которого открытие, Экстренный доступ, Кол-во часов, разрывы
group_create.add_argument("--create", nargs=5, 
                          help="5 аргументов. Текст, Дата-Время после которых открытие (2025-04-17 14:00:00), Экстренный доступ(True/False), Кол-во часов(number), Разрывы(number)") 

group_create.add_argument("--read", action="store_true", help="Для чтения капсулы --read, для создания --create с 5-тью аргументами")


parser.add_argument("id", type=int, help="Не зависимо от чтения или создания, нужно id, это имя файла капсулы")

args = parser.parse_args()

def write_capsule(capsule_folder, id, dict_for_encrypt):
    with open(capsule_folder +"/" +str(id), "wb") as file:
        json_str = json.dumps(dict_for_encrypt)
        encrypted_message = cipher_suite.encrypt(json_str.encode())
        file.write(encrypted_message)

if args.read == False: # Создание
    open_time = datetime.datetime.strptime(args.create[1], '%Y-%m-%d %H:%M:%S') # Выдаст ошибку, если время не правильное
    result_dict = {"text":args.create[0], "open_time":args.create[1], "emergency_access":args.create[2],
                   "time":args.create[3], "time_break":args.create[4]}
    write_capsule(capsule_folder, args.id, result_dict)
    print("Успешное создание капсулы")
else: # Чтение
    with open(capsule_folder +"/" +str(args.id), 'rb') as file:
        capsule_data = file.read()
        decrypted_data = cipher_suite.decrypt(capsule_data).decode()
        decrypted_json = json.loads(decrypted_data) # loads - из строки, load из файла, аналогично dumps и dump
        open_time = datetime.datetime.strptime(decrypted_json['open_time'], '%Y-%m-%d %H:%M:%S')
        current_time = datetime.datetime.now()
        print("Текущие время сервера:", str(current_time)[0:19])
        if current_time > open_time:
            print(decrypted_json['text'])
        elif decrypted_json['emergency_access'] == 'True':
            print("Капсула может быть открыта с помощью экстренного доступа. Запускаем экстренный доступ")
            UPDATE_START_AND_END_TIME = int(decrypted_json['time']) // int(decrypted_json['time_break'])
            print("Время каждую итерацию увеличивается на", UPDATE_START_AND_END_TIME, "час")
            print("Для открытие капсулы нужно", UPDATE_START_AND_END_TIME*int(decrypted_json['time_break']), "часов")
            if decrypted_json.get('start_limit', False):
                start_limit = datetime.datetime.strptime(decrypted_json['start_limit'], '%Y-%m-%d %H:%M:%S')
                end_limit = datetime.datetime.strptime(decrypted_json['end_limit'], '%Y-%m-%d %H:%M:%S')
                if current_time > start_limit and current_time < end_limit:
                    decrypted_json['num_access'] += 1
                    if int(decrypted_json['num_access']) == int(decrypted_json['time_break']):
                        print("Капсула может быть открыта")
                        print(decrypted_json['text'])
                        del decrypted_json['num_access']
                        del decrypted_json['start_limit']
                        del decrypted_json['end_limit']
                    else:
                        print("Успешная итерация, назначены новые дата начала и дата конца следующего запроса доступа")
                        decrypted_json['start_limit'] = str(start_limit + datetime.timedelta(hours=UPDATE_START_AND_END_TIME))[0:19]
                        decrypted_json['end_limit'] = str(end_limit + datetime.timedelta(hours=UPDATE_START_AND_END_TIME))[0:19]
                        # decrypted_json['start_limit'] = str(start_limit + datetime.timedelta(minutes=1))[0:19]
                        # decrypted_json['end_limit'] = str(end_limit + datetime.timedelta(minutes=1))[0:19]
                        print("Вам нужно зайти с", decrypted_json['start_limit'], "до", decrypted_json['end_limit'])
                        print("Сейчас ", decrypted_json['num_access'], "итерация, из", decrypted_json['time_break'])
                    
                else:
                    print("Правильное время пропущено, Новые дата начала и дата конца")
                    decrypted_json['start_limit'] = str(current_time + datetime.timedelta(hours=UPDATE_START_AND_END_TIME))[0:19]
                    decrypted_json['end_limit'] = str(current_time + datetime.timedelta(hours=UPDATE_START_AND_END_TIME, minutes=15))[0:19]
                    # decrypted_json['start_limit'] = str(current_time + datetime.timedelta(minutes=1))[0:19]
                    # decrypted_json['end_limit'] = str(current_time + datetime.timedelta(minutes=15))[0:19]
                    decrypted_json['num_access'] = 0
                    print("Вам нужно зайти с", decrypted_json['start_limit'], "до", decrypted_json['end_limit'])
                    print("Сейчас ", decrypted_json['num_access'], "итерация, из", decrypted_json['time_break'])
            else:
                decrypted_json['start_limit'] = str(current_time + datetime.timedelta(hours=UPDATE_START_AND_END_TIME))[0:19]
                decrypted_json['end_limit'] = str(current_time + datetime.timedelta(hours=UPDATE_START_AND_END_TIME, minutes=15))[0:19]
                # decrypted_json['start_limit'] = str(current_time + datetime.timedelta(minutes=1))[0:19]
                # decrypted_json['end_limit'] = str(current_time + datetime.timedelta(minutes=15))[0:19]
                decrypted_json['num_access'] = 0
                print("Вам нужно зайти с", decrypted_json['start_limit'], "до", decrypted_json['end_limit'])
                print("Сейчас ", decrypted_json['num_access'], "итерация, из", decrypted_json['time_break'])
            
            write_capsule(capsule_folder, args.id, decrypted_json)
        else:
            print("Капсула не может быть отрыта")
        
        