#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")

import sys
import json
import os
import subprocess
from PIL import Image
from music21 import *

# === Пути ===
BASE_DIR = os.getcwd()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# === LilyPond ===
us = environment.UserSettings()
lilypond_path = os.environ.get("LILYPOND_PATH", "/usr/bin/lilypond")
us['lilypondPath'] = lilypond_path


def log(msg):
    print(msg, file=sys.stderr)


# === Упрощение аккордов ===
def simplify_chord(ch):
    pitches = sorted({p.nameWithOctave for p in ch.pitches})
    new_ch = chord.Chord(pitches)
    new_ch.duration = ch.duration
    return new_ch


# === Склейка PNG ===
def combine_images_vertical(images):
    if not images:
        return None

    max_width = max(img.width for img in images)
    normalized = []

    for img in images:
        if img.width != max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        normalized.append(img)

    total_height = sum(img.height for img in normalized)
    combined = Image.new("RGB", (max_width, total_height), "white")

    y = 0
    for img in normalized:
        combined.paste(img, (0, y))
        y += img.height

    return combined


# === Чистка .ly файла от устаревших команд LilyPond 2.24 ===
def clean_ly_file(path):
    with open(path, "r", encoding="utf-8") as f:
        ly = f.read()

    # Удаляем устаревшие команды
    bad_commands = [
        r"\RemoveEmptyStaffContext",
        r"\override VerticalAxisGroup #'remove-first = ##t",
    ]
    for cmd in bad_commands:
        ly = ly.replace(cmd, "")

    # Исправляем устаревший синтаксис
    ly = ly.replace("#'direction", "direction")

    # Удаляем двойные << >>, которые ломают 2.24.4
    ly = ly.replace("<<", "< <").replace(">>", "> >")

    with open(path, "w", encoding="utf-8") as f:
        f.write(ly)


# === Основная функция ===
def process_file(xml_path, semitones=-2):
    try:
        log(f"Загружаем MusicXML: {xml_path}")
        score = converter.parse(xml_path)

        if len(score.flat.notes) == 0:
            raise Exception("MusicXML содержит 0 нот")

        # Определяем тональность
        try:
            key = score.analyze("key")
            source_key = f"{key.tonic.name} {key.mode}"
        except:
            source_key = "unknown"

        # === Транспонирование ===
        transposed = score.transpose(semitones)

        # === Фикс beam-групп и длительностей ===
        transposed.makeNotation(inPlace=True)

        # === Упрощение аккордов ===
        for n in transposed.recurse().notes:
            if isinstance(n, chord.Chord):
                new = simplify_chord(n)
                n.pitches = new.pitches

        base = os.path.splitext(os.path.basename(xml_path))[0]
        ly_path = os.path.join(OUTPUTS_DIR, f"{base}_transposed.ly")

        log(f"Сохраняем .ly: {ly_path}")
        transposed.write("lilypond", fp=ly_path)

        # === Чистим .ly файл ===
        clean_ly_file(ly_path)

        # === Запуск LilyPond ===
        log("Запускаем LilyPond...")
        result = subprocess.run(
            [
                lilypond_path,
                "--png",
                "-dresolution=300",
                "-o",
                os.path.join(OUTPUTS_DIR, base + "_transposed"),
                ly_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            log(result.stderr)
            raise Exception("LilyPond compilation failed")

        # === Поиск PNG ===
        pngs = []
        page = 1

        while True:
            p = os.path.join(OUTPUTS_DIR, f"{base}_transposed-page{page}.png")
            if os.path.exists(p):
                pngs.append(p)
                page += 1
            else:
                break

        single = os.path.join(OUTPUTS_DIR, f"{base}_transposed.png")
        if not pngs and os.path.exists(single):
            pngs.append(single)

        if not pngs:
            raise Exception("PNG не созданы")

        # === Склейка ===
        images = [Image.open(p) for p in pngs]
        combined = combine_images_vertical(images)

        out_name = f"{base}_transposed.png"
        out_path = os.path.join(OUTPUTS_DIR, out_name)
        combined.save(out_path, optimize=True, quality=95)

        for img in images:
            img.close()
        for p in pngs:
            os.remove(p)

        result = {
            "success": True,
            "input_file": os.path.basename(xml_path),
            "output_files": [
                {
                    "path": out_path,
                    "name": out_name,
                    "url": f"/outputs/{out_name}",
                }
            ],
            "source_key": source_key,
            "message": "Готово",
        }

        print(json.dumps(result, ensure_ascii=False))
        return result

    except Exception as e:
        import traceback
        log(str(e))
        log(traceback.format_exc())
        print(json.dumps({"success": False, "error": str(e)}))
        return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No file path"}))
        sys.exit(1)

    xml_path = sys.argv[1]
    semitones = int(sys.argv[2]) if len(sys.argv) > 2 else -2

    process_file(xml_path, semitones)




