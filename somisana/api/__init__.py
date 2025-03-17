from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from somisana.api.routers import product
from somisana.db import Session
from somisana.version import VERSION

from somisana.api.routers import product
from somisana.api.routers import simulation

app = FastAPI(
    title="SOMISANA API",
    description="SOMISANA | SOMISANA Api",
    version=VERSION,
    docs_url='/swagger',
    redoc_url='/docs',
)

app.include_router(product.router, prefix='/product', tags=['Product'])
app.include_router(simulation.router, prefix='/simulation', tags=['Simulation'])

app.add_middleware(
    CORSMiddleware,
    # allow_origins=config.ODP.API.ALLOW_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
