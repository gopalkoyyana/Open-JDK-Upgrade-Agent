# Changelog

All notable changes to the OpenJDK Upgrade Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-06

### Added - CRITICAL SECURITY FEATURE

- **Vulnerability Check**: Integrated automatic security vulnerability checking using the OSV.dev (Open Source Vulnerabilities) database
  - Queries OSV.dev API before any download or upgrade operation
  - Checks for CRITICAL and HIGH severity vulnerabilities in the target OpenJDK version
  - **Automatically aborts** the upgrade process if critical vulnerabilities are detected
  - Works in both normal and dry-run modes
  - Provides detailed vulnerability information including:
    - Vulnerability ID (CVE, GHSA, etc.)
    - Severity level
    - Summary and details
    - References for more information
  - Generates comprehensive reports including vulnerability data
  
- **VulnerabilityChecker Class**: New dedicated class for security checks
  - Queries multiple package ecosystems (Maven, etc.)
  - Intelligent severity detection from CVSS scores and database metadata
  - Robust error handling for API connectivity issues
  
- **requirements.txt**: Added Python dependencies file
  - `requests>=2.31.0` for API communication

### Changed

- **README.md**: Updated with comprehensive vulnerability check documentation
  - Added vulnerability check to features list
  - Updated prerequisites to include `requests` library
  - Added detailed vulnerability check section with usage examples
  - Updated installation instructions
  
- **Agent Workflow**: Modified to prioritize security
  - Vulnerability check now runs as the **first step** before any operations
  - Process exits with error code 1 if vulnerabilities are found
  - Enhanced logging with clear security alerts

### Security

- **Protection Against Known Vulnerabilities**: The agent now prevents installation of OpenJDK versions with known CRITICAL or HIGH severity security issues
- **Proactive Security**: Users are protected even during dry-run operations
- **Transparency**: All vulnerability findings are logged and reported

### Testing

- **test_vulnerability_check.py**: New comprehensive test suite
  - Tests API connectivity to OSV.dev
  - Validates severity detection logic
  - Tests multiple OpenJDK versions (8, 11, 17, 21, 23)
  - Provides detailed test reports

## [1.0.0] - 2025-11-30

### Added

- Initial release of OpenJDK Upgrade Agent
- Cross-platform support (Linux, macOS, Windows)
- Automatic detection of existing Java installations
- Backup functionality for existing JAVA_HOME
- Smart upgrade using package managers (apt, yum, brew, choco, winget)
- Manual installation fallback using Adoptium API
- Dependency analysis for applications
- Dependency upgrade with user confirmation
- Health check functionality
- Comprehensive logging and reporting
- Dry-run mode for safe testing

### Features

- Detection of current Java/OpenJDK installations
- Dependency analysis using ldd, otool, dumpbin
- Automated backup before upgrades
- Package manager integration
- Verification and health checks
- Detailed run reports

---

## Version History Summary

- **v2.0.0** (2025-12-06): Added critical vulnerability checking feature
- **v1.0.0** (2025-11-30): Initial release with core upgrade functionality
