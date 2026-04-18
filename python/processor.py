#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")

import sys
import json
import os
import subprocess
from PIL import Image
from music21 import *

def log(msg):
    print(msg, file=sys.stderr)

# Показываем версию music21
log("music21 version: " + music21.__version__)

# === Пути ===
BASE_DIR = os.getcwd()
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# === LilyPond ===
us = environment.UserSettings()
lilypond_path = os.environ.get("LILYPOND_PATH", "/usr/bin/lilypond")
us['lilypondPath'] = lilypond_path

# === КРИТИЧЕСКОЕ: заставляем music21 использовать старый форматтер ===
env = environment.Environment()
env['lilypondVersion'] = '2.18.0'



def log(msg):
    print(msg, file=sys.stderr)

log("music21 version: " + music21.__version__)

def simplify_chord(ch):
    pitches = sorted({p.nameWithOctave for p in ch.pitches})
    new_ch = chord.Chord(pitches)
    new_ch.duration = ch.duration
    return new_ch


def clean_ly_file(path):
    with open(path, "r", encoding="utf-8") as f:
        ly = f.read()

    # Удаляем мусор
    ly = ly.replace("\\RemoveEmptyStaffContext", "")
    ly = ly.replace("#'direction", "direction")

    # Убираем вложенные << >>
    ly = ly.replace("<<", "< <")
    ly = ly.replace(">>", "> >")

    with open(path, "w", encoding="utf-8") as f:
        f.write(ly)


def process_file(xml_path, semitones=-2):
    try:
        log(f"Загружаем MusicXML: {xml_path}")
        score = converter.parse(xml_path)

        if len(score.flat.notes) == 0:
            raise Exception("MusicXML содержит 0 нот")

        try:
            key = score.analyze("key")
            source_key = f"{key.tonic.name} {key.mode}"
        except:
            source_key = "unknown"

        transposed = score.transpose(semitones)
        transposed.makeNotation(inPlace=True)

        for n in transposed.recurse().notes:
            if isinstance(n, chord.Chord):
                new = simplify_chord(n)
                n.pitches = new.pitches

        base = os.path.splitext(os.path.basename(xml_path))[0]
        ly_path = os.path.join(OUTPUTS_DIR, f"{base}_transposed.ly")

        log(f"Сохраняем .ly: {ly_path}")
        transposed.write("lilypond", fp=ly_path)

        clean_ly_file(ly_path)

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

        # PNG поиск
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

        result = {
            "success": True,
            "input_file": os.path.basename(xml_path),
            "output_files": [
                {
                    "path": pngs[0],
                    "name": os.path.basename(pngs[0]),
                    "url": f"/outputs/{os.path.basename(pngs[0])}",
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






