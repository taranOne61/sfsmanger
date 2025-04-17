import os
import sqlite3
import json
from pathlib import Path

# Проверяем доступность библиотеки android.storage перед попыткой использования
try:
    from android.storage import primary_external_storage_path

    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

# Директория с деталями (относительная к проекту)
if IS_ANDROID:
    BASE_DIRECTORY = primary_external_storage_path()
else:
    BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

DETAILS_DIRECTORY = os.path.join(BASE_DIRECTORY, 'details')
TARGET_DATABASE_PATH = os.path.join(BASE_DIRECTORY, 'templates.db')

# Основные ключи и их изменяемые параметры
KEYS_TO_CHANGE = {
    'p': {'x': 'float', 'y': 'float'},
    'o': {'x': 'float', 'y': 'float', 'z': 'float'},
    'N': {'size': 'float', 'width_original': 'float', 'width_a': 'float', 'width_b': 'float',
          'height': 'float', 'fuel_percent': 'float', 'force_percent': 'float', 'force_multiplier': 'float',
          'sep_force_multiplier': 'float', 'state': 'float', 'state_target': 'float'},
    'B': {'engine_on': 'bool', 'heat_on__for_creative_use': 'bool', 'gimbal_on': 'bool',
          'detach_edge': 'bool', 'adapt_to_tank': 'bool', 'occupied_a': 'bool'}
}


# Функция для изменения значения в JSON-объекте
def change_value_in_json(obj, key, new_value):
    if isinstance(new_value, str):
        try:
            new_value = float(new_value)
        except ValueError:
            pass  # Оставляем строковым значением, если не удается преобразовать в число
    obj[key] = new_value


# Основная логика программы
def main():
    global data  # Объявляем переменную глобальной, чтобы она была доступна позже

    # Запрашиваем путь для новой директории
    user_chosen_dir = input("\nУкажите полный путь к директории для сохранения новых файлов: ").strip()
    Path(user_chosen_dir).mkdir(parents=True, exist_ok=True)

    # Используем выбранную пользователем директорию
    output_directory = user_chosen_dir

    # Ищем файлы в подпапках
    found_blueprints = []
    for root, dirs, files in os.walk(DETAILS_DIRECTORY):
        for file in files:
            if file == 'Blueprint.txt':
                found_blueprints.append((root, file))

    if not found_blueprints:
        print("Ни одного файла Blueprint.txt не обнаружено.")
        return

    # Выводим список доступных файлов с нумерацией
    print("Список доступных файлов для редактирования:")
    for i, (root, _) in enumerate(found_blueprints):
        print(f"[{i}] {os.path.basename(root)}")

    # Пользователь выбирает файл
    while True:
        choice = input("Введите номер файла для редактирования (или q для выхода): ")
        if choice.strip().lower() == 'q':
            print("Выход из программы.")
            return
        try:
            choice_num = int(choice)
            if 0 <= choice_num < len(found_blueprints):
                chosen_root, _ = found_blueprints[choice_num]
                blueprint_file_path = os.path.join(chosen_root, 'Blueprint.txt')
                break
            else:
                print("Номер вне диапазона. Попробуйте снова.")
        except ValueError:
            print("Введите действительное число или 'q' для выхода.")

    # Читаем содержимое файла
    with open(blueprint_file_path, 'r') as f:
        content = f.read()

    try:
        # Парсим JSON-данные
        data = json.loads(content)
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return

    # Обрабатываем части ("parts") в JSON
    parts = data.get('parts')
    if parts is None or not isinstance(parts, list):
        print("Не удалось найти массив 'parts'.")
        return

    for part_index, part in enumerate(parts):
        print(f"\nОбрабатываем часть №{part_index + 1}:")
        for key in KEYS_TO_CHANGE.keys():
            if key in part:
                print(f"Объект с ключом '{key}' найден:")
                for param_key, param_type in KEYS_TO_CHANGE[key].items():
                    if param_key in part[key]:
                        current_value = part[key][param_key]

                        if param_type == 'float':
                            while True:
                                new_value = input(
                                    f"Введите новое значение для параметра '{param_key}' ({current_value}): ")
                                try:
                                    new_value = float(new_value)
                                    break
                                except ValueError:
                                    print("Введите числовое значение.")
                        elif param_type == 'bool':
                            while True:
                                choice = input(
                                    f"Введите новое значение для параметра '{param_key}' (1 - true, 2 - false): ")
                                if choice == '1':
                                    new_value = True
                                    break
                                elif choice == '2':
                                    new_value = False
                                    break
                                else:
                                    print("Выберите 1 или 2.")

                        change_value_in_json(part[key], param_key, new_value)
                        print(f"Параметр '{param_key}' успешно изменён на {new_value}.")
                    else:
                        print(f"Параметра '{param_key}' не найдено в ключе '{key}'. Пропускаем...")

    # Сохраняем изменённый файл
    save_file_path = os.path.join(output_directory, 'Blueprint.txt')
    with open(save_file_path, 'w') as f:
        json.dump(data, f, indent=4)

    # Создаем файл Version.txt с фиксированной версией
    version_file_path = os.path.join(output_directory, 'Version.txt')
    with open(version_file_path, 'w') as vf:
        vf.write('"1.59.15"')

    print(f"Изменённый файл и Version.txt сохранены в {output_directory}.")

    # Завершаем выполнение программы
    print("Работа программы завершена.")


if __name__ == "__main__":
    main()