#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore")

import sys
import json
import os
import subprocess
from PIL import Image
import xml.etree.ElementTree as ET

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

# === КРИТИЧЕСКОЕ: заставляем music21 использовать старый форматтер ===
env = environment.Environment()
env['lilypondVersion'] = '2.18.0'


# ---------------------------------------------------------
# NORMALIZATION OF MUSICXML
# ---------------------------------------------------------
def normalize_musicxml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Удаляем namespace
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    # 1) Удаляем вложенные <voice> внутри <note>
    for note in root.findall(".//note"):
        voices = note.findall("voice")
        if len(voices) > 1:
            for v in voices[1:]:
                note.remove(v)

    # 2) Удаляем вложенные <measure> внутри <measure>
    for measure in root.findall(".//measure"):
        nested = measure.findall("measure")
        for m in nested:
            measure.remove(m)

    # 3) Удаляем пустые ноты
    for measure in root.findall(".//measure"):
        for note in list(measure):
            if note.tag == "note":
                if note.find("pitch") is None and note.find("rest") is None:
                    measure.remove(note)

    # 4) Чистим backup/forward
    for measure in root.findall(".//measure"):
        children = list(measure)
        cleaned = []
        skip = False

        for i, child in enumerate(children):
            if skip:
                skip = False
                continue

            if child.tag in ("backup", "forward"):
                if i + 1 < len(children) and children[i+1].tag in ("backup", "forward"):
                    skip = False
                    continue

            cleaned.append(child)

        measure[:] = cleaned

    # 5) Удаляем вложенные <part> внутри <part>
    for part in root.findall(".//part"):
        nested = part.findall("part")
        for p in nested:
            part.remove(p)

    normalized_path = xml_path.replace(".musicxml", "_normalized.musicxml")
    tree.write(normalized_path, encoding="utf-8", xml_declaration=True)
    return normalized_path


# ---------------------------------------------------------
# CHORD SIMPLIFICATION
# ---------------------------------------------------------
def simplify_chord(ch):
    pitches = sorted({p.nameWithOctave for p in ch.pitches})
    new_ch = chord.Chord(pitches)
    new_ch.duration = ch.duration
    return new_ch


# ---------------------------------------------------------
# CLEAN LILYPOND FILE
# ---------------------------------------------------------
def clean_ly_file(path):
    with open(path, "r", encoding="utf-8") as f:
        ly = f.read()

    ly = ly.replace("\\RemoveEmptyStaffContext", "")
    ly = ly.replace("#'direction", "direction")
    ly = ly.replace("<<", "< <")
    ly = ly.replace(">>", "> >")

    with open(path, "w", encoding="utf-8") as f:
        f.write(ly)


# ---------------------------------------------------------
# MAIN PROCESSING
# ---------------------------------------------------------
def process_file(xml_path, semitones=-2):
    try:
        log(f"Нормализуем MusicXML: {xml_path}")
        xml_path = normalize_musicxml(xml_path)

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

        base = os.path.splitext(os.path.basename(xml_path))[0].replace("_normalized", "")
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








