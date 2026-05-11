import asyncio
import logging

import config
from utils.mudae_parser import MudaeParser

logger = logging.getLogger(__name__)


class RollService:
    def __init__(self, client, channel):
        """Inicializa o serviço de roll com o cliente e canal do Discord.

        Args:
            client: Instância do cliente Discord autenticado.
            channel: Canal de texto onde os comandos serão enviados.
        """
        self.client = client
        self.channel = channel

    async def execute(self) -> bool:
        """Executa o ciclo de roll: verifica disponibilidade de claim via $mu
        e envia $wa caso o claim esteja disponível.

        Retorna:
            True se o claim está disponível e $wa foi enviado, False caso contrário.
        """
        can_marry = await self._check_mu()
        logger.info("Status de claim: %s", "disponível" if can_marry else "indisponível")

        if not can_marry:
            logger.warning("$wa bloqueado — sem claim disponível no momento")
            return False

        await self.channel.send("$wa")
        logger.info("$wa enviado em #%s", self.channel.name)
        return True

    async def _check_mu(self) -> bool:
        """Envia $mu e interpreta a resposta do Mudae para verificar disponibilidade de claim.
        O listener é registrado antes do envio para evitar race condition com a resposta do Mudae.

        Retorna:
            True se o claim está disponível, False se estiver em cooldown.
            Retorna True por segurança em caso de timeout.
        """
        def is_mudae_msg(m):
            return (
                m.author.id == config.MUDAE_BOT_ID
                and m.channel.id == self.channel.id
            )

        waiter = asyncio.ensure_future(
            self.client.wait_for("message", check=is_mudae_msg, timeout=config.TIMEOUT_MU)
        )

        await self.channel.send("$mu")
        logger.debug("$mu enviado — aguardando resposta do Mudae")

        try:
            msg = await waiter
            if msg.content:
                logger.debug("Resposta $mu (texto): %s", msg.content.strip())
                return MudaeParser.can_marry_from_text(msg.content)
            if msg.embeds:
                logger.debug("Resposta $mu (embed)")
                return MudaeParser.can_marry(msg.embeds[0])
            return True
        except asyncio.TimeoutError:
            logger.warning("$mu sem resposta em %ds — assumindo claim disponível", config.TIMEOUT_MU)
            return True
