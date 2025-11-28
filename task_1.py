"""
Рекурсивне переміщення та сортування файлів із вихідної директорії
до директорії призначення.

Функціональність:
- Парсинг аргументів командного рядка (source, destination).
- Рекурсивний обхід усіх вкладених папок вихідної директорії.
- Переміщення кожного файлу до піддиректорії у директорії призначення,
  назва якої відповідає розширенню файлу.
- Обробка помилок доступу, зіткнень і неможливості переміщення.
- Ігнорування директорії призначення, якщо вона знаходиться всередині джерела.
"""


import argparse  
import shutil    
from pathlib import Path  


def copy_and_sort(src: Path, dst_root: Path) -> None:
    """
    Рекурсивно обходить директорію-джерело та переміщує файли
    до директорії призначення, розкладаючи їх у піддиректорії за розширенням.

    Параметри:
        src (Path): поточна директорія, яку обходимо.
        dst_root (Path): коренева директорія призначення.

    Поведінка:
        - Кожен файл переміщується у dst_root/<extension>.
        - Файли без розширення зберігаються у папці 'no_extension'.
        - Якщо target-файл вже існує, shutil.move може перезаписати його,
          залежно від ОС.
        - Папка призначення, якщо вона знаходиться всередині джерела,
          не обходиться рекурсивно.
    """
    try:  
        for item in src.iterdir():                        # Проходимо усі елементи у поточній директорії
            if item.is_dir():                             # Якщо елемент є директорією
                if item.resolve() == dst_root.resolve():  # Перевіряємо, чи не є елемент директорією призначення
                    continue                              # Якщо так, пропускаємо
                copy_and_sort(item, dst_root)             # Викликаємо рекурсивно для піддиректорії
            elif item.is_file():                          # Якщо елемент є файлом
                ext = item.suffix.lower().lstrip(".")     # Отримуємо розширення файлу
                if not ext:                               # Якщо розширення відсутнє
                    ext = "no_extension"                  # Встановлюємо розширення "no_extension"

                target_dir = dst_root / ext                    # Створюємо директорію призначення для розширення
                target_dir.mkdir(parents=True, exist_ok=True)  # Створюємо директорію, якщо вона не існує

                target_file = target_dir / item.name           # Створюємо шлях до файлу в директорії призначення

                try:  
                    shutil.move(str(item), str(target_file))   # Переміщуємо файл до директорії призначення
                except (OSError, PermissionError) as e:        # Якщо виникає помилка при переміщенні
                    print(f"Помилка переміщення '{item}': {e}") 
    except (PermissionError, OSError) as e:                    # Якщо виникає помилка при доступі до директорії
        print(f"Помилка доступу до директорії '{src}': {e}") 


def parse_args() -> argparse.Namespace:
    """
    Парсить аргументи командного рядка.

    Аргументи:
        source — шлях до вихідної директорії (обов'язковий).
        destination — шлях до директорії призначення
                       (необов'язковий, за замовчуванням 'dist').

    Повертає:
        argparse.Namespace з полями source і destination.

    Примітка:
        Директорія destination буде створена автоматично, якщо вона відсутня.
    """
    parser = argparse.ArgumentParser( 
        description="Рекурсивно переміщує файли з сортуванням за розширенням."  
    )
    parser.add_argument(  
        "source",
        help="Шлях до вихідної директорії.", 
    )
    parser.add_argument(  
        "destination",
        nargs="?",  
        default="dist",  
        help="Шлях до директорії призначення (за замовчуванням: dist).", 
    )
    return parser.parse_args()  


def main() -> None:
    """
    Точка входу програми.

    Логіка:
        - Зчитує аргументи командного рядка.
        - Перевіряє існування джерела.
        - Створює директорію призначення (якщо немає).
        - Викликає рекурсивне переміщення та сортування файлів.
    """
    args = parse_args()  
    src = Path(args.source).resolve()  
    dst = Path(args.destination).resolve()  

    if not src.exists() or not src.is_dir():  
        print(f"Помилка: директорія джерела '{src}' не існує або не є директорією.")  
        return  

    try:  
        dst.mkdir(parents=True, exist_ok=True) 
    except (OSError, PermissionError) as e:  
        print(f"Не вдалося створити директорію призначення '{dst}': {e}")  
        return 

    copy_and_sort(src, dst)  
    print("Переміщення та сортування завершено.") 


if __name__ == "__main__": 
    main()  
