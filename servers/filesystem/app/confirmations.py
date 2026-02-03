"""Pending deletion confirmation token state (file-backed)."""
import json
import pathlib
from datetime import datetime, timezone
from typing import Dict

CONFIRMATION_FILE = pathlib.Path("./.pending_confirmations.json")
CONFIRMATION_TTL_SECONDS = 60


def load_confirmations() -> Dict[str, Dict]:
    """Load pending confirmations from the JSON file."""
    if not CONFIRMATION_FILE.exists():
        return {}
    try:
        with CONFIRMATION_FILE.open("r") as f:
            data = json.load(f)
            now = datetime.now(timezone.utc)
            valid_confirmations = {}
            for token, details in data.items():
                try:
                    details["expiry"] = datetime.fromisoformat(details["expiry"])
                    if details["expiry"] > now:
                        valid_confirmations[token] = details
                except (ValueError, TypeError, KeyError):
                    continue
            return valid_confirmations
    except (json.JSONDecodeError, IOError):
        return {}


def save_confirmations(confirmations: Dict[str, Dict]) -> None:
    """Save pending confirmations to the JSON file."""
    try:
        serializable = {
            token: {**details, "expiry": details["expiry"].isoformat()}
            for token, details in confirmations.items()
        }
        with CONFIRMATION_FILE.open("w") as f:
            json.dump(serializable, f, indent=2)
    except IOError:
        pass


def cleanup_stale_confirmation_file() -> None:
    """Remove stale confirmation file on startup."""
    if CONFIRMATION_FILE.exists():
        try:
            CONFIRMATION_FILE.unlink()
        except OSError:
            pass
