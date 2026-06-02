from fastapi import APIRouter, Depends
from dtos.dashboard.dashboard_dto import DashboardResponseDTO
from services.dashboard_service import DashboardService
from mappers.dashboard_mapper import DashboardMapper
from shared.dependencies import get_current_user, require_role
from enums.user_enum import UserRole

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@dashboard_router.get("/provider", response_model=DashboardResponseDTO)
def get_provider_dashboard(period: str = "month", current_user: dict = Depends(require_role(UserRole.PROVIDER))):
    model = DashboardService.get_metrics(int(current_user["sub"]), period)
    return DashboardMapper.model_to_dto(model)