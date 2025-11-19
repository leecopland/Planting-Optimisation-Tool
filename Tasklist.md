## High-Level Architecture

**Frontend**: Web interface (Figma → React or similar).

**Backend**: FastAPI service providing REST endpoints.

**Data Science**: Data cleaning, validation, feature engineering, predictive modelling, suitability scoring.

Database: PostgreSQL.

Deployment: Containerized (Docker), hosted on university infrastructure or cloud environment.

## 2. Global Tasks (ALL Teams)
## 2.1 Project Setup

* Skills audit (tech stack familiarity, role allocation).

* Repository creation, branching strategy, PR workflow definition.

* Set up project directory structure (frontend, backend, data-science modules).

### Create documentation:

* CONTRIBUTING.md (how to get started, submit a PR, don't leak API key etc.)

* Style guide (PEP8, Black/Ruff, ESLint, Prettier)

* Security guidelines (authentication, roles, exposing endpoints, data handling, input validation)

* Testing philosophy (code coverage, Test-driven development)

* Setup instructions and dependency installation

### 2.2 Compliance & Governance (mainly DS team)

* Create anonymisation strategy for farm owner names or further data being added.

* Define data privacy boundaries and allowed data flows.

* Document external approval processes (e.g., Gold Standard species list).

### 2.3 Testing & CI/CD

* Establish minimum code coverage targets.

* Choose test frameworks (pytest, React Testing Library).

* Set up automated linting, type checking, unit tests.

* Potential CI pipeline for automated deploys.

## 3. Backend Team
### 3.1 API Foundations

* Initialize FastAPI project.

* Define routing and modular structure.

* Establish API versioning approach.

* Set up environment variables and application config.

### 3.2 Database & ORM

* Design schema:

    * Farms

    * Species

    * Environmental attributes

    * Intercropping pairs

    * Pests

    * Terrain hazards

    * Goals/quotas (carbon capture %, biodiversity %, etc.)

    * Database connection (SQLModel or SQLAlchemy)

    * Migration setup (Alembic).

### 3.3 Endpoints – MVP

CRUD for Farms & Species.
 
* Endpoint to ingest cleaned DS data.

* Endpoint to retrieve suitability recommendations.

* Authentication (basic tokens / OAuth2 Password Flow).

* Bulk upload/download endpoints for CSV.

### 3.4 Recommendation Logic Integration

* Receive suitability scores from DS module.

* Apply exclusion rules:

* Elevation limits

* Soil pH extremes

* Terrain hazards

* Apply limiting and intercropping factor logic.

* Enforce global farm-network goals (e.g., 30% carbon-capture species).

* Handle recommendation of "not-yet-approved" species.

### 3.5 System-Level Features

* Role-based access (Area Manager vs Standard User).

* Logging and observability (structured logs).

* Error responses and validation with Pydantic schemas.

## 4. Data Science Team
### 4.1 Data Preparation

* Data cleaning, normalisation, missing value handling.

* Remove or anonymise personal identifiers.

* Exploratory data analysis and data validation reports.

### 4.2 Modelling

Feature engineering for:

   * Rainfall
   * Temperature
   * Soil pH
   * Terrain hazards
   * Intercropping interactions
   * Build suitability models (regression, classification, or rule-based hybrid).
   * Evaluate accuracy using appropriate metrics.

### 4.3 Domain-Specific Requirements

* Pest impact modelling and survival risk estimation.

* Intercropping compatibility matrix (bidirectional).

* Compute yield reduction risk.

* Species approval status ingestion & update tool.

### 4.4 Additional Features

* Tree coverage estimation model (e.g., 3m × 3m spacing).

* Identification model (sapling image classification).

* API format for sending suitability scores to backend.

## 5. Frontend Team
### 5.1 Design

UX discovery & requirements from PO.

Figma wireframes for:

   * Dashboard

   * Farm lists

   * Recommendation view

   * Upload/download screens

   * Species exploration

   * Risk/hazard overlays

   * Interactive components defined (buttons, forms, tables).

### 5.2 Implementation

* Set up frontend project (React+Vite?).

* Implement global layout, navigation, theming.

* Integrate frontend → backend API calls.

Data visualisation for:

* Recommended species

* Coverage calculations

* Pest alerts

* Hazard maps

* Intercropping warnings

### 5.3 Authentication

* Login page and token storage.

* Role-specific dashboards.

### 6. User Stories (Examples)
#### 6.1 Role: Farm/Area Manager

> I can upload farm data in bulk so I don’t manually enter 100 farms.

> I can download species recommendations for all farms I manage.

> I can see hazard warnings (flood zones, landslides) that might affect survivability.

> I can view how many seedlings are required based on planting density.

#### 6.2 Role: Agronomy Scientist

> I can update limiting/exclusion factors to reflect new research.

> I can propose new species for approval.

#### 6.3 Role: Farmer

>  I can visually identify saplings using the image-recognition feature.

# 7. Sprint 1 Tasks
Global

* Skills audit

* Repo setup

* CONTRIBUTING.md

* Style guide decisions

* CI linting + tests

* Backend

* Create FastAPI skeleton

* Define database schema draft

* Set up ORM

* Implement basic CRUD species/farms

* Create API documentation with OpenAPI

* Data Science

* Clean and validate datasets

* Initial EDA

* Build early suitability scoring baseline

* Frontend

* Define Figma wireframes

* Set up React project

* Add login screen and scaffold pages

* Sprint 1 should produce a functioning API skeleton, a frontend scaffold, and the first DS outputs feeding into the backend.