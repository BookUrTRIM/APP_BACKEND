# BookUrTrim — Backend API

API REST pour la plateforme de réservation de prestations capillaires **BookUrTrim**.
Construite avec FastAPI, SQLAlchemy et PostgreSQL.

---

## Stack technique

| Couche | Technologie |
|---|---|
| Framework web | FastAPI 0.115.x |
| ORM | SQLAlchemy 2.x |
| Base de données | PostgreSQL |
| Authentification | JWT via PyJWT |
| Validation | Pydantic v2 |
| Paiement | Stripe |
| Documentation API | OpenAPI intégré (/docs, /redoc) |

---

## Architecture

```
src/
├── app.py                  # Factory FastAPI — point d'entrée
├── config.py               # Variables d'environnement centralisées
│
├── controllers/            # APIRouters FastAPI (routing + HTTP)
├── services/               # Logique métier
├── repositories/           # Accès base de données (requêtes SQLAlchemy)
├── mappers/                # Conversion DAO ↔ Model ↔ DTO
├── daos/                   # Entités SQLAlchemy (ORM)
├── models/                 # Dataclasses métier
├── dtos/                   # Schémas Pydantic (validation + sérialisation)
│   ├── auth/
│   ├── client/
│   ├── provider/
│   ├── service/
│   ├── availability/
│   ├── appointment/
│   ├── payment/
│   ├── invoice/
│   ├── review/
│   └── notification/
├── enums/                  # Enums Python
├── exceptions/             # Exceptions HTTP métier (AppException)
├── shared/                 # Utilitaires transversaux
│   ├── db.py               # Base SQLAlchemy + session factory
│   ├── logger.py           # Configuration du logging
│   ├── swagger.py          # Initialisation Flasgger
│   ├── decorators.py       # @role_required, @require_json, @safe_swag_from
│   └── error_handlers.py   # Gestionnaire global d'erreurs FastAPI
└── docs/                   # Documentation Swagger (fichiers YAML)
    ├── definitions.yaml    # Schémas globaux réutilisables
    ├── auth/
    ├── clients/
    ├── providers/
    ├── services/
    ├── availabilities/
    ├── appointments/
    ├── payments/
    └── notifications/
```

---

## Installation

### Prérequis

- Python 3.11+
- PostgreSQL 15+

### Mise en place

```bash
# 1. Cloner le dépôt
git clone <repo-url>
cd APP_BACKEND

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.template .env
# Éditer .env avec vos valeurs

# 5. Créer la base de données
psql -U postgres -c "CREATE DATABASE bookurtrim;"
psql -U postgres -d bookurtrim -f db/script.sql
```

---

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `DATABASE_URL` | URL de connexion PostgreSQL | `postgresql://postgres:password@localhost:5432/bookurtrim` |
| `JWT_SECRET_KEY` | Clé secrète JWT (min. 32 chars) | `change-me-...` |
| `JWT_ACCESS_TOKEN_TTL_MINUTES` | Durée de vie du token (minutes) | `60` |
| `STRIPE_SECRET_KEY` | Clé secrète Stripe | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Secret de vérification webhook Stripe | `whsec_...` |
| `DOCS_ENABLED` | Active /docs et /redoc (`1` = oui) | `0` |
| `APP_ENV` | Environnement (`development` / `production`) | `development` |
| `LOG_LEVEL` | Niveau de log (`DEBUG` / `INFO` / ...) | `INFO` |

---

## Lancement

```bash
# Depuis la racine du projet
cd src
python app.py
```

L'API démarre sur `http://localhost:8000`.

Swagger UI (si `DOCS_ENABLED=1`) : `http://localhost:8000/docs`

---

## Endpoints principaux

| Domaine | Préfixe | Description |
|---|---|---|
| Auth | `/auth` | Inscription, connexion |
| Clients | `/clients` | Profils clients |
| Prestataires | `/providers` | Profils prestataires, services, disponibilités, avis |
| Prestations | `/services` | CRUD des prestations |
| Disponibilités | `/availabilities` | Créneaux de disponibilité |
| Rendez-vous | `/appointments` | Réservations, annulation, factures, avis |
| Paiements | `/payments` | Paiements Stripe, webhook |
| Notifications | `/notifications` | Notifications liées aux rendez-vous |

---

## Flux métier principal

```
POST /auth/signup          → Créer un compte (client ou prestataire)
POST /auth/login           → Obtenir un token JWT

POST /clients              → Créer le profil client
POST /providers            → Créer le profil prestataire
POST /services             → Créer une prestation (prestataire)
POST /availabilities       → Déclarer des créneaux (prestataire)

POST /appointments         → Réserver un RDV (client)
PATCH /appointments/:id    → Confirmer / terminer (prestataire)
POST /appointments/:id/cancel → Annuler

POST /payments             → Initier un paiement
POST /payments/webhook     → Confirmer via Stripe (webhook)

POST /appointments/:id/invoice  → Générer la facture
POST /appointments/:id/review   → Déposer un avis
```