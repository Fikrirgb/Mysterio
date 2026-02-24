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
    'Elf': {'desc': 'Mahir magi, lebih beruntung di Lembah Scarnhorst', 'nyawa': 90, 'energi': 80, 'dodge_chance': 0.50, 'lembah_bonus': 0.10, 'gunung_bonus': 0.00},
    'Dwarf': {'desc': 'Tahan banting di Gunung Gneissenau', 'nyawa': 110, 'energi': 60, 'dodge_chance': 0.30, 'lembah_bonus': 0.00, 'gunung_bonus': 0.12},
    'Human': {'desc': 'Serba bisa', 'nyawa': 100, 'energi': 70, 'dodge_chance': 0.40, 'lembah_bonus': 0.05, 'gunung_bonus': 0.05},
    'Orc': {'desc': 'Kuat tapi kurang gesit', 'nyawa': 120, 'energi': 50, 'dodge_chance': 0.25, 'lembah_bonus': -0.05, 'gunung_bonus': 0.08},
    'Goblin': {'desc': 'Lincah dan licik', 'nyawa': 80, 'energi': 100, 'dodge_chance': 0.60, 'lembah_bonus': 0.08, 'gunung_bonus': -0.02},
    'Giant': {'desc': 'Raksasa kuat dengan nyawa besar, kurang gesit', 'nyawa': 140, 'energi': 40, 'dodge_chance': 0.15, 'lembah_bonus': -0.05, 'gunung_bonus': 0.15},
}


# Class definitions: description, nyawa bonus, path bonuses, and race synergies
CLASSES = {
    'Knight': {'desc': 'Prajurit seimbang, memiliki pertahanan baik', 'nyawa_bonus': 10, 'dodge_bonus': 0.10, 'lembah_bonus': 0.05, 'gunung_bonus': 0.03, 'race_bonuses': {'Human': 0.03, 'Dwarf': 0.02}},
    'Barbar': {'desc': 'Serangan kuat, cepat marah', 'nyawa_bonus': 20, 'dodge_bonus': -0.10, 'lembah_bonus': -0.02, 'gunung_bonus': 0.08, 'race_bonuses': {'Orc': 0.05, 'Giant': 0.04}},
    'Mage': {'desc': 'Pengguna sihir, manipulasi peluang', 'nyawa_bonus': -10, 'dodge_bonus': 0.15, 'lembah_bonus': 0.12, 'gunung_bonus': -0.03, 'race_bonuses': {'Elf': 0.06}},
    'Assassin': {'desc': 'Lincah, peluang kritis tinggi', 'nyawa_bonus': -5, 'dodge_bonus': 0.25, 'lembah_bonus': 0.06, 'gunung_bonus': 0.02, 'race_bonuses': {'Goblin': 0.05}},
    'Tank': {'desc': 'Pelindung, sangat tahan banting', 'nyawa_bonus': 30, 'dodge_bonus': 0.05, 'lembah_bonus': -0.03, 'gunung_bonus': 0.10, 'race_bonuses': {'Dwarf': 0.04, 'Giant': 0.03}},
    'Archer': {'desc': 'Penembak jitu, akurasi tinggi dari jarak jauh', 'nyawa_bonus': 0, 'dodge_bonus': 0.20, 'lembah_bonus': 0.04, 'gunung_bonus': 0.01, 'race_bonuses': {'Elf': 0.04}},
}


# Enemy definitions for left path (Kiri) - lebih banyak musuh biasa
LEFT_PATH_ENEMIES = {
    'Skeleton Guard': {'nyawa': 30, 'damage': 15, 'deskripsi': 'Penjaga tulang belulang yang berkeliling di koridor'},
    'Prison Rat': {'nyawa': 15, 'damage': 5, 'deskripsi': 'Tikus penjara raksasa yang lapar'},
    'Zombie Convict': {'nyawa': 40, 'damage': 20, 'deskripsi': 'Tahanan yang telah dimutasikan menjadi undead'},
    'Iron Golem': {'nyawa': 50, 'damage': 25, 'deskripsi': 'Golem besi yang menjaga harta karun'},
    'Wraith Guard': {'nyawa': 35, 'damage': 18, 'deskripsi': 'Roh penjaga yang terperangkap di lorong'},
}

LEFT_PATH_BOSS = {
    'Shadow Warden': {
        'nyawa': 100,
        'damage': 30,
        'deskripsi': 'Komandan bayangan penjara ini, makhluk yang dibuat dari kegelapan itu sendiri'
    }
}

# Enemy definitions for right path (Kanan) - lebih kuat dan sengit
RIGHT_PATH_ENEMIES = {
    'Mutant Beast': {'nyawa': 45, 'damage': 25, 'deskripsi': 'Makhluk bermutasi dari eksperimen ilmuwan'},
    'Guard Beast': {'nyawa': 50, 'damage': 28, 'deskripsi': 'Anjing penjara yang ditingkatkan dengan sihir'},
    'Armored Sentinel': {'nyawa': 60, 'damage': 30, 'deskripsi': 'Sentinela bersenjata yang menjaga kedalaman'},
    'Blood Knight': {'nyawa': 70, 'damage': 35, 'deskripsi': 'Ksatria yang telah dikutuk dan dipenuhi kemarahan'},
}

RIGHT_PATH_BOSS = {
    'The Chained One': {
        'nyawa': 150,
        'damage': 40,
        'deskripsi': 'Sesuatu yang sangat kuat ditahan dengan rantai di kedalaman penjara. Kini rantai itu hancur dan ia ingin balas dendam.'
    }
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


def explore_dungeon(name, path, nama_path, nyawa, energi, race, class_name, enemies_dict, boss_dict):
    """Explore a dungeon path with enemies and a boss at the end. Supports attack and dodge actions."""
    
    path_intro = f"Kamu memasuki {nama_path}..."
    dramatic_print(path_intro)
    time.sleep(0.5)
    
    # Calculate dodge chance based on race and class
    base_dodge_chance = RACES.get(race, {}).get('dodge_chance', 0.3)
    class_dodge_bonus = CLASSES.get(class_name, {}).get('dodge_bonus', 0)
    player_dodge_chance = max(0.0, min(1.0, base_dodge_chance + class_dodge_bonus))
    
    # Encounter 2-3 random enemies
    num_encounters = random.randint(2, 3)
    
    for encounter_num in range(1, num_encounters + 1):
        if nyawa <= 0:
            break
            
        # Pick random enemy
        enemy_name = random.choice(list(enemies_dict.keys()))
        enemy = enemies_dict[enemy_name]
        enemy_nyawa = enemy['nyawa']
        enemy_damage = enemy['damage']
        
        # Battle message
        battle_msg = (
            f"Langkah {encounter_num}: {enemy_name} muncul!\n"
            f"{enemy['deskripsi']}\n"
            f"Nyawa musuh: {enemy_nyawa}"
        )
        dramatic_print(battle_msg)
        time.sleep(0.3)
        
        # Battle: player and enemy exchange damage
        player_damage = random.randint(15, 30)
        
        while enemy_nyawa > 0 and nyawa > 0:
            # Player turn - choose action
            status_msg = f"Nyawa: {nyawa} | Energi: {energi} | Nyawa musuh: {enemy_nyawa}"
            dramatic_print(status_msg, width=60, delay_char=0.001)
            
            action = show_menu(
                "Pilih aksi:",
                ["Serang", "Dodge (Hemat Energi)"]
            )
            
            if "Serang" in action:
                # Attack action
                damage = player_damage + random.randint(-5, 5)
                enemy_nyawa -= damage
                
                attack_msg = f"Kamu menyerang! Damage: {damage}. Nyawa musuh tersisa: {max(0, enemy_nyawa)}"
                dramatic_print(attack_msg, width=60, delay_char=0.002)
                time.sleep(0.2)
                
            else:  # Dodge action
                if energi < 15:
                    dodge_fail = "Energi mu tidak cukup untuk dodge!"
                    dramatic_print(dodge_fail, width=60, delay_char=0.002)
                    time.sleep(0.2)
                else:
                    dodge_roll = random.random()
                    if dodge_roll < player_dodge_chance:
                        dodge_success = f"Kamu berhasil dodge! {enemy_name} menyerang kekosongan!"
                        dramatic_print(dodge_success, width=60, delay_char=0.002)
                        energi -= 15
                        time.sleep(0.2)
                        continue  # Skip enemy attack this turn
                    else:
                        dodge_fail = f"Dodge mu gagal! Kamu terkena serangan penuh!"
                        dramatic_print(dodge_fail, width=60, delay_char=0.002)
                        energi -= 15
                        time.sleep(0.2)
            
            if enemy_nyawa <= 0:
                break
            
            # Enemy attack
            damage = enemy_damage + random.randint(-3, 3)
            nyawa -= damage
            
            hit_msg = f"{enemy_name} menyerang! Damage: {damage}. Nyawa mu tersisa: {max(0, nyawa)}"
            dramatic_print(hit_msg, width=60, delay_char=0.002)
            time.sleep(0.2)
            
            # Regenerate small amount of energy after each exchange
            energi = min(energi + 5, RACES.get(race, {}).get('energi', 100))
        
        if enemy_nyawa <= 0:
            victory_msg = f"{enemy_name} terkalahkan! Kamu menemukan sedikit emas dan potion."
            dramatic_print(victory_msg)
            nyawa += random.randint(5, 15)  # Small healing
            energi = max(energi, 30)  # Restore some energy after victory
            time.sleep(0.3)
        else:
            defeat_msg = "Kamu tidak dapat terus berjuang lagi..."
            dramatic_print(defeat_msg)
            break
    
    if nyawa <= 0:
        return nyawa, energi
    
    # Boss encounter
    print("\n")
    boss_name = list(boss_dict.keys())[0]
    boss = boss_dict[boss_name]
    boss_nyawa = boss['nyawa']
    boss_damage = boss['damage']
    
    boss_intro = (
        f"\n{'='*60}\n"
        f"AKHIR JALUR: PERTARUNGAN BOSS FINAL!\n"
        f"{'='*60}\n\n"
        f"{boss_name} muncul di depanmu!\n"
        f"{boss['deskripsi']}\n"
        f"Nyawa musuh: {boss_nyawa}"
    )
    dramatic_print(boss_intro)
    time.sleep(1)
    
    # Boss battle
    player_damage = random.randint(20, 35)
    
    while boss_nyawa > 0 and nyawa > 0:
        # Player turn - choose action
        status_msg = f"Nyawa: {nyawa} | Energi: {energi} | Nyawa Boss: {boss_nyawa}"
        dramatic_print(status_msg, width=60, delay_char=0.001)
        
        action = show_menu(
            "Pilih aksi melawan BOSS:",
            ["Serang", "Dodge (Hemat Energi)"]
        )
        
        if "Serang" in action:
            # Attack action
            damage = player_damage + random.randint(-10, 10)
            boss_nyawa -= damage
            
            attack_msg = f"Kamu menyerang BOSS! Damage: {damage}. Nyawa boss tersisa: {max(0, boss_nyawa)}"
            dramatic_print(attack_msg, width=60, delay_char=0.002)
            time.sleep(0.2)
            
        else:  # Dodge action
            if energi < 15:
                dodge_fail = "Energi mu tidak cukup untuk dodge!"
                dramatic_print(dodge_fail, width=60, delay_char=0.002)
                time.sleep(0.2)
            else:
                dodge_roll = random.random()
                # Boss is harder to dodge against
                boss_dodge_chance = player_dodge_chance * 0.7
                if dodge_roll < boss_dodge_chance:
                    dodge_success = f"Kamu berhasil dodge serangan BOSS!"
                    dramatic_print(dodge_success, width=60, delay_char=0.002)
                    energi -= 15
                    time.sleep(0.2)
                    continue  # Skip boss attack this turn
                else:
                    dodge_fail = f"BOSS meluncurkan serangan yang tidak bisa dihindari sepenuhnya!"
                    dramatic_print(dodge_fail, width=60, delay_char=0.002)
                    energi -= 15
                    time.sleep(0.2)
        
        if boss_nyawa <= 0:
            break
        
        # Boss attack (stronger)
        damage = boss_damage + random.randint(-5, 5)
        nyawa -= damage
        
        hit_msg = f"{boss_name} menyerang balik dengan KEKUATAN PENUH! Damage: {damage}. Nyawa mu: {max(0, nyawa)}"
        dramatic_print(hit_msg, width=60, delay_char=0.002)
        time.sleep(0.2)
        
        # Regenerate energy
        energi = min(energi + 5, RACES.get(race, {}).get('energi', 100))
    
    print("\n")
    if boss_nyawa <= 0:
        victory_msg = (
            f"{boss_name} JATUH!\n"
            f"Kamu telah mengalahkan boss! Kebebasan terasa semakin dekat...\n"
            f"Nyawa tersisa: {nyawa} | Energi: {energi}"
        )
        dramatic_print(victory_msg)
        print(FG_CYAN + SWORD_ART + RESET)
    else:
        defeat_msg = "Kamu kalah... Kegelapan penjara menelan kesadaranmu..."
        dramatic_print(defeat_msg)
        print(FG_CYAN + SKULL_ART + RESET)
    
    return nyawa, energi


def opening_sequence(name, race, class_name):
    """Display the opening sequence with waking up inside the experimental tube already transformed."""
    clear_screen()
    
    # First scene: waking up inside the tube
    scene1 = (
        f"Matamu terbuka dengan susah di dalam kegelapan. Semuanya gelap sekali, hanya cahaya "
        f"hijau pucat yang menembus kegelapan itu. Kepala mu sakit luar biasa.\n"
        f"Kamu mencoba menggerakkan tubuh, tapi terasa ada ribuan jarum menusuk di setiap otol mu.\n"
        f"Perlahan, kesadaran kembali... dan kamu menyadari sesuatu BERBEDA tentang diri mu sekarang."
    )
    dramatic_print(scene1)
    time.sleep(1)
    
    # Second scene: realizing the transformation
    scene2 = (
        f"Cahaya hijau meningkat. Mata mu menyesuaikan. Kamu menyadari kamu TERJEBAK di dalam "
        f"tabung kaca eksperimen yang besar, penuh dengan cairan kuning dan merah yang berbau aneh.\n"
        f"Tetapi tubuh mu... ia berbeda sekarang. Kamu adalah {race}!\n"
        f"Elektroda tertanam di kulit mu. Pipa-pipa plastik menghisap zat kimia. "
        f"Kaca di sekitar mu terasa basah dan dingin.\n"
        f"Di luar tabung, laboratorium yang gelap berkembang. Sederet mesin berdetak dengan ritme yang aneh."
    )
    dramatic_print(scene2)
    time.sleep(1)
    
    # Third scene: realization and determination
    scene3 = (
        f"Kilatan ingatan yang mengerikan menyambar pikiranmu. Pertempuran... kekalahan... tubuhmu dibawa ke sini.\n"
        f"Mereka menangkap mu {race}. Mereka ingin tahu kekuatan apa yang ada dalam dirimu. "
        f"Mereka menguji... menguji... menguji tanpa henti di laboratorium penjara bawah tanah ini."
    )
    dramatic_print(scene3)
    time.sleep(1)
    
    # Fourth scene: alarm and opportunity
    scene4 = (
        f"BLIP! BLIP! BLIP!\n"
        f"Sebuah alarm berbunyi keras di kejauhan. Cahaya merah darurat menerangi laboratorium. "
        f"Para ilmuwan bergegas keluar, meninggalkan monitor dan stasiun kerja mereka.\n"
        f"Kesempatan mu. Kesempatan SATU-SATUNYA untuk hidup."
    )
    dramatic_print(scene4)
    time.sleep(0.5)
    
    # Fifth scene: breaking free from the tube
    scene5 = (
        f"Kamu mengambil napas dalam-dalam dengan otot-otot {race} mu yang baru.\n"
        f"Energi {class_name} mengalir dalam darah mu. Kamu adalah pejuang yang dibangkitkan kembali, "
        f"dan TIDAK ADA yang akan menahan mu lagi.\n"
        f"DENGAN SEKALI HENTAKAN, kamu menendang kaca tabung itu dengan SEGENAP TENAGA!"
    )
    dramatic_print(scene5)
    time.sleep(0.3)
    
    print("\n")
    print(FG_CYAN + """
    ╔════════════════════════════════════════╗
    ║         TABUNG KACA PECAH!!!            ║
    ║   Cairan kuning dan merah muncrat!!!    ║
    ║  Kamu terjatuh keluar dari tabung itu!  ║
    ║  Paru-paru mu mengisap udara pertama    ║
    ║         kali sejak lama sekali!         ║
    ╚════════════════════════════════════════╝
    """ + RESET)
    time.sleep(1)
    
    # Sixth scene: transformation after breaking free
    scene6 = (
        "Cairan eksperimen menetes dari tubuh mu. Pipa-pipa plastik copot dengan kasar. "
        "Elektroda tercabut dari kulit mu.\n"
        "Dan kemudian... tubuh mu mulai berubah. Kulit mu megelupas dan berganti. "
        "Otot mu bertanya dengan cara yang baru. Kekuatan yang menakjubkan mengalir dalam vena mu.\n"
        "Eksperimen mereka BERHASIL! Kamu bukan lagi manusia biasa. "
        "Kamu adalah sesuatu yang lebih kuat, lebih misterius."
    )
    dramatic_print(scene6)
    time.sleep(1)
    
    # Seventh scene: escape and journey
    scene7 = (
        "Alarm terus berbunyi. Kamu berlari melalui koridor gelap yang berbau lumut dan karat.\n"
        "Cahaya merah darurat memandu mu ke atas... terus ke atas... "
        "keluar dari laboratorium penjara bawah tanah itu.\n"
        "Akhirnya... kamu keluar ke udara malam yang segar. Kamu BEBAS. "
        "Tapi siapa sebenarnya diri mu sekarang?"
    )
    dramatic_print(scene7)
    time.sleep(1)
    
    # Eighth scene: reaching the prison gate
    print("\n")
    scene8 = (
        f"Kamu berlari menembus hutan gelap, napas mu tersenggal. Suara teriakan penjaga "
        f"menggema di belakang. Mereka mengejar!\n"
        f"Tapi ada sesuatu di depanmu. Sebuah gerbang RAKSASA terbuat dari besi dan batu, "
        f"tertanam di bukit batu yang menjulang tinggi.\n"
        f"Gerbang penjara utama... yang menjadi jalan keluar atau jalan menuju gulma lebih dalam."
    )
    dramatic_print(scene8)
    time.sleep(1)
    
    # Ninth scene: discovering two paths
    scene9 = (
        f"Gerbang terbuka lebar. Kamu masuk melewati pintu logam yang melengking. "
        f"Di belakangmu, suara penjaga semakin dekat.\n"
        f"Tapi di depanmu... ada dua jalan.\n"
        f"Ke KIRI: Lorong sempit yang menghilang ke dalam kegelapan. "
        f"Kamu mendengar suara angin dingin dan derit logam kuno.\n"
        f"Ke KANAN: Jalan yang lebih luas, cahaya hijau aneh bersinar dari kedalaman. "
        f"Tapi kamu bisa mendengar... dentuman... seperti sesuatu yang berat berjalan di sana.\n"
        f"\n"
        f"Pilihan sulit. Tapi kamu harus memilih SEKARANG. Penjaga semakin dekat!"
    )
    dramatic_print(scene9)
    time.sleep(1)
    
    return


def game_utama():
    print("--- MEMULAI PETUALANGAN DIGITAL ---")
    print("\n")
    
    SAVE_FILE = "savegame.json"
    
    # Get or load player name and basic info
    nama = None
    race = None
    class_name = None
    nyawa = 100
    energi = 70  # Default energi
    
    # Check for existing save
    if os.path.exists(SAVE_FILE):
        kont = show_menu("Ditemukan permainan tersimpan. Lanjutkan?", ["Ya", "Tidak"])
        if kont and kont[0].lower() == 'y':
            try:
                with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                nama = data.get('name')
                nyawa = int(data.get('nyawa', 100))
                race = data.get('race')
                class_name = data.get('class')
                if nama and race and class_name:
                    dramatic_print(f"Memuat permainan untuk {nama}. Nyawa: {nyawa}. Ras: {race}. Kelas: {class_name}")
                else:
                    raise Exception("Data save tidak lengkap")
            except Exception:
                dramatic_print("Gagal memuat permainan. Memulai permainan baru.")
                nama = None
                race = None
                class_name = None
                nyawa = 100
        else:
            # Start new game and remove old save
            try:
                os.remove(SAVE_FILE)
            except Exception:
                pass
    
    # Get player name if not loaded
    if not nama:
        nama = input("Siapa namamu? ").strip() or "Pemain"
        print()
    
    # Race selection (if not loaded)
    if not race:
        intro_text = (
            f"Sebelum terjatuh ke kegelapan laboratorium bawah tanah itu, saat roh mu masih "
            f"terikat dengan dunia magis... kamu memiliki kesempatan untuk memilih "
            f"bentuk baru yang akan menerima transformasi eksperimen ilmuwan jahat itu.\n"
            f"{nama}, apa ras yang akan menjadi esensi mu?"
        )
        dramatic_print(intro_text)
        print()
        
        choices = [f"{r} - {RACES[r]['desc']}" for r in RACES]
        picked = show_menu("Pilih rasmu:", choices)
        race = picked.split(' - ')[0]
        nyawa = RACES.get(race, {}).get('nyawa', nyawa)
        energi = RACES.get(race, {}).get('energi', 70)
        
        race_awakening = (
            f"Ya... rasmu adalah {race}.\n"
            f"{RACES.get(race,{}).get('desc','')}\n"
            f"Nyawa dasarmu: {nyawa} | Energi dasarmu: {energi}"
        )
        dramatic_print(race_awakening)
        print()
    
    # Class selection (if not loaded)
    if not class_name:
        class_intro = (
            f"Dan dalam momen terakhir sebelum kesadaran ditarik ke abyss, "
            f"kamu merasakan takdir mu membentuk... Apa peranmu? Apa jalan yang akan kamu ambil "
            f"dalam kehidupan yang akan datang?"
        )
        dramatic_print(class_intro)
        print()
        
        class_choices = [f"{c} - {CLASSES[c]['desc']}" for c in CLASSES]
        picked_c = show_menu("Pilih kelasmu:", class_choices)
        class_name = picked_c.split(' - ')[0]
        nyawa = nyawa + CLASSES.get(class_name, {}).get('nyawa_bonus', 0)
        
        class_awakening = (
            f"Kamu adalah {class_name}.\n"
            f"{CLASSES.get(class_name,{}).get('desc','')}\n"
            f"Total Nyawa mu: {nyawa} | Total Energi mu: {energi}"
        )
        dramatic_print(class_awakening)
        print()
    
    # Now the transformation is complete, show the opening sequence
    time.sleep(1)
    opening_sequence(nama, race, class_name)
    
    print("\n")
    
    # Main game loop - choose paths and explore dungeons
    while True:
        # Prompt player for path choice
        path_choice = show_menu(
            f"{nama}, pilih jalur mana yang ingin kamu masuki?",
            ["Kiri - Lorong Kegelapan", "Kanan - Medan Pertarungan"]
        )
        
        print("\n")
        
        if "Kiri" in path_choice:
            # Left path
            nyawa, energi = explore_dungeon(
                nama, 
                "left",
                "Lorong Kegelapan (Kiri)",
                nyawa,
                energi,
                race,
                class_name,
                LEFT_PATH_ENEMIES,
                LEFT_PATH_BOSS
            )
        else:
            # Right path
            nyawa, energi = explore_dungeon(
                nama,
                "right", 
                "Medan Pertarungan (Kanan)",
                nyawa,
                energi,
                race,
                class_name,
                RIGHT_PATH_ENEMIES,
                RIGHT_PATH_BOSS
            )
        
        print("\n")
        
        # Check if player is still alive
        if nyawa <= 0:
            dramatic_print(f"{nama}, nyawamu habis. Petualanganmu berakhir di penjara gelap ini.")
            # Remove save
            try:
                if os.path.exists(SAVE_FILE):
                    os.remove(SAVE_FILE)
            except Exception:
                pass
            break
        
        # Offer to save after path completion
        simpan = show_menu("Simpan permainan?", ["Ya", "Tidak"])
        if simpan and simpan[0].lower() == 'y':
            try:
                with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'name': nama, 'nyawa': nyawa, 'race': race, 'class': class_name}, f)
                dramatic_print(f"Permainan disimpan ke {SAVE_FILE}.")
            except Exception:
                dramatic_print("Gagal menyimpan permainan.")
        
        print("\n")
        
        # Ask if player wants to continue
        lanjut = show_menu("Apakah kamu ingin mengeksplorasi jalur yang lain atau melanjutkan pencarian kebebasan?", ["Lanjutkan Petualangan", "Keluar Permainan"])
        if lanjut and "Keluar" in lanjut:
            dramatic_print(f"Terima kasih telah bermain, {nama}. Sampai jumpa!")
            break


if __name__ == "__main__":
    game_utama()