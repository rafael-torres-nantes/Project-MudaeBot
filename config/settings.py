import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    """Lê uma variável de ambiente obrigatória e lança erro se ausente.

    Args:
        key: Nome da variável de ambiente.

    Retorna:
        Valor da variável de ambiente como string.

    Lança:
        RuntimeError: Se a variável não estiver definida ou estiver vazia.
    """
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Variável de ambiente obrigatória ausente: {key}")
    return value


def _int(key: str, default: int) -> int:
    """Lê uma variável de ambiente e a converte para inteiro, usando valor padrão se ausente.

    Args:
        key: Nome da variável de ambiente.
        default: Valor padrão caso a variável não esteja definida.

    Retorna:
        Valor inteiro da variável de ambiente ou o padrão.
    """
    return int(os.getenv(key, str(default)))


DISCORD_TOKEN: str = _require("DISCORD_TOKEN")
MUDAE_BOT_ID: int = _int("MUDAE_BOT_ID", 432610292342587392)

TARGET_GUILD: str = os.getenv("TARGET_GUILD", "OCOLAST")
TARGET_CHANNEL: str = os.getenv("TARGET_CHANNEL", "cartinhas")

KAKERA_MIN: int = _int("KAKERA_MIN", 150)
FUZZY_THRESHOLD: int = _int("FUZZY_THRESHOLD", 85)

TIMEOUT_TOP: int = _int("TIMEOUT_TOP", 15)
TIMEOUT_MU: int = _int("TIMEOUT_MU", 10)

WISHLIST_FILE: str = os.getenv("WISHLIST_FILE", "data/wishlist.txt")
ANIME_WISHLIST_FILE: str = os.getenv("ANIME_WISHLIST_FILE", "data/anime_wishlist.txt")
