def color_text(text: str, fg:str=None, bg:str=None) -> str:
    fg_colors = {"black": 30,"red": 31,"green": 32,"yellow": 33,"blue": 34,
        "magenta": 35,"cyan": 36,"white": 37,
    }

    bg_colors = {
        "black": 40, "red": 41, "green": 42, "yellow": 43, "blue": 44,"magenta": 45,
        "cyan": 46,"white": 47,
    }

    codes = []

    if fg in fg_colors:
        codes.append(str(fg_colors[fg]))

    if bg in bg_colors:
        codes.append(str(bg_colors[bg]))

    if not codes:
        return text

    return f"\033[{';'.join(codes)}m{text}\033[0m"


def sakila_banner() -> str:
    banner = "\n".join(
        [
            "  ____        _    _ _        _      ____                           _     ",
            " / ___|  __ _| | _(_) | __ _ / |    / ___|  ___  __ _ _ __ ___ ___ | |__  ",
            " \\___ \\ / _` | |/ / | |/ _` || |____\\___ \\ / _ \\/ _` | '__/ __/ _ \\| '_ \\ ",
            "  ___) | (_| |   <| | | (_| || |_____|__) |  __/ (_| | | | (_| (_) | | | |",
            " |____/ \\__,_|_|\\_\\_|_|\\__,_||_|    |____/ \\___|\\__,_|_|  \\___\\___/|_| |_|",
        ]
    )
    return color_text(banner, "cyan")


def dict_to_color_str(d: dict) -> str:
    return ", ".join(f"{color_text(k.capitalize() if i == 0 else k, "magenta")} - '{color_text(v, "yellow")}'" for i, (k,v) in enumerate(d.items()))
