import re


class MudaeParser:
    _NEGATIVE_MARRY = [
        "0 left", "can't marry", "can't claim",
        "cannot claim", "não pode", "0 remaining", "cannot marry",
    ]
    _KAKERA_MIN_PATTERN = re.compile(r"(\d+)\s*kakera", re.IGNORECASE)
    _KAKERA_STAR_PATTERN = re.compile(r"[⭐✨]\s*(\d+)")
    # formato real: **#1** - **Hatsune Miku** - VOCALOID
    _TOP_LINE_PATTERN = re.compile(r"^\*\*#\d+\*\*\s+-\s+\*\*(.+?)\*\*\s+-\s+")

    @classmethod
    def can_marry(cls, embed) -> bool:
        """
        Verifica se pode casar a partir de um embed (resposta com formatação rica).
        Procura indicadores negativos na descrição e campos do embed.

        Args:
            embed: Objeto embed do Discord a ser analisado.
        """
        if embed is None:
            return True
        text = (embed.description or "").lower()
        for field in embed.fields:
            text += field.value.lower()
        return not any(indicator in text for indicator in cls._NEGATIVE_MARRY)

    @classmethod
    def can_marry_from_text(cls, text: str) -> bool:
        """
        Verifica se pode casar a partir de uma mensagem de texto puro.
        Usado para parsear a resposta do $mu, que o Mudae envia como texto simples
        (ex: "rafatn, you can't claim for another 45 min.").

        Args:
            text: Conteúdo textual da mensagem do Mudae.
        """
        return not any(indicator in text.lower() for indicator in cls._NEGATIVE_MARRY)

    @staticmethod
    def character_name(embed) -> str | None:
        """
        Extrai o nome do personagem rolado a partir do embed. O Mudae armazena
        o nome no campo author.name do embed de roll.

        Args:
            embed: Objeto embed do Discord a ser analisado.
        """
        if embed is None:
            return None
        if embed.author and embed.author.name:
            return embed.author.name
        return None

    @staticmethod
    def series_name(embed) -> str | None:
        """
        Extrai o nome da série/anime do embed de roll. O Mudae coloca o nome
        da série na primeira linha não-vazia da descrição do embed.

        Args:
            embed: Objeto embed do Discord a ser analisado.
        """
        if embed is None or not embed.description:
            return None
        for line in embed.description.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped
        return None

    @classmethod
    def kakera_value(cls, embed) -> int:
        """
        Extrai o valor de kakera do embed. Busca padrões como "123 kakera" ou
        "⭐ 123" na descrição, rodapé e campos do embed.

        Args:
            embed: Objeto embed do Discord a ser analisado.
        """
        if embed is None:
            return 0
        sources = [embed.description or ""]
        if embed.footer and embed.footer.text:
            sources.append(embed.footer.text)
        for field in embed.fields:
            sources.append(field.value)
        text = " ".join(sources)
        for pattern in (cls._KAKERA_MIN_PATTERN, cls._KAKERA_STAR_PATTERN):
            match = pattern.search(text)
            if match:
                return int(match.group(1))
        return 0

    @classmethod
    def top_names(cls, embed) -> set[str]:
        """
        Parseia o embed do comando $top e retorna os nomes dos personagens listados.
        Espera linhas no formato "1. Nome — ⭐ 1234" ou "1. Nome (série) — ⭐ 1234".

        Args:
            embed: Objeto embed do Discord retornado pelo comando $top.
        """
        if embed is None or not embed.description:
            return set()
        names = set()
        for line in embed.description.splitlines():
            match = cls._TOP_LINE_PATTERN.match(line)
            if match:
                names.add(match.group(1).strip().lower())
        return names
