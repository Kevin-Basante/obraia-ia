"""Elements the service measures, so the backend and the docs can show them."""

from fastapi import APIRouter, Depends

from app.elements import REQUIRED_DIMENSIONS, ElementType
from app.quantities import unit_of
from app.schemas import ElementInfo
from app.security import require_service_token

router = APIRouter(prefix="/api/v1", tags=["Elements"], dependencies=[Depends(require_service_token)])


@router.get("/elements", response_model=list[ElementInfo])
def list_elements() -> list[ElementInfo]:
    """Each element type with the dimensions the model must read and the unit of its total."""
    return [
        ElementInfo(element_type=element, required_dimensions=list(REQUIRED_DIMENSIONS[element]), unit=unit_of(element))
        for element in ElementType
    ]
