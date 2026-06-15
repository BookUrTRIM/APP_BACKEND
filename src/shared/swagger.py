"""
Configuration de la documentation OpenAPI pour FastAPI.
FastAPI génère Swagger UI (/docs) et ReDoc (/redoc) automatiquement.
"""
from __future__ import annotations

_OPENAPI_TAGS = [
    {"name": "auth",           "description": "Inscription et connexion"},
    {"name": "clients",        "description": "Gestion des profils clients"},
    {"name": "providers",      "description": "Gestion des profils prestataires"},
    {"name": "services",       "description": "Prestations proposées par les prestataires"},
    {"name": "availabilities", "description": "Créneaux de disponibilité"},
    {"name": "appointments",   "description": "Réservations de rendez-vous"},
    {"name": "payments",       "description": "Paiements et webhooks Stripe"},
    {"name": "invoices",       "description": "Factures générées après prestation"},
    {"name": "reviews",        "description": "Avis clients sur les rendez-vous"},
    {"name": "notifications",  "description": "Notifications liées aux rendez-vous"},
]


def get_openapi_metadata() -> dict:
    return {
        "title": "BookUrTrim API",
        "version": "1.0.0",
        "description": (
            "Documentation interactive de l'API BookUrTrim.\n\n"
            "Plateforme de réservation de prestations capillaires."
        ),
        "openapi_tags": _OPENAPI_TAGS,
    }
