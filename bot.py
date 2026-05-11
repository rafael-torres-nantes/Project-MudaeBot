import logging

import discord
from discord.ext import tasks

import config
from service.claim_service import ClaimService
from service.kakera_service import KakeraService
from service.roll_service import RollService
from utils.wishlist_loader import Wishlist

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)-20s] %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("discord").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

client = discord.Client()

roll_service: RollService | None = None
claim_service: ClaimService | None = None


def get_channel():
    """Localiza e retorna o canal de texto configurado no servidor alvo.

    Retorna:
        Objeto do canal Discord, ou None se o servidor ou canal não forem encontrados.
    """
    guild = discord.utils.get(client.guilds, name=config.TARGET_GUILD)
    if not guild:
        logger.error("Servidor '%s' não encontrado", config.TARGET_GUILD)
        return None
    channel = discord.utils.get(guild.text_channels, name=config.TARGET_CHANNEL)
    if not channel:
        logger.error("Canal '%s' não encontrado em '%s'", config.TARGET_CHANNEL, config.TARGET_GUILD)
        return None
    return channel


@client.event
async def on_ready():
    """Executado quando o bot se conecta ao Discord com sucesso.
    Inicializa os serviços, carrega as wishlists, busca o top kakera e inicia o loop horário.
    """
    global roll_service, claim_service
    logger.info("Logado como %s", client.user)

    channel = get_channel()
    if not channel:
        return

    wishlist = Wishlist.load()
    anime_wishlist = Wishlist.load_anime()
    logger.info("Wishlist carregada: %d personagens, %d animes", len(wishlist), len(anime_wishlist))

    top_names = await KakeraService(client, channel).fetch_top()

    claim_service = ClaimService(wishlist, top_names, anime_wishlist)
    roll_service = RollService(client, channel)

    claim_service.can_marry = await roll_service.execute()
    hourly_roll.start()


@tasks.loop(hours=1)
async def hourly_roll():
    """Loop executado a cada hora para realizar o ciclo de roll automático."""
    if roll_service and claim_service:
        logger.debug("Loop horário disparado")
        claim_service.can_marry = await roll_service.execute()


@hourly_roll.before_loop
async def before_roll():
    """Aguarda o bot estar pronto antes de iniciar o loop horário."""
    await client.wait_until_ready()


@client.event
async def on_message(message):
    """Intercepta mensagens do Mudae no canal configurado e aciona o serviço de claim.

    Args:
        message: Mensagem recebida no Discord.
    """
    if message.author.id != config.MUDAE_BOT_ID or claim_service is None:
        return
    channel = get_channel()
    if not channel or message.channel.id != channel.id:
        return
    await claim_service.handle(message)


client.run(config.DISCORD_TOKEN)
