import subprocess


# Тестовый запуск создания
# python main.py 12 --create "gfbgfb" "2025-04-17 14:00:00" True 1 3
# python main.py 13 --create "gfbgfb" "2025-05-17 14:00:00" False 2 2

# Тестовый запуск открытия
# python main.py 12 --read
# python main.py 13 --read

result = subprocess.run('"dist/create_read_capsules/create_read_capsules.exe" 13 --read',shell=True, check=True, capture_output = True, text=True)
#result = subprocess.run('"dist/create_read_capsules/create_read_capsules.exe" 13 --create gfbgfb "2025-05-17 14:00:00" True 2 2',shell=True, check=True, capture_output = True, text=True)
#result = subprocess.run('"dist/create_read_capsules/create_read_capsules.exe" --help',shell=True, check=True, capture_output = True, text=True)
print(str(result.stdout).split('\n')[0:-1])
print(str(result.stdout))