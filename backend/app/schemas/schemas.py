from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
from datetime import datetime


class AssetBase(BaseModel):
    name: str
    asset_type: str
    provider: Optional[str] = None
    region: Optional[str] = None
    ip_address: Optional[str] = None
    domain: Optional[str] = None
    publicly_exposed: bool = False
    criticality: int = 1
    tags: list[str] = []


class AssetResponse(AssetBase):
    id: UUID
    discovered_at: datetime
    last_seen_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class VulnerabilityBase(BaseModel):
    cve_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    cvss_score: Optional[float] = None
    severity: Optional[str] = None
    cisa_kev: bool = False
    exploit_available: bool = False
    affected_component: Optional[str] = None
    fixed_version: Optional[str] = None
    status: str = "active"


class VulnerabilityResponse(VulnerabilityBase):
    id: UUID
    discovered_at: datetime
    updated_at: datetime
    asset_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class AttackPathResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    path_steps: list[Any] = []
    is_active: bool = True
    discovered_at: datetime
    vulnerability_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class SecurityScoreResponse(BaseModel):
    overall_score: float
    asset_coverage: float
    vulnerability_score: float
    exposure_score: float
    iam_score: float
    secret_score: float
    trend: list[dict] = []


class ScanResultResponse(BaseModel):
    id: UUID
    scan_type: str
    status: str
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AISummaryRequest(BaseModel):
    asset_id: Optional[UUID] = None
    vulnerability_id: Optional[UUID] = None
    context: Optional[str] = None


class AISummaryResponse(BaseModel):
    summary: str
    risk_assessment: str
    recommended_actions: list[str]
    threat_context: Optional[str] = None