from typing import Annotated
from fastapi import Depends, Request
from adapters.db import Crud, build_crud


def get_db_manager(request: Request):
    db_provider = request.app.state.db_provider
    if db_provider is None:
        raise RuntimeError("db connection is not initialized")
    return build_crud(db_provider.session_factory)


DbManagerDep = Annotated[Crud, Depends(get_db_manager)]
