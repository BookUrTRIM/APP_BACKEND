from fastapi import APIRouter, Depends, HTTPException
from dtos.dashboard.dashboard_dto import DashboardResponseDTO
from repositories.dashboard_repository import DashboardRepository
from shared.dependencies import get_current_user

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/provider", response_model=DashboardResponseDTO)
def get_provider_dashboard(period: str = "month",current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "provider":
        raise HTTPException(status_code=403, detail="Réservé aux prestataires")
    metrics = DashboardRepository.get_provider_dashboard_metrics(int(current_user["sub"]),period)
    if not metrics:
        raise HTTPException(status_code=404, detail="Prestataire introuvable")
    return DashboardResponseDTO(**metrics)