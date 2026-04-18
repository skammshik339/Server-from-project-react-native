#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")

import sys
import json
import os
import subprocess
import math
from PIL import Image
from music21 import *

# === Базовые пути ===
BASE_DIR = os.getcwd()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# === Настройка пути к LilyPond ===
us = environment.UserSettings()
lilypond_path = os.environ.get("LILYPOND_PATH", "/usr/bin/lilypond")
us['lilypondPath'] = lilypond_path


def log(msg):
    print(msg, file=sys.stderr)


def combine_images_vertical(images):
    if not images:
        return None

    max_width = max(img.width for img in images)
    normalized_images = []

    for img in images:
        if img.width != max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            resized = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            normalized_images.append(resized)
        else:
            normalized_images.append(img)

    total_height = sum(img.height for img in normalized_images)
    combined = Image.new("RGB", (max_width, total_height), "white")

    y_offset = 0
    for img in normalized_images:
        combined.paste(img, (0, y_offset))
        y_offset += img.height

    return combined


def process_file(xml_path, semitones=-2):
    try:
        log(f"Загружаем MusicXML: {xml_path}")

        # === Читаем MusicXML ===
        score = converter.parse(xml_path)

        # === КРИТИЧЕСКАЯ ПРОВЕРКА ===
        note_count = len(score.flat.notes)
        log(f"НОТ В ФАЙЛЕ: {note_count}")

        if note_count == 0:
            raise Exception(
                "MusicXML содержит 0 нот — файл не читается этой версией music21 или повреждён."
            )

        # === Определяем тональность ===
        try:
            key = score.analyze("key")
            source_key = f"{key.tonic.name} {key.mode}"
            log(f"Определена тональность: {source_key}")
        except Exception:
            source_key = "unknown"

        # === Транспонирование ===
        log(f"Транспонируем на {semitones} полутонов")
        transposed = score.transpose(semitones)

        base_name = os.path.splitext(os.path.basename(xml_path))[0]
        ly_filename = f"{base_name}_transposed.ly"
        ly_path = os.path.join(OUTPUTS_DIR, ly_filename)

        # === Сохраняем .ly ===
        log(f"Сохраняем LilyPond файл: {ly_path}")
        transposed.write("lilypond", fp=ly_path)

        # === Запускаем LilyPond ===
        log("Запускаем LilyPond...")

        result = subprocess.run(
            [
                lilypond_path,
                "--png",
                "-dresolution=300",
                "-o",
                os.path.join(OUTPUTS_DIR, base_name + "_transposed"),
                ly_path,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            log(f"LilyPond stderr: {result.stderr}")
            raise Exception("LilyPond compilation failed")

        log("LilyPond успешно завершил работу")

        # === Ищем PNG ===
        raw_png_files = []
        page = 1

        while True:
            png_path = os.path.join(
                OUTPUTS_DIR, f"{base_name}_transposed-page{page}.png"
            )
            if os.path.exists(png_path):
                raw_png_files.append(png_path)
                log(f"Найден PNG: {png_path}")
                page += 1
            else:
                break

        if not raw_png_files:
            single_png = os.path.join(
                OUTPUTS_DIR, f"{base_name}_transposed.png"
            )
            if os.path.exists(single_png):
                raw_png_files.append(single_png)
                log(f"Найден одиночный PNG: {single_png}")

        if not raw_png_files:
            raise Exception("LilyPond не создал PNG — ошибка рендеринга.")

        log(f"Всего исходных PNG: {len(raw_png_files)}")

        # === БЕЗ ОБРЕЗКИ — берём как есть ===
        cropped_images = []
        for png_path in raw_png_files:
            img = Image.open(png_path)
            cropped_images.append(img)
            log(f"Страница без обрезки: {png_path}")

        # === Склейка ===
        pages_per_combined = 5
        combined_pngs = []
        num_groups = math.ceil(len(cropped_images) / pages_per_combined)

        for group_idx in range(num_groups):
            start = group_idx * pages_per_combined
            end = min(start + pages_per_combined, len(cropped_images))
            group_images = cropped_images[start:end]

            combined = combine_images_vertical(group_images)

            if combined:
                if num_groups == 1:
                    output_filename = f"{base_name}_transposed.png"
                else:
                    output_filename = f"{base_name}_transposed_{group_idx + 1}.png"

                output_path = os.path.join(OUTPUTS_DIR, output_filename)
                combined.save(output_path, optimize=True, quality=95)

                combined_pngs.append(
                    {
                        "path": output_path,
                        "name": output_filename,
                        "url": f"/outputs/{output_filename}",
                    }
                )

                log(f"Создана комбинированная страница {group_idx + 1}: {output_path}")
                combined.close()

        # === Закрываем изображения ===
        for img in cropped_images:
            img.close()

        # === Удаляем исходные PNG ===
        for png_path in raw_png_files:
            if os.path.exists(png_path):
                os.remove(png_path)
                log(f"Удалён исходный файл: {png_path}")

        log(f"Всего итоговых PNG: {len(combined_pngs)}")

        # === Ответ ===
        final_result = {
            "success": True,
            "input_file": os.path.basename(xml_path),
            "output_files": combined_pngs,
            "source_key": source_key,
            "message": f"Транспонирование выполнено успешно ({len(combined_pngs)} файлов)",
        }

        print(json.dumps(final_result, ensure_ascii=False))
        return final_result

    except Exception as e:
        import traceback
        log(f"ОШИБКА: {str(e)}")
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


