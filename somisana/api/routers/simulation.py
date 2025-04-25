from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib import save_file_resource
from somisana.api.lib.auth import Authorize
from somisana.api.models import SimulationModel, ResourceModel
from somisana.const import SOMISANAScope, EntityType
from somisana.db import Session
from somisana.db.models import Simulation, SimulationResource

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
        data_access_url=simulation.data_access_url,
        cover_image=ResourceModel(
            id=simulation.resources[0].id,
            resource_type=simulation.resources[0].resource_type,
        ) if simulation.resources else None,
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
async def update_simulation(
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


@router.put(
    '/{simulation_id}/resource/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_file_resource(
        simulation_id: int,
        resource_query: Annotated[ResourceModel, Query()],
        file: Annotated[UploadFile, File()]
):
    if not (Session.get(Simulation, simulation_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource_id = save_file_resource(
        file=file,
        resource_model=ResourceModel(**resource_query.dict()),
        entity_type=EntityType.SIMULATION,
        entity_id=simulation_id
    )

    SimulationResource(
        simulation_id=simulation_id,
        resource_id=resource_id,
    ).save()

    return resource_id
