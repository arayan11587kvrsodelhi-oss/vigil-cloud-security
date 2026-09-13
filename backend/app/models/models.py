from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from datetime import datetime
import enum


class AssetType(str, enum.Enum):
    CLOUD_INSTANCE = "cloud_instance"
    API_ENDPOINT = "api_endpoint"
    CONTAINER = "container"
    DATABASE = "database"
    STORAGE_BUCKET = "storage_bucket"
    FUNCTION = "function"
    LOAD_BALANCER = "load_balancer"
    DNS_RECORD = "dns_record"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityStatus(str, enum.Enum):
    ACTIVE = "active"
    FIXED = "fixed"
    ACCEPTED = "accepted"
    FALSE_POSITIVE = "false_positive"
    IN_TRIAGE = "in_triage"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=True)  # aws, gcp, azure, etc.
    region = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    domain = Column(String(255), nullable=True)
    publicly_exposed = Column(Boolean, default=False)
    criticality = Column(Integer, default=1)  # 1-10
    asset_metadata = Column("metadata", JSONB, default={})
    tags = Column(JSONB, default=[])
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    vulnerabilities = relationship("Vulnerability", back_populates="asset")
    containers = relationship("Container", back_populates="asset")
    secrets = relationship("Secret", back_populates="asset")
    network_routes = relationship("NetworkRoute", back_populates="asset")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cve_id = Column(String(20), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    cvss_score = Column(Float, nullable=True)
    cvss_vector = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=True)
    cisa_kev = Column(Boolean, default=False)
    exploit_available = Column(Boolean, default=False)
    affected_component = Column(String(255), nullable=True)
    fixed_version = Column(String(100), nullable=True)
    status = Column(String(20), default=VulnerabilityStatus.ACTIVE.value)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    references = Column(JSONB, default=[])
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)

    asset = relationship("Asset", back_populates="vulnerabilities")
    attack_paths = relationship("AttackPath", back_populates="vulnerability")


class Container(Base):
    __tablename__ = "containers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    image = Column(String(500), nullable=True)
    registry = Column(String(255), nullable=True)
    tag = Column(String(100), nullable=True)
    status = Column(String(50), default="running")
    privileges = Column(String(50), default="standard")
    exposed_ports = Column(JSONB, default=[])
    environment_vars = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)

    asset = relationship("Asset", back_populates="containers")


class Secret(Base):
    __tablename__ = "secrets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # api_key, password, token, certificate
    severity = Column(String(20), default="high")
    location = Column(String(500), nullable=True)
    exposed = Column(Boolean, default=False)
    rotated = Column(Boolean, default=False)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)

    asset = relationship("Asset", back_populates="secrets")


class NetworkRoute(Base):
    __tablename__ = "network_routes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_ip = Column(String(45), nullable=True)
    destination_ip = Column(String(45), nullable=True)
    port = Column(Integer, nullable=True)
    protocol = Column(String(10), default="TCP")
    is_public = Column(Boolean, default=False)
    is_allowed = Column(Boolean, default=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)

    asset = relationship("Asset", back_populates="network_routes")


class IAMRole(Base):
    __tablename__ = "iam_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=True)
    permissions = Column(JSONB, default=[])
    is_overprivileged = Column(Boolean, default=False)
    trust_policy = Column(JSONB, default={})
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)


class AttackPath(Base):
    __tablename__ = "attack_paths"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(20), nullable=True)
    path_steps = Column(JSONB, default=[])
    is_active = Column(Boolean, default=True)
    discovered_at = Column(DateTime, default=datetime.utcnow)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)
    vulnerability_id = Column(UUID(as_uuid=True), ForeignKey("vulnerabilities.id"), nullable=True)

    vulnerability = relationship("Vulnerability", back_populates="attack_paths")


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_type = Column(String(50), nullable=False)  # dependency, secret, container, sbom
    status = Column(String(20), default="completed")
    total_findings = Column(Integer, default=0)
    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)
    summary = Column(JSONB, default={})
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id"), nullable=True)