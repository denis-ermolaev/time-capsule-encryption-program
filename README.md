# Build

`pyarmor gen --enable-jit --mix-str --assert-call --private foo.py`

`pyarmor gen --enable-jit --assert-call --private create_read_capsules.py`

`pyarmor gen --enable-jit --assert-call --private --pack onefile main.py`

`pyarmor gen --enable-jit --assert-call --private --pack onedir create_read_capsules.py`

# Возможные аргументы

- id\*
- Либо --read либо --create. В случае с --create, доп аргументы\*:

1. text Текст
2. date_open Дата-Время после которых открытие (2025-04-17 14:00:00)
3. date_change - Последний, с него считаются недели для opening_days_mode

- Флаг --emergency

1. ea_after_open(true false) ЭД доступен только после времени открытия(Т.е открытие просто так не работает)
2. ea_time_separation - [ [ [1, 1], 'hidden'], [ [1, 5] , 'open'], [ [0.5,0.5], 'open'] ] - json
   Работает так, в начале первый запрос экстренного доступа, выбирается случайное число от 1 до 1 часа
   Причём время захода сказано не будет, т.е надо переодически заходить проверять
   Дальше от 1 до 5 часов, нужно подождать, время будет дано конкретное, если зайти в другое, то сброс и так далее

- Флаг --opening_days_mode

1. day_week_odm - m,t,w,th,f,sa,su - дни недели, когда капсулу можно открыть
2. num_week_odm - раз в сколько недель. Если 0, то каждую неделю
3. time_odm_start - С этого времени 12:00
4. time_odm_end - До этого времени 13:00
