from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dtos.dashboard.dashboard_dto import DashboardResponseDTO
from enums.user_enum import UserRole
from mappers.dashboard_mapper import DashboardMapper
from services.dashboard_service import DashboardService
from shared.db import get_db
from shared.dependencies import require_role

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/provider", response_model=DashboardResponseDTO)
def get_provider_dashboard(
    period: str = "month",
    current_user: dict = Depends(require_role(UserRole.PROVIDER)),
    db: Session = Depends(get_db),
) -> DashboardResponseDTO:
    model = DashboardService.get_metrics(db, int(current_user["sub"]), period)
    return DashboardMapper.model_to_dto(model)
