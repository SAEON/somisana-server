from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib.auth import Authorize
from somisana.api.models import SimulationModel
from somisana.const import SOMISANAScope
from somisana.db import Session
from somisana.db.models import Simulation

router = APIRouter()


@router.get(
    '/all',
    dependencies=[Depends(Authorize(SOMISANAScope.SIMULATION_READ))]
)
async def list_simulations():
    all_simulations = Session.query(Simulation).all()

    return all_simulations


@router.get(
    '/{simulation_id}',
    response_model=SimulationModel,
    dependencies=[Depends(Authorize(SOMISANAScope.SIMULATION_READ))]
)
async def get_simulation(
        simulation_id: int,
) -> SimulationModel:
    if not (simulation := Session.get(Simulation, simulation_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return SimulationModel(
        id=simulation.id,
        title=simulation.title,
        folder_path=simulation.folder_path,
        data_access_url=simulation.data_access_url
    )


@router.post(
    '/',
    dependencies=[Depends(Authorize(SOMISANAScope.SIMULATION_ADMIN))]
)
async def create_simulation(
        simulation_in: SimulationModel
) -> int:
    simulation = Simulation(
        title=simulation_in.title,
        folder_path=simulation_in.folder_path,
        data_access_url=simulation_in.data_access_url
    )

    simulation.save()

    return simulation.id


@router.put(
    '/{simulation_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.SIMULATION_ADMIN))]
)
async def update_product(
        simulation_id: int,
        simulation_in: SimulationModel
):
    if not (simulation := Session.get(Simulation, simulation_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    simulation.title = simulation_in.title,
    simulation.folder_path = simulation_in.folder_path,
    simulation.data_access_url = simulation_in.data_access_url,

    simulation.save()


@router.delete(
    '/{simulation_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.SIMULATION_ADMIN))]
)
async def delete_simulation(
        simulation_id: int
):
    if not (simulation := Session.get(Simulation, simulation_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    simulation.delete()
