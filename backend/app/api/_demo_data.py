"""VIGIL demo fixtures.

Everything in this module is SIMULATED for demonstration purposes. Nothing is
retrieved from a live scanner, cloud provider, SIEM, or threat-intelligence feed.

The fixtures are authored as internally consistent security records so the
CVE -> affected component -> installed version -> fixed version -> CVSS ->
severity -> KEV status -> exploit availability -> affected asset relationships
never contradict one another. Real public identifiers (CVE IDs, CVSS vectors,
and package/service names) are used so the UI exercises realistic data shapes;
the installed/fixed versions and asset mappings are illustrative, not live
findings.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings


def demo_mode_enabled() -> bool:
    """Return True only when the operator explicitly opted into demo mode.

    Demo fixtures exist for local development so the UI has something to render.
    They are gated behind ``ENABLE_DEMO_MODE`` (default: off) so VIGIL never
    presents simulated records as real security findings, and they are only ever
    consulted for endpoints that have no database-backed implementation. Callers
    must never use this to disguise a failed database query.
    """
    return bool(settings.ENABLE_DEMO_MODE)


def simulated_response(payload: dict) -> dict:
    """Tag a response as simulated and clearly not real telemetry."""
    return {**payload, "source_state": "simulated", "simulated": True}

# ---------------------------------------------------------------------------
# Vulnerability catalogue
# ---------------------------------------------------------------------------
# Each entry is a single source of truth. Severity is derived from the CVSS
# score, KEV and exploit availability are fixed per-CVE (never randomised), and
# fixed_version is the real patched version for the named component.
VULNERABILITY_CATALOG: list[dict[str, Any]] = [
    {
        "cve_id": "CVE-2021-44228",
        "title": "Apache Log4j2 JNDI remote code execution (Log4Shell)",
        "description": (
            "JNDI lookups used in configuration, log messages and parameters do not "
            "protect against attacker-controlled LDAP lookups. An attacker who can "
            "control log messages can execute arbitrary code loaded from a remote "
            "server."
        ),
        "cvss_score": 10.0,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        "affected_component": "log4j-core",
        "installed_version": "2.14.1",
        "fixed_version": "2.17.1",
        "ecosystem": "maven",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-3094",
        "title": "XZ Utils backdoor in liblzma build chain (xz 5.6.0/5.6.1)",
        "description": (
            "Malicious code introduced into xz/liblzma 5.6.0 and 5.6.1 can intercept "
            "authentication on affected systems. This affects the xz-utils package, "
            "not application-level JavaScript dependencies."
        ),
        "cvss_score": 10.0,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        "affected_component": "xz-utils",
        "installed_version": "5.6.1",
        "fixed_version": "5.6.2",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-21626",
        "title": "runc container escape via leaked file descriptor (Leaky Vessels)",
        "description": (
            "runc before 1.1.12 allows an attacker to escape the container namespace "
            "through an inherited working-directory file descriptor, exposing the "
            "host filesystem."
        ),
        "cvss_score": 8.6,
        "cvss_vector": "CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H",
        "affected_component": "runc",
        "installed_version": "1.1.11",
        "fixed_version": "1.1.12",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-23897",
        "title": "Jenkins arbitrary file read via CLI command parser",
        "description": (
            "Jenkins uses the args4j library to parse CLI commands. A missing "
            "permission check allows an attacker with Overall/Read to read arbitrary "
            "files on the Jenkins controller."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "jenkins-core",
        "installed_version": "2.441",
        "fixed_version": "2.442",
        "ecosystem": "maven",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2023-44487",
        "title": "HTTP/2 Rapid Reset denial of service",
        "description": (
            "The HTTP/2 protocol allows a denial of service because request "
            "cancellation can reset many streams quickly, exhausting server "
            "resources."
        ),
        "cvss_score": 7.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
        "affected_component": "golang.org/x/net/http2",
        "installed_version": "0.16.0",
        "fixed_version": "0.17.0",
        "ecosystem": "go",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2023-46604",
        "title": "Apache ActiveMQ OpenWire remote code execution",
        "description": (
            "Apache ActiveMQ is vulnerable to remote code execution through unsafe "
            "deserialization in the OpenWire protocol. An attacker can run arbitrary "
            "commands by sending crafted class types."
        ),
        "cvss_score": 10.0,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        "affected_component": "activemq-broker",
        "installed_version": "5.17.5",
        "fixed_version": "5.18.3",
        "ecosystem": "maven",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-0204",
        "title": "GoAnywhere MFT authentication bypass",
        "description": (
            "GoAnywhere MFT allows authentication bypass via the administrative "
            "portal, permitting creation of admin users without authentication."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "goanywhere-mft",
        "installed_version": "7.4.0",
        "fixed_version": "7.4.1",
        "ecosystem": "system",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2023-50164",
        "title": "Apache Struts path traversal enabling file-upload RCE",
        "description": (
            "Apache Struts is vulnerable to path traversal via manipulated file "
            "upload parameters, allowing an attacker to upload a malicious file and "
            "achieve remote code execution."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "struts2-core",
        "installed_version": "6.3.0",
        "fixed_version": "6.3.0.2",
        "ecosystem": "maven",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-27198",
        "title": "JetBrains TeamCity authentication bypass",
        "description": (
            "JetBrains TeamCity before 2023.11.4 allows an unauthenticated attacker "
            "to bypass authentication and gain administrative control of the server."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "teamcity-server",
        "installed_version": "2023.11.3",
        "fixed_version": "2023.11.4",
        "ecosystem": "system",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-6387",
        "title": "OpenSSH regreSSHion unauthenticated remote code execution",
        "description": (
            "A signal-handler race condition in the OpenSSH server can lead to "
            "unauthenticated remote code execution as root on glibc-based Linux."
        ),
        "cvss_score": 8.1,
        "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "openssh-server",
        "installed_version": "9.6p1",
        "fixed_version": "9.8p1",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-38475",
        "title": "Apache HTTP Server mod_rewrite path confusion",
        "description": (
            "Insufficient escaping of output in mod_rewrite can allow an attacker to "
            "map URLs to filesystem locations served by the server, potentially "
            "executing code."
        ),
        "cvss_score": 9.1,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
        "affected_component": "httpd",
        "installed_version": "2.4.58",
        "fixed_version": "2.4.59",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2023-38545",
        "title": "curl SOCKS5 heap buffer overflow",
        "description": (
            "A heap-based buffer overflow in curl's SOCKS5 proxy handshake can lead "
            "to remote code execution when curl uses a malicious SOCKS5 proxy."
        ),
        "cvss_score": 8.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H",
        "affected_component": "curl",
        "installed_version": "8.3.0",
        "fixed_version": "8.4.0",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2022-22965",
        "title": "Spring Framework data binding RCE (Spring4Shell)",
        "description": (
            "A Spring MVC data-binding vulnerability on JDK 9+ allows remote code "
            "execution through class-loader manipulation via request parameters."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "spring-webmvc",
        "installed_version": "5.3.17",
        "fixed_version": "5.3.18",
        "ecosystem": "maven",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-1597",
        "title": "PostgreSQL JDBC driver SQL injection via PreferQueryMode",
        "description": (
            "pgjdbc allows SQL injection when using a non-default PreferQueryMode "
            "setting with attacker-controlled integer parameters."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "postgresql-jdbc",
        "installed_version": "42.6.0",
        "fixed_version": "42.7.2",
        "ecosystem": "maven",
        "cisa_kev": False,
        "exploit_available": False,
    },
    {
        "cve_id": "CVE-2023-45853",
        "title": "zlib MiniZip integer overflow",
        "description": (
            "MiniZip in zlib contains an integer overflow that can lead to a heap "
            "buffer overflow when processing specially crafted ZIP archives."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "zlib",
        "installed_version": "1.2.13",
        "fixed_version": "1.3.1",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": False,
    },
    {
        "cve_id": "CVE-2024-4577",
        "title": "PHP CGI argument injection remote code execution",
        "description": (
            "PHP on Windows in CGI mode is vulnerable to argument injection through "
            "best-fit encoding conversion, allowing remote code execution."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "php-cgi",
        "installed_version": "8.1.28",
        "fixed_version": "8.1.29",
        "ecosystem": "system",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2023-4863",
        "title": "libwebp heap buffer overflow",
        "description": (
            "A heap buffer overflow in libwebp allows an attacker to perform an "
            "out-of-bounds write via a crafted WebP image, exploited in the wild via "
            "browsers and applications."
        ),
        "cvss_score": 8.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H",
        "affected_component": "libwebp",
        "installed_version": "1.3.1",
        "fixed_version": "1.3.2",
        "ecosystem": "system",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-2961",
        "title": "glibc iconv buffer overflow to out-of-bounds write",
        "description": (
            "The iconv() function in the GNU C Library may write up to 3 bytes past "
            "the end of the output buffer when converting to ISO-2022-CN-EXT, "
            "leading to memory corruption."
        ),
        "cvss_score": 8.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H",
        "affected_component": "glibc",
        "installed_version": "2.38",
        "fixed_version": "2.39",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2022-42889",
        "title": "Apache Commons Text interpolation RCE (Text4Shell)",
        "description": (
            "Apache Commons Text performs variable interpolation using lookup keys "
            "with default lookups able to trigger script, URL and DNS lookups, "
            "leading to remote code execution."
        ),
        "cvss_score": 9.8,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "commons-text",
        "installed_version": "1.9",
        "fixed_version": "1.10.0",
        "ecosystem": "maven",
        "cisa_kev": True,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-27199",
        "title": "JetBrains TeamCity limited path traversal",
        "description": (
            "JetBrains TeamCity before 2023.11.4 allows an unauthenticated attacker "
            "to perform limited path traversal and leak sensitive information."
        ),
        "cvss_score": 7.3,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L",
        "affected_component": "teamcity-server",
        "installed_version": "2023.11.3",
        "fixed_version": "2023.11.4",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": False,
    },
    {
        "cve_id": "CVE-2023-6246",
        "title": "glibc __vsyslog_internal heap overflow",
        "description": (
            "A heap-based buffer overflow in glibc's syslog implementation can allow "
            "local privilege escalation to root on affected distributions."
        ),
        "cvss_score": 7.8,
        "cvss_vector": "CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H",
        "affected_component": "glibc",
        "installed_version": "2.37",
        "fixed_version": "2.39",
        "ecosystem": "system",
        "cisa_kev": False,
        "exploit_available": True,
    },
    {
        "cve_id": "CVE-2024-20931",
        "title": "Oracle WebLogic Server JNDI remote code execution",
        "description": (
            "A vulnerability in Oracle WebLogic Server lets an unauthenticated "
            "attacker with network access compromise WebLogic Server."
        ),
        "cvss_score": 7.5,
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H",
        "affected_component": "weblogic-server",
        "installed_version": "14.1.1.0.0",
        "fixed_version": "14.1.1.0.1",
        "ecosystem": "maven",
        "cisa_kev": False,
        "exploit_available": False,
    },
]


def cvss_to_severity(score: float | None) -> str:
    """Map a CVSS v3 base score to a severity band."""
    if score is None:
        return "unknown"
    if score >= 9.0:
        return "critical"
    if score >= 7.0:
        return "high"
    if score >= 4.0:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------
# Each asset lists the components it runs so a vulnerability can be mapped to a
# plausible host. Data is deterministic (no random.*) so counts stay stable and
# consistent between requests.
DEMO_ASSETS: list[dict[str, Any]] = [
    {
        "id": "asset-api-gateway-prod",
        "name": "api-gateway-prod",
        "asset_type": "api_endpoint",
        "provider": "aws",
        "region": "us-east-1",
        "ip_address": "203.0.113.10",
        "domain": "api-gateway-prod.cloud.internal",
        "publicly_exposed": True,
        "criticality": 10,
        "tags": ["production", "customer-facing"],
        "components": ["log4j-core", "golang.org/x/net/http2", "httpd"],
    },
    {
        "id": "asset-payment-service",
        "name": "payment-service",
        "asset_type": "cloud_instance",
        "provider": "aws",
        "region": "us-east-1",
        "ip_address": "10.0.4.21",
        "domain": "payment-service.cloud.internal",
        "publicly_exposed": False,
        "criticality": 10,
        "tags": ["production", "critical"],
        "components": ["spring-webmvc", "postgresql-jdbc", "commons-text"],
    },
    {
        "id": "asset-user-db-prod",
        "name": "user-db-prod",
        "asset_type": "database",
        "provider": "aws",
        "region": "us-east-1",
        "ip_address": "10.0.8.5",
        "domain": "user-db-prod.cloud.internal",
        "publicly_exposed": True,
        "criticality": 10,
        "tags": ["production", "critical"],
        "components": ["postgresql-jdbc", "glibc"],
    },
    {
        "id": "asset-web-app-frontend",
        "name": "web-app-frontend",
        "asset_type": "api_endpoint",
        "provider": "aws",
        "region": "eu-west-1",
        "ip_address": "203.0.113.42",
        "domain": "web-app-frontend.cloud.internal",
        "publicly_exposed": True,
        "criticality": 8,
        "tags": ["production", "customer-facing"],
        "components": ["node", "libwebp", "curl"],
    },
    {
        "id": "asset-auth-service",
        "name": "auth-service",
        "asset_type": "cloud_instance",
        "provider": "gcp",
        "region": "eu-west-1",
        "ip_address": "10.12.2.9",
        "domain": "auth-service.cloud.internal",
        "publicly_exposed": True,
        "criticality": 9,
        "tags": ["production", "critical"],
        "components": ["golang.org/x/net/http2", "openssh-server", "glibc"],
    },
    {
        "id": "asset-ml-training-worker",
        "name": "ml-training-worker",
        "asset_type": "container",
        "provider": "aws",
        "region": "us-west-2",
        "ip_address": "10.30.1.77",
        "domain": "ml-training-worker.cloud.internal",
        "publicly_exposed": False,
        "criticality": 7,
        "tags": ["internal", "critical"],
        "components": ["runc", "xz-utils", "glibc"],
    },
    {
        "id": "asset-data-pipeline",
        "name": "data-pipeline",
        "asset_type": "cloud_instance",
        "provider": "gcp",
        "region": "us-west-2",
        "ip_address": "10.40.6.15",
        "domain": "data-pipeline.cloud.internal",
        "publicly_exposed": False,
        "criticality": 8,
        "tags": ["internal", "critical"],
        "components": ["zlib", "curl", "commons-text"],
    },
    {
        "id": "asset-ci-runner",
        "name": "ci-runner",
        "asset_type": "cloud_instance",
        "provider": "aws",
        "region": "us-east-1",
        "ip_address": "10.50.3.4",
        "domain": "ci-runner.cloud.internal",
        "publicly_exposed": False,
        "criticality": 7,
        "tags": ["internal", "monitoring"],
        "components": ["jenkins-core", "teamcity-server", "node"],
    },
    {
        "id": "asset-admin-portal",
        "name": "admin-portal",
        "asset_type": "api_endpoint",
        "provider": "azure",
        "region": "eu-west-1",
        "ip_address": "203.0.113.88",
        "domain": "admin-portal.cloud.internal",
        "publicly_exposed": True,
        "criticality": 9,
        "tags": ["production", "customer-facing"],
        "components": ["php-cgi", "httpd", "struts2-core"],
    },
    {
        "id": "asset-audit-log-store",
        "name": "audit-log-store",
        "asset_type": "storage_bucket",
        "provider": "aws",
        "region": "us-east-1",
        "ip_address": "10.60.0.2",
        "domain": "audit-log-store.cloud.internal",
        "publicly_exposed": False,
        "criticality": 6,
        "tags": ["internal", "monitoring"],
        "components": ["zlib"],
    },
    {
        "id": "asset-legacy-billing",
        "name": "legacy-billing",
        "asset_type": "cloud_instance",
        "provider": "azure",
        "region": "us-west-2",
        "ip_address": "10.70.9.30",
        "domain": "legacy-billing.cloud.internal",
        "publicly_exposed": False,
        "criticality": 8,
        "tags": ["staging", "critical"],
        "components": ["weblogic-server", "activemq-broker", "spring-webmvc"],
    },
    {
        "id": "asset-search-index",
        "name": "search-index",
        "asset_type": "cloud_instance",
        "provider": "gcp",
        "region": "ap-southeast-2",
        "ip_address": "10.80.4.6",
        "domain": "search-index.cloud.internal",
        "publicly_exposed": False,
        "criticality": 6,
        "tags": ["internal"],
        "components": ["glibc", "zlib"],
    },
]

# The container inventory. Only fields the data model actually provides are
# included; no image digests, capabilities or mounted secrets are fabricated.
DEMO_CONTAINERS: list[dict[str, Any]] = [
    {
        "id": "container-gateway",
        "name": "gateway-container",
        "image": "registry.internal/vigil/api-gateway:1.4.2",
        "status": "running",
        "privileges": "privileged",
        "exposed_ports": [80, 443, 3000],
        "vulnerabilities": 7,
        "asset_id": "asset-api-gateway-prod",
        "host": "k8s-worker-1",
    },
    {
        "id": "container-web",
        "name": "web-container",
        "image": "registry.internal/vigil/web-app:2.1.0",
        "status": "running",
        "privileges": "standard",
        "exposed_ports": [3000],
        "vulnerabilities": 4,
        "asset_id": "asset-web-app-frontend",
        "host": "k8s-worker-2",
    },
    {
        "id": "container-ml-trainer",
        "name": "ml-training-worker",
        "image": "registry.internal/vigil/ml-trainer:0.9.5",
        "status": "running",
        "privileges": "privileged",
        "exposed_ports": [],
        "vulnerabilities": 5,
        "asset_id": "asset-ml-training-worker",
        "host": "k8s-worker-3",
    },
    {
        "id": "container-auth",
        "name": "auth-container",
        "image": "registry.internal/vigil/auth-service:3.0.1",
        "status": "running",
        "privileges": "standard",
        "exposed_ports": [8443],
        "vulnerabilities": 2,
        "asset_id": "asset-auth-service",
        "host": "k8s-worker-1",
    },
    {
        "id": "container-pipeline",
        "name": "pipeline-runner",
        "image": "registry.internal/vigil/data-pipeline:1.2.0",
        "status": "exited",
        "privileges": "standard",
        "exposed_ports": [],
        "vulnerabilities": 3,
        "asset_id": "asset-data-pipeline",
        "host": "k8s-worker-2",
    },
]


# ---------------------------------------------------------------------------
# Demo-mode vulnerability expansion (development only)
# ---------------------------------------------------------------------------
# This mirrors the legacy fixture expansion: the catalogue is expanded into
# per-asset findings and only ever used when ENABLE_DEMO_MODE is on. It lives
# here so demo mode has a single, clearly-labelled source of simulated records
# and the production endpoints contain no fixture logic.

from datetime import datetime, timedelta

_DEMO_BASE_TIME = datetime(2024, 8, 1, 9, 0, 0)


def build_demo_vulnerabilities() -> list[dict[str, Any]]:
    """Expand the simulated catalogue into per-asset findings (demo mode only)."""
    findings: list[dict[str, Any]] = []
    for idx, entry in enumerate(VULNERABILITY_CATALOG):
        component = entry["affected_component"]
        matching = [a for a in DEMO_ASSETS if component in a.get("components", [])]
        if matching:
            matching.sort(
                key=lambda a: (a["publicly_exposed"], a["criticality"]), reverse=True
            )
            asset = matching[0]
        else:
            asset = None

        if entry["cisa_kev"] and entry["exploit_available"]:
            status = "active"
        elif entry["cisa_kev"]:
            status = "in_triage"
        elif entry["cvss_score"] >= 9.0:
            status = "active"
        else:
            status = "in_triage" if idx % 3 == 0 else "fixed"

        findings.append(
            {
                "id": f"vuln-{idx}",
                "cve_id": entry["cve_id"],
                "title": entry["title"],
                "description": entry["description"],
                "cvss_score": entry["cvss_score"],
                "cvss_vector": entry["cvss_vector"],
                "severity": cvss_to_severity(entry["cvss_score"]),
                "cisa_kev": entry["cisa_kev"],
                "exploit_available": entry["exploit_available"],
                "affected_component": component,
                "installed_version": entry["installed_version"],
                "fixed_version": entry["fixed_version"],
                "ecosystem": entry["ecosystem"],
                "status": status,
                "asset_id": asset["id"] if asset else None,
                "asset_name": asset["name"] if asset else "unassigned",
                "publicly_exposed": bool(asset and asset["publicly_exposed"]),
                "discovered_at": (_DEMO_BASE_TIME - timedelta(hours=idx * 7)).isoformat(),
                "updated_at": (
                    _DEMO_BASE_TIME - timedelta(hours=max(0, idx * 7 - 3))
                ).isoformat(),
                "source_state": "simulated",
            }
        )
    return findings
