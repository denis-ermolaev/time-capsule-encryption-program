import subprocess


# Тестовый запуск создания
# python create_read_capsules.py 12 --create "gfbgfb" "2025-04-26 14:00:00" True 1 3
# python create_read_capsules.py 13 --create "gfbgfb" "2025-05-17 14:00:00" True 2 2

# Тестовый запуск открытия
# python create_read_capsules.py 12 --read
# python create_read_capsules.py 13 --read

result = subprocess.run(f'"dist/create_read_capsules/create_read_capsules.exe" 12 --read',shell=True, check=True, capture_output = True, text=True)
# result = subprocess.run(f'"dist/create_read_capsules/create_read_capsules.exe" 12 --create gfbgfb "2025-05-27 14:00:00" True 2 2',shell=True, check=True, capture_output = True, text=True)


print(str(result.stdout).split('\n'))
print(str(result.stdout))