# Threat Advisory TLP:WHITE — Supply Chain Compromise via CI/CD Platform Vulnerabilities

**Advisory ID:** CSENTRY-ADV-002  
**Date:** 2024-04-01  
**Severity:** CRITICAL  
**TLP Classification:** WHITE (Unrestricted)

## Summary

Critical authentication bypass vulnerabilities in widely deployed CI/CD platforms — including JetBrains TeamCity, Jenkins, and GitHub Actions — present a severe supply chain risk. Exploitation of these vulnerabilities allows threat actors to inject malicious code into software build pipelines, potentially compromising downstream customers and supply chain partners.

## Affected Technologies

- **JetBrains TeamCity** (CVE-2024-27198): Authentication bypass allowing unauthenticated admin account creation. CVSS 9.8. Actively exploited by APT29.
- **Jenkins** (CVE-2024-23897): Arbitrary file read from Jenkins controller, exposing credentials and secrets. CVSS 9.8.
- **ConnectWise ScreenConnect** (CVE-2024-1709): Authentication bypass enabling administrative access. CVSS 10.0.

## Supply Chain Risk Context

CI/CD platforms occupy a privileged position in enterprise environments. Compromise of a build server enables attackers to:
- Inject malicious code into compiled software artefacts
- Access source code repositories and intellectual property
- Harvest cloud credentials and API tokens stored as build secrets
- Pivot to production deployment environments
- Compromise downstream customers in managed service provider (MSP) scenarios

**The SolarWinds (SUNBURST) and 3CX supply chain attacks demonstrate the catastrophic downstream impact achievable through CI/CD compromise.**

## MITRE ATT&CK Mapping

| Tactic | Technique | Description |
|--------|-----------|-------------|
| Initial Access | T1190 | Exploit Public-Facing Application |
| Persistence | T1195.002 | Compromise Software Supply Chain |
| Credential Access | T1552.001 | Credentials in Files |
| Collection | T1213 | Data from Information Repositories |
| Exfiltration | T1567 | Exfiltration Over Web Service |
| Impact | T1486 | Data Encrypted for Impact (ransomware) |

## Threat Actor Intelligence

APT29 (SVR) has been confirmed exploiting CVE-2024-27198 in TeamCity to conduct supply chain attacks against defence contractors, technology companies, and government suppliers in NATO member states. The group's post-exploitation toolkit includes:
- **BEACON** implant for persistent C2 communication
- **LAZAGNE** for credential harvesting
- Custom Python scripts for secrets exfiltration from build configuration files

## Detection Opportunities

1. New admin account creation outside normal provisioning workflows
2. REST API calls to `/app/rest/users` without prior authentication
3. Build job creation or modification by unexpected users
4. Unexpected outbound connections from build agents

## Recommended Mitigations

1. **Upgrade immediately**: Apply patches for all affected versions
2. **Network isolation**: Place CI/CD systems behind VPN with strict access controls
3. **Secrets management**: Migrate build secrets to a dedicated secrets vault (HashiCorp Vault, AWS Secrets Manager)
4. **Code signing**: Implement pipeline artefact signing to detect tampering
5. **SBOM**: Generate and validate Software Bill of Materials for all builds
6. **Privileged access review**: Audit all CI/CD service accounts and remove unused credentials

## References

- CISA Advisory AA24-057A: Threat Actors Exploit Multiple Vulnerabilities in Ivanti Connect Secure  
- NCSC Advisory: SVR Targeting of CI/CD Environments  
- JetBrains Security Bulletin: CVE-2024-27198 and CVE-2024-27199
