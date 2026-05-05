from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional, TypedDict

import yaml
from flasgger import Swagger

import config

logger = logging.getLogger(__name__)


class SwaggerSpec(TypedDict):
    endpoint: str
    route: str
    rule_filter: Callable
    model_filter: Callable


class SwaggerConfig(TypedDict, total=False):
    headers: list[dict[str, str]]
    specs: list[SwaggerSpec]
    static_url_path: str
    swagger_ui: bool
    specs_route: str
    doc_dir: str


class SwaggerTemplate(TypedDict, total=False):
    swagger: str
    info: dict[str, str]
    basePath: str
    tags: list[dict[str, str]]
    securityDefinitions: dict
    security: list
    definitions: dict[str, dict]


def init_swagger(app) -> Optional[Swagger]:
    """
    Initialise la documentation Swagger / Flasgger pour l'application Flask.
    Retourne None si SWAGGER_ENABLED=0 dans l'environnement.
    """
    if not getattr(config, "SWAGGER_ENABLED", False):
        logger.warning("Swagger désactivé (SWAGGER_ENABLED=0).")
        return None

    docs_dir: Path = Path(__file__).resolve().parents[1] / "docs"
    defs_path: Path = docs_dir / "definitions.yaml"

    template: SwaggerTemplate = {
        "swagger": "2.0",
        "info": {
            "title": "BookUrTrim API",
            "version": "1.0.0",
            "description": (
                "Documentation interactive de l'API BookUrTrim.\n\n"
                "Plateforme de réservation de prestations capillaires."
            ),
        },
        "basePath": "/",
        "tags": [
            {"name": "auth",          "description": "Inscription et connexion"},
            {"name": "clients",       "description": "Gestion des profils clients"},
            {"name": "providers",     "description": "Gestion des profils prestataires"},
            {"name": "services",      "description": "Prestations proposées par les prestataires"},
            {"name": "availabilities","description": "Créneaux de disponibilité"},
            {"name": "appointments",  "description": "Réservations de rendez-vous"},
            {"name": "payments",      "description": "Paiements et webhooks Stripe"},
            {"name": "invoices",      "description": "Factures générées après prestation"},
            {"name": "reviews",       "description": "Avis clients sur les rendez-vous"},
            {"name": "notifications", "description": "Notifications liées aux rendez-vous"},
        ],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Bearer token. Exemple : **Bearer &lt;votre_token&gt;**",
            },
        },
        "security": [{"BearerAuth": []}],
    }

    if not defs_path.exists():
        raise FileNotFoundError(f"Fichier de définitions Swagger introuvable : {defs_path}")

    try:
        with defs_path.open(encoding="utf-8") as f:
            defs = yaml.safe_load(f) or {}
            if "definitions" in defs:
                template["definitions"] = defs["definitions"]
                logger.info(
                    "Swagger : %d définitions importées depuis %s",
                    len(defs["definitions"]),
                    defs_path,
                )
            else:
                logger.warning("Clé 'definitions' absente dans %s", defs_path)
    except yaml.YAMLError as e:
        logger.error("Erreur YAML dans %s : %s", defs_path, e)
        raise

    swagger_config: SwaggerConfig = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/apispec_1.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "doc_dir": str(docs_dir.resolve()),
    }

    swagger = Swagger(app, template=template, config=swagger_config)
    logger.info("Swagger initialisé — documentation sur /apidocs/ (dossier : %s)", docs_dir)
    return swagger
