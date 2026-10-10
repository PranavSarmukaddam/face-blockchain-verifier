"""
utils/logging_utils.py
Coloured, stage-aware console logger for the pipeline.
"""
import sys
from datetime import datetime

# Ensure utf-8 encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


RESET  = "\033[0m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"


def _supports_colour() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(colour: str, text: str) -> str:
    if _supports_colour():
        return f"{colour}{text}{RESET}"
    return text


def stage(n: int, total: int, label: str) -> None:
    print(f"\n{_c(BOLD, f'[{n}/{total}]')} {_c(CYAN, label)}")


def ok(msg: str) -> None:
    print(f"      {_c(GREEN, '✓')} {msg}")


def warn(msg: str) -> None:
    print(f"      {_c(YELLOW, '⚠')} {msg}")


def err(msg: str) -> None:
    print(f"      {_c(RED, '✗')} {msg}")


def info(msg: str) -> None:
    print(f"        {msg}")


def separator() -> None:
    print("=" * 60)


def header(title: str) -> None:
    separator()
    print(_c(BOLD, f"  {title}"))
    separator()


def result(verified: bool) -> None:
    separator()
    if verified:
        print(_c(GREEN, _c(BOLD, "  FINAL RESULT: ✓ VERIFIED")))
    else:
        print(_c(RED, _c(BOLD, "  FINAL RESULT: ✗ NOT VERIFIED")))
    separator()


def debug(msg: str, enabled: bool = False) -> None:
    if enabled:
        ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"  [DEBUG {ts}] {msg}")
