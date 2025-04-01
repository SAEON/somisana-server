from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.models import SimulationIn
from somisana.db import Session
from somisana.db.models import Simulation

router = APIRouter()


@router.get(
    '/all'
)
async def list_simulations():
    all_simulations = Session.query(Simulation).all()

    return all_simulations


@router.post(
    '/'
)
async def create_simulation(
        simulation_in: SimulationIn
) -> int:
    simulation = Simulation(
        title=simulation_in.title,
        folder_path=simulation_in.folder_path,
        data_access_url=simulation_in.data_access_url
    )

    simulation.save()

    return simulation.id


@router.delete(
    '/{simulation_id}'
)
async def delete_simulation(
        simulation_id: int
):
    if not (simulation := Session.get(Simulation, simulation_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    simulation.delete()
