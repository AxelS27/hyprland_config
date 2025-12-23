#!/usr/bin/env python3
import json, sys, pathlib, subprocess

BASE = pathlib.Path("~/.config/lthemes").expanduser()
CONFIG = BASE / "lthemes-config.json"
CURRENT_CSS = BASE / "current-theme.css"
CURRENT_CONF = BASE / "current-theme.conf"
CURRENT_RASI = BASE / "current-theme.rasi"
ROFI_THEME = "~/.config/rofi/launchers/type-2/style-1.rasi"
ROFI_WALL_THEME = "~/.config/rofi/launchers/type-6/style-9.rasi"

def die(msg):
    print(f"[LThemes] {msg}")
    sys.exit(1)

def load_config():
    if CONFIG.exists():
        return json.loads(CONFIG.read_text())
    return {"current": None}

def save_config(theme, wallpaper=None):
    data = {"current": theme}
    if wallpaper:
        data["wallpaper-path"] = str(wallpaper)
    else:
        old = load_config()
        if "wallpaper-path" in old:
            data["wallpaper-path"] = old["wallpaper-path"]
    CONFIG.write_text(json.dumps(data, indent=2))

def themes():
    return sorted([d.name for d in BASE.iterdir() if d.is_dir() and (d / "colors.css").exists()])

def generate_currentTheme(theme):
    css  = BASE / theme / "colors.css"
    conf = BASE / theme / "colors.conf"
    rasi = BASE / theme / "colors.rasi"
    CURRENT_CSS.write_text(f'@import url("{css}");\n')
    CURRENT_CONF.write_text(f"source = {conf}\n")
    wallpaper = str(load_config().get("wallpaper-path", ""))
    rasi_content = f'@import "{rasi}"\n\n'
    if wallpaper:
        rasi_content += f'imagebox {{\n    background-image: url("{wallpaper}");\n}}\n'
    CURRENT_RASI.write_text(rasi_content)

def cmd_list():
    for t in themes():
        print(t)

def cmd_get():
    config = load_config()
    if config["current"]:
        print(config["current"])
    else:
        die("No active theme")

def cmd_set(theme):
    if theme not in themes():
        die(f"Theme not found: {theme}")
    wallpaper_select(theme)

def rofi_select(options, prompt="", theme_file=ROFI_THEME):
    current = load_config().get("current")
    rofi_input = "\n".join(f"{t} *" if t==current else t for t in options)
    try:
        result = subprocess.run(
            ["rofi", "-dmenu", "-theme", theme_file, "-p", prompt],
            input=rofi_input.encode(),
            capture_output=True
        )
        choice = result.stdout.decode().strip().rstrip(" *")
        if choice in options:
            return choice
        return None
    except FileNotFoundError:
        die("Rofi not found")

def wallpaper_select(theme):
    WALL_DIR = BASE / theme / "wallpapers"
    if not WALL_DIR.exists():
        save_config(theme)
        generate_currentTheme(theme)
        return
    options = [f for f in WALL_DIR.iterdir() if f.is_file()]
    if not options:
        save_config(theme)
        generate_currentTheme(theme)
        return
    current_wallpaper = str(load_config().get("wallpaper-path", ""))
    rofi_input = ""
    for f in options:
        mark = " *" if str(f) == current_wallpaper else ""
        rofi_input += f"{f.name}{mark}\0icon\x1f{f}\n"
    result = subprocess.run(
        ["rofi", "-dmenu", "-theme", ROFI_WALL_THEME, "-p", "Select wallpaper"],
        input=rofi_input.encode(),
        capture_output=True
    )
    choice = result.stdout.decode().strip()
    selected = next((f for f in options if f.name == choice), None)
    if selected:
        save_config(theme, selected)
        generate_currentTheme(theme)
        subprocess.run([
            "swww", "img",
            str(selected),
            "--transition-type", "any",
            "--transition-step", "20",
            "--transition-duration", "3"
        ])
        try:
            reload_script = pathlib.Path("~/.config/lthemes/scripts/reload.sh").expanduser()
            subprocess.run([str(reload_script)], check=True)
        except Exception as e:
            print(f"[LThemes] Failed to run reload.sh: {e}")
    else:
        save_config(theme)
        generate_currentTheme(theme)

def cmd_select():
    t = rofi_select(themes())
    if t:
        cmd_set(t)
    else:
        die("No theme selected")

if len(sys.argv) < 2:
    cmd_select()
else:
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
    elif cmd == "get":
        cmd_get()
    elif cmd == "set":
        if len(sys.argv) < 3:
            die("Usage: themes.py set <theme>")
        cmd_set(sys.argv[2])
    elif cmd == "select":
        cmd_select()
    else:
        die(f"Unknown command: {cmd}")

