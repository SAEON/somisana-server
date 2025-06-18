from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from somisana.api.lib import local_resource_folder_path
from somisana.api.routers import dataset
from somisana.api.routers import product
from somisana.api.routers import resource
from somisana.db import Session
from somisana.version import VERSION

app = FastAPI(
    title="SOMISANA API",
    description="SOMISANA | SOMISANA Api",
    version=VERSION,
    docs_url='/swagger',
    redoc_url='/docs',
)

app.include_router(product.router, prefix='/product', tags=['Product'])
app.include_router(resource.router, prefix='/resource', tags=['Resource'])
app.include_router(dataset.router, prefix='/dataset', tags=['Dataset'])

app.add_middleware(
    CORSMiddleware,
    # allow_origins=config.ODP.API.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/local_resources", StaticFiles(directory=local_resource_folder_path), name="Local Resources")


@app.middleware('http')
async def db_middleware(request: Request, call_next):
    try:
        response: Response = await call_next(request)
        if 200 <= response.status_code < 400:
            Session.commit()
        else:
            Session.rollback()
    finally:
        Session.remove()

    return response
