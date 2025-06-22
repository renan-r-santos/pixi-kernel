import json
from pathlib import Path
from dataclasses import asdict

import tornado
from jupyter_server.base.handlers import APIHandler
from jupyter_server.serverapp import ServerWebApplication
from jupyter_server.utils import url_path_join
from returns.result import Failure

from .compatibility import has_compatible_pixi
from .env import envs_from_path


class EnvHandler(APIHandler):
    @tornado.web.authenticated
    async def post(self) -> None:
        result = await has_compatible_pixi()
        if isinstance(result, Failure):
            raise tornado.web.HTTPError(500, result.failure())

        body = self.get_json_body()
        if body is None:
            raise tornado.web.HTTPError(400, "Missing request body")

        server_root = body["serverRoot"]
        local_path = body["localPath"]

        notebook_path = Path(server_root).expanduser().joinpath(local_path).resolve()
        if notebook_path.is_file():
            notebook_path = notebook_path.parent

        envs = await envs_from_path(notebook_path)
        envs_dicts = [asdict(env) for env in envs]
        await self.finish(json.dumps(envs_dicts))


def setup_handlers(web_app: ServerWebApplication) -> None:
    base_url = web_app.settings["base_url"]
    url_path = url_path_join(base_url, "pixi-kernel", "envs")
    web_app.add_handlers(".*$", [(url_path, EnvHandler)])  # type: ignore[no-untyped-call]
