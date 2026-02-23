import time
import random
import json
import os
import sys
import textwrap

# ANSI colors for simple styling
CSI = "\x1b["
RESET = CSI + "0m"
FG_CYAN = CSI + "36m"
FG_WHITE = CSI + "97m"
BG_BLUE = CSI + "44m"


SWORD_ART = r"""
       />
 (===[===>
       \
"""

SKULL_ART = r"""
       .-.
      (o o)
      | O \
       \   \
        `---'
"""


# Race definitions: description, base nyawa, and path bonuses
RACES = {
    'Elf': {'desc': 'Mahir magi, lebih beruntung di Lembah Scarnhorst', 'nyawa': 90, 'lembah_bonus': 0.10, 'gunung_bonus': 0.00},
    'Dwarf': {'desc': 'Tahan banting di Gunung Gneissenau', 'nyawa': 110, 'lembah_bonus': 0.00, 'gunung_bonus': 0.12},
    'Human': {'desc': 'Serba bisa', 'nyawa': 100, 'lembah_bonus': 0.05, 'gunung_bonus': 0.05},
    'Orc': {'desc': 'Kuat tapi kurang gesit', 'nyawa': 120, 'lembah_bonus': -0.05, 'gunung_bonus': 0.08},
    'Goblin': {'desc': 'Lincah dan licik', 'nyawa': 80, 'lembah_bonus': 0.08, 'gunung_bonus': -0.02},
    'Giant': {'desc': 'Raksasa kuat dengan nyawa besar, kurang gesit', 'nyawa': 140, 'lembah_bonus': -0.05, 'gunung_bonus': 0.15},
}


# Class definitions: description, nyawa bonus, path bonuses, and race synergies
CLASSES = {
    'Knight': {'desc': 'Prajurit seimbang, memiliki pertahanan baik', 'nyawa_bonus': 10, 'lembah_bonus': 0.05, 'gunung_bonus': 0.03, 'race_bonuses': {'Human': 0.03, 'Dwarf': 0.02}},
    'Barbar': {'desc': 'Serangan kuat, cepat marah', 'nyawa_bonus': 20, 'lembah_bonus': -0.02, 'gunung_bonus': 0.08, 'race_bonuses': {'Orc': 0.05, 'Giant': 0.04}},
    'Mage': {'desc': 'Pengguna sihir, manipulasi peluang', 'nyawa_bonus': -10, 'lembah_bonus': 0.12, 'gunung_bonus': -0.03, 'race_bonuses': {'Elf': 0.06}},
    'Assassin': {'desc': 'Lincah, peluang kritis tinggi', 'nyawa_bonus': -5, 'lembah_bonus': 0.06, 'gunung_bonus': 0.02, 'race_bonuses': {'Goblin': 0.05}},
    'Tank': {'desc': 'Pelindung, sangat tahan banting', 'nyawa_bonus': 30, 'lembah_bonus': -0.03, 'gunung_bonus': 0.10, 'race_bonuses': {'Dwarf': 0.04, 'Giant': 0.03}},
    'Archer': {'desc': 'Penembak jitu, akurasi tinggi dari jarak jauh', 'nyawa_bonus': 0, 'lembah_bonus': 0.04, 'gunung_bonus': 0.01, 'race_bonuses': {'Elf': 0.04}},
}


def dramatic_print(text):
    ui_print(text)


def clear_screen():
    print('\033[2J\033[H', end='')


def ui_print(text, width=60, delay_char=0.006):
    """Print text inside a boxed dialog with a typewriter effect."""
    lines = []
    for paragraph in str(text).split('\n'):
        wrapped = textwrap.wrap(paragraph, width=width)
        if not wrapped:
            lines.append('')
        else:
            lines.extend(wrapped)

    # draw box
    print(FG_CYAN + '+' + '-' * (width + 2) + '+' + RESET)
    for line in lines:
        # typewriter effect per line
        sys.stdout.write(FG_CYAN + '| ' + RESET)
        for ch in line:
            sys.stdout.write(FG_WHITE + ch + RESET)
            sys.stdout.flush()
            time.sleep(delay_char)
        # padding
        pad = width - len(line)
        sys.stdout.write(' ' * pad)
        sys.stdout.write(FG_CYAN + ' |\n' + RESET)
    print(FG_CYAN + '+' + '-' * (width + 2) + '+' + RESET)
    time.sleep(0.25)


def show_menu(prompt, choices):
    """Show a vertical menu inside a box and return the chosen item (string).

    Choices can be a list of strings; user selects by number.
    """
    width = max(len(prompt), max((len(c) for c in choices), default=0)) + 4
    wrapped = textwrap.wrap(prompt, width=width - 4)
    print(FG_CYAN + '+' + '-' * (width) + '+' + RESET)
    for line in wrapped:
        print(FG_CYAN + '| ' + RESET + line.ljust(width - 2) + FG_CYAN + ' |' + RESET)
    print(FG_CYAN + '|' + ' ' * (width) + '|' + RESET)
    for i, c in enumerate(choices, start=1):
        entry = f"{i}. {c}"
        print(FG_CYAN + '| ' + RESET + entry.ljust(width - 2) + FG_CYAN + ' |' + RESET)
    print(FG_CYAN + '+' + '-' * (width) + '+' + RESET)

    while True:
        s = input('Pilih nomor: ').strip()
        if s.isdigit():
            idx = int(s) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        print('Pilihan tidak valid, coba lagi.')


def play(choice=None, name="Pemain", nyawa=100, race=None, class_name=None):
    """Execute a single path choice.

    If `choice` is None this function will prompt the user (interactive mode).
    Returns tuple (message, nyawa_after, success_bool).
    """
    interactive = choice is None

    if interactive:
        choice = show_menu("Pilih jalur:", ["Lembah Scarnhorst", "Gunung Gneissenau"])

    raw = (choice or "").strip().lower()

    # map synonyms
    if raw in ("lembah scarnhorst", "lembah", "scarnhorst", "kiri", "ke kiri"):
        path = "lembah"
        success_prob = 0.75
    elif raw in ("gunung gneissenau", "gunung", "gneissenau", "kanan", "ke kanan"):
        path = "gunung"
        success_prob = 0.45
    else:
        # invalid choice counts as a mistake
        nyawa -= 20
        msg = f"{name}, pilihan tidak dikenali. Kamu kehilangan 20 nyawa. Nyawa tersisa: {nyawa}."
        if interactive:
            dramatic_print(msg)
        return msg, nyawa, False

    # randomness element
    roll = random.random()

    # apply race modifiers if provided
    if race in RACES:
        r = RACES[race]
        if path == 'lembah':
            success_prob = max(0.0, success_prob + r.get('lembah_bonus', 0))
        else:
            success_prob = max(0.0, success_prob + r.get('gunung_bonus', 0))

    # apply class modifiers if provided
    if class_name in CLASSES:
        c = CLASSES[class_name]
        if path == 'lembah':
            success_prob = max(0.0, success_prob + c.get('lembah_bonus', 0))
        else:
            success_prob = max(0.0, success_prob + c.get('gunung_bonus', 0))
        # class-race synergy
        race_buffs = c.get('race_bonuses', {})
        if race and race in race_buffs:
            success_prob = max(0.0, success_prob + race_buffs[race])

    if roll < success_prob:
        msg = (
            f"{name}, kamu menavigasi {( 'Lembah Scarnhorst' if path=='lembah' else 'Gunung Gneissenau')} dengan cerdik!\n"
            "Kamu menemukan sebuah artefak yang akan membantumu di petualangan selanjutnya."
        )
        if interactive:
            dramatic_print(msg)
            dramatic_print(SWORD_ART)
        return msg, nyawa, True
    else:
        nyawa -= 20
        msg = (
            f"{name}, sayang sekali. Jalur itu penuh jebakan dan bug. Nyawa berkurang 20. Nyawa tersisa: {nyawa}."
        )
        if interactive:
            dramatic_print(msg)
            dramatic_print(SKULL_ART)
        return msg, nyawa, False


def game_utama():
    print("--- MEMULAI PETUALANGAN DIGITAL ---")
    # Opening narrative
    intro = (
        "Malam Tuan, anda telah dimasukkan ke dalam penjara yang jauh di dalam tanah "
        "dikarenakan pasukan yang anda pimpin mengalami kekalahan dan tubuh anda "
        "dijadikan sebagai bahan penelitian di laboratorium penjara bawah tanah musuh."
    )
    dramatic_print(intro)
    SAVE_FILE = "savegame.json"

    # check for existing save
    if os.path.exists(SAVE_FILE):
        kont = show_menu("Ditemukan permainan tersimpan. Lanjutkan?", ["Ya", "Tidak"])
        if kont and kont[0].lower() == 'y':
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                nama = data.get('name')
                if not nama:
                    nama = input("Siapa namamu? ").strip() or "Pemain"
                nyawa = int(data.get('nyawa', 100))
                race = data.get('race')
                class_name = data.get('class')
                dramatic_print(f"Memuat permainan untuk {nama}. Nyawa: {nyawa}. Ras: {race if race else 'Belum dipilih'}. Kelas: {class_name if class_name else 'Belum dipilih'}")
            except Exception:
                dramatic_print("Gagal memuat permainan. Memulai permainan baru.")
                nama = input("Siapa namamu? ").strip() or "Pemain"
                nyawa = 100
                race = None
        else:
            # start new and remove old save
            try:
                os.remove(SAVE_FILE)
            except Exception:
                pass
            nama = input("Siapa namamu? ").strip() or "Pemain"
            nyawa = 100
            race = None
    else:
        nama = input("Siapa namamu? ").strip() or "Pemain"
        nyawa = 100
        race = None

    # Race selection (if not loaded)
    if not race:
        choices = [f"{r} - {RACES[r]['desc']}" for r in RACES]
        picked = show_menu("Pilih rasmu:", choices)
        # extract race key from picked string
        race = picked.split(' - ')[0]
        # set initial nyawa based on race (unless loaded)
        nyawa = RACES.get(race, {}).get('nyawa', nyawa)
        dramatic_print(f"Kamu memilih ras {race}. {RACES.get(race,{}).get('desc','')}")

    # Class selection
    class_name = None
    if not class_name:
        class_choices = [f"{c} - {CLASSES[c]['desc']}" for c in CLASSES]
        picked_c = show_menu("Pilih kelasmu:", class_choices)
        class_name = picked_c.split(' - ')[0]
        # apply class nyawa bonus to starting nyawa
        nyawa = nyawa + CLASSES.get(class_name, {}).get('nyawa_bonus', 0)
        dramatic_print(f"Kamu memilih kelas {class_name}. {CLASSES.get(class_name,{}).get('desc','')}")

    while True:
        dramatic_print(f"Selamat datang, {nama}! Nyawa kamu: {nyawa}.")

        # play until win or out of nyawa
        while nyawa > 0:
            msg, nyawa, success = play(choice=None, name=nama, nyawa=nyawa, race=race, class_name=class_name)
            if success:
                dramatic_print("Kamu menang pada jalur ini!")
            if nyawa <= 0:
                dramatic_print("Nyawamu habis. Kamu gugur di perjalanan.")
                dramatic_print(SKULL_ART)

            # offer to save after each round if player still has nyawa
            if nyawa > 0:
                simpan = show_menu("Simpan permainan?", ["Ya", "Tidak"])
                if simpan and simpan[0].lower() == 'y':
                    try:
                        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                            json.dump({'name': nama, 'nyawa': nyawa, 'race': race, 'class': class_name}, f)
                        dramatic_print(f"Permainan disimpan ke {SAVE_FILE}.")
                    except Exception:
                        dramatic_print("Gagal menyimpan permainan.")
            else:
                # if player died, remove any save
                try:
                    if os.path.exists(SAVE_FILE):
                        os.remove(SAVE_FILE)
                except Exception:
                    pass

            if nyawa > 0 and success:
                # ask if player wants to continue the same session or end
                lanjut = show_menu("Lanjutkan petualangan?", ["Ya", "Tidak"])
                if not (lanjut and lanjut[0].lower() == 'y'):
                    break
            if nyawa <= 0:
                break

        again = show_menu("Main lagi?", ["Ya", "Tidak"])
        if not (again and again[0].lower() == 'y'):
            dramatic_print("Terima kasih telah bermain. Sampai jumpa!")
            break


if __name__ == "__main__":
    game_utama()