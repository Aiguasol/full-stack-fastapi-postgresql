import logging
from pathlib import Path

import typer

from alembic import command
from alembic.config import Config
from app import initial_data
from app.core.config import SettingsModeEnum, settings
from app.db.init_db import refresh_db
from app.initial_data import SessionLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def print_settings():
    is_prod = settings.FASTAPI_MODE == SettingsModeEnum.PROD
    color = typer.colors.RED if is_prod else typer.colors.BLUE
    bold = is_prod

    for k, v in settings:
        if isinstance(v, list):
            typer.secho(f"{k}:", color=color, bold=bold)
            for e in v:
                typer.secho(f"\t{e}", color=color, bold=bold)
        else:
            typer.secho(f"{k}: {v}", color=color, bold=bold)


@app.command()
def init_db():
    initial_data.main()


@app.command()
def refresh_db(use_alembic: bool = True, seed_data: bool = True):

    if not use_alembic:
        db = SessionLocal()
        refresh_db(db=db)
    else:
        alembic_cfg = Config(Path(__file__).parent.parent / "alembic.ini")
        command.downgrade(alembic_cfg, "base")
        command.upgrade(alembic_cfg, "head")

    if seed_data:
        initial_data.main()


if __name__ == "__main__":
    app()
