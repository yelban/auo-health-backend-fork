# file: root/__init__.py
from asyncio import run
from datetime import datetime
from functools import wraps
from uuid import UUID

import typer


# This is a standard decorator that takes arguments
# the same way app.command does but with
# app as the first parameter
def async_command(app, *args, **kwargs):
    def decorator(async_func):

        # Now we make a function that turns the async
        # function into a synchronous function.
        # By wrapping async_func we preserve the
        # meta characteristics typer needs to create
        # a good interface, such as the description and
        # argument type hints
        @wraps(async_func)
        def sync_func(*_args, **_kwargs):
            return run(async_func(*_args, **_kwargs))

        # Now use app.command as normal to register the
        # synchronous function
        app.command(*args, **kwargs)(sync_func)

        # We return the async function unmodifed,
        # so its library functionality is preserved
        return async_func

    return decorator


# as a method injection, app will be replaced as self
# making the syntax exactly the same as it used to be.
# put this all in __init__.py and it will be injected into
# the library project wide
typer.Typer.async_command = async_command

from auo_project import core, crud, db, models, schemas
from auo_project.core.file import get_and_write
from auo_project.db.session import AsyncSession, SessionLocal, engine

cli = typer.Typer(name="project_name API")


@cli.async_command()
async def create_user(
    org_name: str,
    username: str,
    password: str,
    email: str,
    full_name: str = "",
    mobile: str = "",
    is_active: bool = True,
    is_superuser: bool = False,
):
    """Create user"""
    # with AsyncSession(engine) as db_session:
    db_session = SessionLocal()
    org = await crud.org.get_by_name(db_session=db_session, name=org_name)
    if not org:
        raise Exception(f"Not found org name: {org_name}")
    user_in = schemas.UserCreate(
        org_id=org.id,
        username=username,
        full_name=full_name,
        mobile=mobile,
        email=email,
        is_active=is_active,
        is_superuser=is_superuser,
        password=password,
    )
    user = await crud.user.create(db_session=db_session, obj_in=user_in)
    typer.echo(f"created {username} user")
    return user


@cli.async_command()
async def rewrite_file(
    file_id: UUID,
    overwrite: bool = False,
):
    """Rewrite file to Database"""
    db_session = SessionLocal()
    file = await crud.file.get(db_session=db_session, id=file_id)
    await get_and_write(db_session=db_session, file_id=file.id, overwrite=overwrite)
    typer.echo(f"rewrite file id {file_id}")


@cli.async_command()
async def rewrite_file_by_measure_time(
    measure_time: datetime,
    overwrite: bool = False,
):
    """Rewrite file to Database measure time greater than input"""
    db_session = SessionLocal()
    measures = await crud.measure_info.get_all_by_measure_time(
        db_session=db_session,
        measure_time=datetime.strptime(measure_time, "%Y-%m-%d"),
    )
    file_ids = [measure.file_id for measure in measures]
    for file_id in file_ids:
        await get_and_write(db_session=db_session, file_id=file_id, overwrite=overwrite)
        typer.echo(f"rewrite file id {file_id}")


@cli.async_command()
async def delete_measure_related_data(
    measure_id: UUID,
):
    """Delete measure info and related data"""
    db_session = SessionLocal()
    await crud.measure_info.remove(db_session=db_session, id=measure_id)
    typer.echo(f"delete measure info id {measure_id}")


@cli.command()
def shell():  # pragma: no cover
    """Opens an interactive shell with objects auto imported"""
    _vars = {
        "cli": cli,
        "core": core,
        "crud": crud,
        "db": db,
        "models": models,
        "schemas": schemas,
        "settings": core.config.settings,
        "engine": engine,
        "AsyncSession": AsyncSession,
        "SessionLocal": SessionLocal,
        "create_user": create_user,
        "rewrite_file": rewrite_file,
        "delete_measure_related_data": delete_measure_related_data,
    }
    typer.echo(f"Auto imports: {list(_vars.keys())}")
    try:
        from IPython import start_ipython

        start_ipython(argv=[], user_ns=_vars)
    except ImportError:
        import code

        code.InteractiveConsole(_vars).interact()


if __name__ == "__main__":
    cli()
