# Phase 6: Global Scale & Ecosystem Expansion

This phase focuses on opening the CAPS platform to external systems and automotive networks, while providing a multi-organization management structure.

## Proposed Changes

### [Backend/Database]
#### [MODIFY] [backend/database.py](file:///home/ubuntu/Pedestrian_Safety_Analysis/backend/database.py)
- Update `AnalysisResult` model to include `tenant_id` for multi-tenancy.
- Ensure the database initialization handles the new column.

#### [MODIFY] [backend/main.py](file:///home/ubuntu/Pedestrian_Safety_Analysis/backend/main.py)
- **Open API Implementation**: Create `/api/v1/external/events` for external emergency services (119/Police) to fetch or subscribe to critical safety alerts.
- **V2X Integration**: Create a V2X broadcast service endpoint `/api/v1/v2x/messages` that formats safety data into standard V2X messages (e.g., PSM - Personal Safety Message).
- **Multi-tenant Filtering**: Add `tenant_id` header or query parameter support to API endpoints.

### [Documentation]
#### [MODIFY] [docu/ROADMAP.md](file:///home/ubuntu/Pedestrian_Safety_Analysis/docu/ROADMAP.md)
- Mark Phase 6 items as completed.

## Open Questions
- For V2X data format, should we simulate a specific standard like J2735? (I will implement a JSON-based representation of these standards).
- For multi-tenancy, do we need full authentication for different tenants now, or just the structural foundation? (I'll start with the structural foundation).

## Verification Plan
### API Testing
- Test the new `/api/v1/external/events` endpoint to ensure it returns filtered "CRITICAL" alerts.
- Test the V2X broadcast endpoint to verify format compliance.
