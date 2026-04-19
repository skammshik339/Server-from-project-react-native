#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")

import sys
import json
import os
import subprocess
import music21
from music21 import *

def log(msg):
    print(msg, file=sys.stderr)

log("music21 version: " + music21.__version__)

# === Пути ===
BASE_DIR = os.getcwd()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# === LilyPond ===
us = environment.UserSettings()
lilypond_path = os.environ.get("LILYPOND_PATH", "/usr/bin/lilypond")
us['lilypondPath'] = lilypond_path
log(f"LilyPond path: {lilypond_path}")


# ---------------------------------------------------------
# SIMPLIFY NOTES
# ---------------------------------------------------------
def simplify_notes(score):
    """Максимально упрощает ноты для LilyPond"""
    
    # 1. Превращаем всё в аккорды (убираем полифонию)
    score = score.chordify()
    log("Упрощено: chordify")
    
    # 2. Убираем все артикуляции, динамику, темпо
    for note in score.flat.notes:
        note.articulations = []
        note.expressions = []
    
    # 3. Убираем лиги и форшлаги
    for note in score.flat.notes:
        note.tie = None
        note.grace = None
    
    # 4. Упрощаем длительности до четвертей/восьмых
    for note in score.flat.notes:
        if note.duration.quarterLength not in [0.5, 1.0, 1.5, 2.0, 3.0, 4.0]:
            note.duration.quarterLength = 1.0
    
    log("Упрощены: артикуляции, длительности, лиги")
    return score


# ---------------------------------------------------------
# FIX LILYPOND FILE (УДАЛЯЕМ ПРОБЛЕМНЫЕ КОМАНДЫ)
# ---------------------------------------------------------
def fix_ly_file(ly_path):
    """Удаляет команды, которые не поддерживаются LilyPond"""
    with open(ly_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Удаляем проблемные команды
    content = content.replace("\\RemoveEmptyStaffContext", "")
    content = content.replace("\\RemoveEmptyStaffContext", "", 1)
    
    # Удаляем строки, начинающиеся с этих команд
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        if 'RemoveEmptyStaffContext' in line:
            continue
        if '\\new Staff' in line and '\\RemoveEmptyStaffContext' in line:
            line = line.replace('\\RemoveEmptyStaffContext', '')
        cleaned_lines.append(line)
    
    content = '\n'.join(cleaned_lines)
    
    # Базовые замены синтаксиса
    content = content.replace("\\override Stem #'direction", "\\override Stem.direction")
    content = content.replace("\\override VerticalAxisGroup #'remove-first", "\\override VerticalAxisGroup.remove-first")
    
    with open(ly_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    log(f"LilyPond файл исправлен")


# ---------------------------------------------------------
# MAIN PROCESSING
# ---------------------------------------------------------
def process_file(xml_path, semitones=-2):
    try:
        log(f"Обработка: {xml_path}")

        # Загружаем MusicXML
        score = converter.parse(xml_path)
        log(f"Загружено нот: {len(score.flat.notes)}")

        # Упрощаем ноты
        score = simplify_notes(score)

        # Определяем тональность
        try:
            key = score.analyze('key')
            source_key = f"{key.tonic.name} {key.mode}"
            log(f"Тональность: {source_key}")
        except:
            source_key = "unknown"

        # Транспонируем
        log(f"Транспонируем на {semitones} полутонов")
        transposed = score.transpose(semitones)

        # Сохраняем как LilyPond
        base_name = os.path.splitext(os.path.basename(xml_path))[0]
        ly_path = os.path.join(OUTPUTS_DIR, f"{base_name}.ly")
        
        log(f"Сохраняем .ly: {ly_path}")
        transposed.write('lilypond', fp=ly_path)

        # Исправляем LilyPond файл (удаляем проблемные команды)
        fix_ly_file(ly_path)

        # Рендерим PNG
        log("Запускаем LilyPond...")
        result = subprocess.run(
            [
                lilypond_path,
                '--png',
                '-dresolution=150',
                '-o', os.path.join(OUTPUTS_DIR, base_name),
                ly_path
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            log(f"LilyPond ошибка: {result.stderr[:300]}")
            raise Exception("LilyPond compilation failed")

        # Ищем PNG
        png_file = None
        for f in os.listdir(OUTPUTS_DIR):
            if f.startswith(base_name) and f.endswith('.png'):
                png_file = f
                break

        if not png_file:
            raise Exception("PNG не создан")

        png_path = os.path.join(OUTPUTS_DIR, png_file)
        log(f"Создан PNG: {png_path}")

        # Результат
        result_data = {
            "success": True,
            "input_file": os.path.basename(xml_path),
            "output_files": [{
                "path": png_path,
                "name": png_file,
                "url": f"/outputs/{png_file}"
            }],
            "source_key": source_key,
            "message": "Готово"
        }

        print(json.dumps(result_data, ensure_ascii=False))
        return result_data

    except Exception as e:
        log(f"ОШИБКА: {str(e)}")
        print(json.dumps({"success": False, "error": str(e)}))
        return None


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No file path"}))
        sys.exit(1)

    xml_path = sys.argv[1]
    semitones = int(sys.argv[2]) if len(sys.argv) > 2 else -2

    process_file(xml_path, semitones)








