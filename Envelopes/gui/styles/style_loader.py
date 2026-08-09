from pathlib import Path


def load_stylesheet(style_path: Path) -> str:
    """Read and return a Qt stylesheet file."""

    try:
        return style_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"Stylesheet not found: {style_path}")
        return ""
    except OSError as error:
        print(f"Unable to read stylesheet: {error}")
        return ""