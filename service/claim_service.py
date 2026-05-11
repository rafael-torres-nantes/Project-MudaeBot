import logging

from rapidfuzz import fuzz, process

import config
from utils.mudae_parser import MudaeParser

logger = logging.getLogger(__name__)


class ClaimService:
    def __init__(self, wishlist: set[str], top_names: set[str], anime_wishlist: set[str]):
        """Inicializa o serviço de claim com as listas de prioridade.

        Args:
            wishlist: Conjunto de nomes de personagens desejados.
            top_names: Conjunto de nomes do top 100 kakera do servidor.
            anime_wishlist: Conjunto de nomes de animes cujos personagens devem ser reclamados.
        """
        self.wishlist = wishlist
        self.top_names = top_names
        self.anime_wishlist = anime_wishlist
        self.can_marry = True

    async def handle(self, message) -> None:
        """Processa uma mensagem do Mudae e reage com ❤️ se o personagem for desejado.
        Segue a hierarquia: top kakera → wishlist → kakera mínimo → anime wishlist.

        Args:
            message: Mensagem do Discord enviada pelo Mudae.
        """
        if not message.embeds:
            return

        embed = message.embeds[0]
        name = MudaeParser.character_name(embed)
        if not name:
            return

        reason = self._match_reason(name.lower(), embed)
        if reason is None:
            logger.debug("Ignorado: %s", name)
            return

        if self.can_marry:
            await message.add_reaction("❤️")
            logger.info("CLAIM — %s (%s)", name, reason)
        else:
            logger.warning("SKIP — %s (%s) — sem claim disponível", name, reason)

    def _match_reason(self, name_lower: str, embed) -> str | None:
        """Determina o motivo pelo qual um personagem deve ser reclamado, conforme prioridade.

        Args:
            name_lower: Nome do personagem em letras minúsculas.
            embed: Embed do Discord com os dados do personagem.

        Retorna:
            String descrevendo o motivo do claim, ou None se não deve ser reclamado.
        """
        if self._fuzzy_in(name_lower, self.top_names):
            return "top 100 kakera"
        if self._fuzzy_in(name_lower, self.wishlist):
            return "wishlist"
        if MudaeParser.kakera_value(embed) > config.KAKERA_MIN:
            return f"kakera > {config.KAKERA_MIN}"
        series = MudaeParser.series_name(embed)
        if series and self._fuzzy_in(series.lower(), self.anime_wishlist):
            return f"anime: {series}"
        return None

    @staticmethod
    def _fuzzy_in(name: str, names: set[str]) -> bool:
        """Verifica se um nome tem correspondência aproximada em um conjunto de nomes.
        Usa similaridade de string para tolerar variações de escrita entre a wishlist
        e o nome exibido pelo Mudae.

        Args:
            name: Nome a verificar em letras minúsculas.
            names: Conjunto de nomes de referência em letras minúsculas.

        Retorna:
            True se houver correspondência acima do limiar configurado.
        """
        if not names:
            return False
        result = process.extractOne(name, names, scorer=fuzz.ratio)
        return result is not None and result[1] >= config.FUZZY_THRESHOLD
