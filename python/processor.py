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

# === Настройка пути к LilyPond ===
us = environment.UserSettings()
lilypond_path = os.environ.get("LILYPOND_PATH", "/usr/bin/lilypond")
us['lilypondPath'] = lilypond_path


def log(msg):
    """Пишет в stderr (не мешает stdout)"""
    print(msg, file=sys.stderr)

def crop_bottom_keep_top(image_path, keep_percent=20):
    """
    Оставляет только верхние keep_percent процентов изображения
    (обрезает нижние 100-keep_percent процентов)
    """
    img = Image.open(image_path)
    width, height = img.size
    # Вычисляем, сколько пикселей оставить сверху
    keep_height = int(height * keep_percent / 100)
    # Обрезаем снизу: оставляем только верхнюю часть
    cropped = img.crop((0, 0, width, keep_height))
    return cropped, img

def combine_images_vertical(images):
    """
    Склеивает изображения по вертикали с сохранением пропорций
    """
    if not images:
        return None
    
    # Определяем максимальную ширину
    max_width = max(img.width for img in images)
    
    # Нормализуем все изображения до одинаковой ширины (сохраняя пропорции)
    normalized_images = []
    for img in images:
        if img.width != max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            resized = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            normalized_images.append(resized)
        else:
            normalized_images.append(img)
    
    # Вычисляем общую высоту
    total_height = sum(img.height for img in normalized_images)
    
    # Создаём новое изображение с белым фоном
    combined = Image.new('RGB', (max_width, total_height), 'white')
    
    y_offset = 0
    for img in normalized_images:
        combined.paste(img, (0, y_offset))
        y_offset += img.height
    
    return combined

def process_file(xml_path, semitones=-2):
    try:
        log(f"Загружаем MusicXML: {xml_path}")

        score = converter.parse(xml_path)

        try:
            key = score.analyze('key')
            source_key = f"{key.tonic.name} {key.mode}"
            log(f"Определена тональность: {source_key}")
        except:
            source_key = "unknown"

        log(f"Транспонируем на {semitones} полутонов")
        transposed = score.transpose(semitones)

        base_name = os.path.splitext(os.path.basename(xml_path))[0]
        ly_filename = f"{base_name}_transposed.ly"
        ly_path = os.path.join('outputs', ly_filename)

        os.makedirs('outputs', exist_ok=True)

        # Сохраняем как LilyPond
        log(f"Сохраняем LilyPond файл: {ly_path}")
        transposed.write('lilypond', fp=ly_path)

        # Вызываем LilyPond для рендеринга
        lilypond_exe = lilypond_path


        log("Запускаем LilyPond...")
        
        result = subprocess.run([
            lilypond_exe,
            '--png',
            '-dresolution=300',
            '-o', os.path.join('outputs', base_name + '_transposed'),
            ly_path
        ], capture_output=True, text=True)

        if result.returncode != 0:
            log(f"LilyPond ошибка: {result.stderr}")
            raise Exception("LilyPond compilation failed")
        
        log("LilyPond успешно завершил работу")

        # Собираем все созданные PNG
        raw_png_files = []
        page = 1
        while True:
            png_path = os.path.join('outputs', f"{base_name}_transposed-page{page}.png")
            if os.path.exists(png_path):
                raw_png_files.append(png_path)
                log(f"Найден PNG: {png_path}")
                page += 1
            else:
                break

        if not raw_png_files:
            single_png = os.path.join('outputs', f"{base_name}_transposed.png")
            if os.path.exists(single_png):
                raw_png_files.append(single_png)
                log(f"Найден одиночный PNG: {single_png}")

        if not raw_png_files:
            raise Exception("Нет созданных PNG файлов")

        log(f"Всего исходных PNG: {len(raw_png_files)}")

        # Обрезаем каждую страницу: оставляем только верхние 20%
        cropped_images = []
        for png_path in raw_png_files:
            cropped_img, original_img = crop_bottom_keep_top(png_path, keep_percent=20)
            cropped_images.append(cropped_img)
            original_img.close()
            log(f"Обрезана страница: {png_path} (оставлено верхних 20%)")

        # Склеиваем по 5 страниц
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
                output_path = os.path.join('outputs', output_filename)
                combined.save(output_path, optimize=True, quality=95)
                combined_pngs.append({
                    "path": output_path,
                    "name": output_filename,
                    "url": f"/outputs/{output_filename}"
                })
                log(f"Создана комбинированная страница {group_idx + 1}: {output_path}")
                combined.close()

        # Закрываем все обрезанные изображения
        for img in cropped_images:
            img.close()

        # Удаляем исходные страницы
        for png_path in raw_png_files:
            if os.path.exists(png_path):
                os.remove(png_path)
                log(f"Удалён исходный файл: {png_path}")

        log(f"Всего итоговых PNG: {len(combined_pngs)}")

        # Формируем результат
        final_result = {
            "success": True,
            "input_file": os.path.basename(xml_path),
            "output_files": combined_pngs,
            "source_key": source_key,
            "message": f"Транспонирование выполнено успешно ({len(combined_pngs)} файлов)"
        }

        print(json.dumps(final_result, ensure_ascii=False))
        return final_result

    except Exception as e:
        log(f"ОШИБКА: {str(e)}")
        import traceback
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