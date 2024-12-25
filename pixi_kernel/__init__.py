import logging

from jupyter_server.serverapp import ServerApp

from .handlers import setup_handlers

logging.basicConfig(level=logging.INFO, format="pixi-kernel %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _jupyter_labextension_paths() -> list[dict[str, str]]:
    return [{"src": "labextension", "dest": "pixi-kernel"}]


def _jupyter_server_extension_points() -> list[dict[str, str]]:
    return [{"module": "pixi_kernel"}]


def _load_jupyter_server_extension(server_app: ServerApp) -> None:
    setup_handlers(server_app.web_app)
    logger.info("Registered pixi_kernel server extension")
