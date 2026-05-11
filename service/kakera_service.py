import asyncio
import logging

import config
from utils.mudae_parser import MudaeParser

logger = logging.getLogger(__name__)


class KakeraService:
    def __init__(self, client, channel):
        """Inicializa o serviço de kakera com o cliente e canal do Discord.

        Args:
            client: Instância do cliente Discord autenticado.
            channel: Canal de texto onde os comandos serão enviados.
        """
        self.client = client
        self.channel = channel

    async def fetch_top(self) -> set[str]:
        """Envia $top e coleta os nomes do ranking de kakera do servidor.
        O listener é registrado antes do envio para evitar race condition com a resposta do Mudae.

        Retorna:
            Conjunto de nomes dos personagens no top kakera, em letras minúsculas.
            Retorna conjunto vazio se o Mudae não responder dentro do timeout.
        """
        def is_mudae_embed(m):
            return (
                m.author.id == config.MUDAE_BOT_ID
                and m.channel.id == self.channel.id
                and len(m.embeds) > 0
            )

        waiter = asyncio.ensure_future(
            self.client.wait_for("message", check=is_mudae_embed, timeout=config.TIMEOUT_TOP)
        )

        await self.channel.send("$top")
        logger.debug("$top enviado — aguardando resposta do Mudae")

        try:
            msg = await waiter
            names = MudaeParser.top_names(msg.embeds[0])
            logger.info("TOP kakera carregado: %d personagens", len(names))
            if not names:
                logger.warning(
                    "TOP kakera retornou 0 nomes — descrição do embed: %.300s",
                    msg.embeds[0].description or "(vazia)",
                )
            return names
        except asyncio.TimeoutError:
            logger.warning("$top sem resposta em %ds — top_names vazio", config.TIMEOUT_TOP)
            return set()
