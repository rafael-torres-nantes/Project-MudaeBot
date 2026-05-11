import os

import config


class Wishlist:
    @classmethod
    def load(cls) -> set[str]:
        """Carrega a wishlist de personagens do arquivo configurado.

        Retorna:
            Conjunto de nomes de personagens em letras minúsculas.
        """
        return cls._load_file(config.WISHLIST_FILE)

    @classmethod
    def load_anime(cls) -> set[str]:
        """Carrega a wishlist de animes do arquivo configurado.

        Retorna:
            Conjunto de nomes de animes em letras minúsculas.
        """
        return cls._load_file(config.ANIME_WISHLIST_FILE)

    @classmethod
    def _load_file(cls, path: str) -> set[str]:
        """Lê um arquivo de wishlist e retorna seu conteúdo como conjunto.
        Cria o arquivo vazio caso não exista. Ignora linhas em branco e comentários (#).

        Args:
            path: Caminho para o arquivo de wishlist.

        Retorna:
            Conjunto de itens da wishlist em letras minúsculas.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()
            return set()
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        return {
            line.strip().lower()
            for line in lines
            if line.strip() and not line.startswith("#")
        }
