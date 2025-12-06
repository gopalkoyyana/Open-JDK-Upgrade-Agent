import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import zipfile
import json
import datetime
import urllib.request
import tempfile
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required for vulnerability checking.")
    print("Install it using: pip install requests")
    sys.exit(1)

class VulnerabilityChecker:
    """Checks for known vulnerabilities in OpenJDK versions using OSV.dev API"""
    
    OSV_API_URL = "https://api.osv.dev/v1/query"
    
    def __init__(self, logger=None):
        self.logger = logger
    
    def log(self, message, level="info"):
        """Log messages if logger is available"""
        if self.logger:
            if level == "info":
                self.logger.info(message)
            elif level == "error":
                self.logger.error(message)
            elif level == "warning":
                self.logger.warning(message)
        else:
            print(f"[{level.upper()}] {message}")
    
    def check_version(self, version):
        """
        Check for vulnerabilities in a specific OpenJDK version.
        
        Args:
            version: The OpenJDK version to check (e.g., "17", "21")
        
        Returns:
            tuple: (has_critical_vulns, vulnerabilities_list)
        """
        self.log(f"Checking for vulnerabilities in OpenJDK {version}...")
        
        # Query OSV.dev for OpenJDK vulnerabilities
        # We'll check multiple package ecosystems that might contain OpenJDK vulnerabilities
        ecosystems = [
            {"ecosystem": "Maven", "name": "org.openjdk:openjdk"},
            {"ecosystem": "Maven", "name": "java"},
        ]
        
        all_vulnerabilities = []
        
        for pkg_info in ecosystems:
            try:
                query = {
                    "package": pkg_info,
                    "version": version
                }
                
                self.log(f"Querying OSV.dev for {pkg_info['ecosystem']}:{pkg_info['name']}...")
                
                response = requests.post(
                    self.OSV_API_URL,
                    json=query,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    vulns = data.get("vulns", [])
                    if vulns:
                        all_vulnerabilities.extend(vulns)
                        self.log(f"Found {len(vulns)} potential vulnerabilities in {pkg_info['ecosystem']}")
                
            except requests.exceptions.RequestException as e:
                self.log(f"Warning: Could not query OSV.dev for {pkg_info}: {e}", level="warning")
                continue
        
        # Also try a general query for OpenJDK
        try:
            # Query by commit/version tag
            query = {
                "commit": f"jdk-{version}"
            }
            
            response = requests.post(
                self.OSV_API_URL,
                json=query,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                vulns = data.get("vulns", [])
                if vulns:
                    all_vulnerabilities.extend(vulns)
        
        except requests.exceptions.RequestException as e:
            self.log(f"Warning: General OpenJDK query failed: {e}", level="warning")
        
        if not all_vulnerabilities:
            self.log(f"✓ No known vulnerabilities found for OpenJDK {version}")
            return False, []
        
        # Analyze vulnerabilities for severity
        critical_vulns = []
        high_vulns = []
        other_vulns = []
        
        for vuln in all_vulnerabilities:
            vuln_id = vuln.get("id", "UNKNOWN")
            summary = vuln.get("summary", "No summary available")
            severity = self._get_severity(vuln)
            
            vuln_info = {
                "id": vuln_id,
                "summary": summary,
                "severity": severity,
                "details": vuln.get("details", ""),
                "references": vuln.get("references", [])
            }
            
            if severity == "CRITICAL":
                critical_vulns.append(vuln_info)
            elif severity == "HIGH":
                high_vulns.append(vuln_info)
            else:
                other_vulns.append(vuln_info)
        
        # Report findings
        total = len(all_vulnerabilities)
        self.log(f"Found {total} total vulnerabilities:")
        self.log(f"  - CRITICAL: {len(critical_vulns)}")
        self.log(f"  - HIGH: {len(high_vulns)}")
        self.log(f"  - OTHER: {len(other_vulns)}")
        
        # Display critical and high vulnerabilities
        for vuln in critical_vulns + high_vulns:
            self.log(f"  [{vuln['severity']}] {vuln['id']}: {vuln['summary']}", level="warning")
        
        has_critical = len(critical_vulns) > 0 or len(high_vulns) > 0
        
        return has_critical, critical_vulns + high_vulns + other_vulns
    
    def _get_severity(self, vuln):
        """Extract severity from vulnerability data"""
        # Check for CVSS score
        severity_info = vuln.get("severity", [])
        if severity_info:
            for sev in severity_info:
                if sev.get("type") == "CVSS_V3":
                    score = sev.get("score")
                    if score:
                        # Parse CVSS score
                        try:
                            # CVSS format: "CVSS:3.1/AV:N/AC:L/..."
                            # We need to calculate or extract the base score
                            # For simplicity, check if HIGH or CRITICAL is mentioned
                            score_str = str(score).upper()
                            if "CRITICAL" in score_str:
                                return "CRITICAL"
                            elif "HIGH" in score_str:
                                return "HIGH"
                        except:
                            pass
        
        # Check database_specific field
        db_specific = vuln.get("database_specific", {})
        severity = db_specific.get("severity", "").upper()
        if severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            return severity
        
        # Check aliases for CVE severity
        aliases = vuln.get("aliases", [])
        for alias in aliases:
            if "CVE-" in alias:
                # Assume CVEs are at least MEDIUM severity
                return "MEDIUM"
        
        return "UNKNOWN"

# Configure logging
def setup_logging(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join(log_dir, f"run_{timestamp}")
    os.makedirs(run_dir)
    
    log_file = os.path.join(run_dir, "commands.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return run_dir

class OpenJDKUpgradeAgent:
    def __init__(self, args, run_dir):
        self.target_version = args.target_version
        self.app_path = args.app_path
        self.dry_run = args.dry_run
        self.backup_dir = args.backup_dir
        self.force = args.force
        self.health_url = args.health_url
        self.run_dir = run_dir
        self.os_type = platform.system().lower()
        self.backup_path = None  # Store backup path for rollback instructions
        self.report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "os": self.os_type,
            "target_version": self.target_version,
            "actions": [],
            "status": "started"
        }

    def log(self, message, level="info"):
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)
        elif level == "warning":
            logging.warning(message)
        
        self.report["actions"].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "level": level,
            "message": message
        })

    def run_command(self, command, check=True, shell=False):
        self.log(f"Executing: {' '.join(command) if isinstance(command, list) else command}")
        if self.dry_run:
            self.log("Dry run: Command skipped.")
            return 0, "Dry run"
        
        try:
            result = subprocess.run(
                command, 
                check=check, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                shell=shell
            )
            self.log(f"Output: {result.stdout}")
            if result.stderr:
                self.log(f"Error Output: {result.stderr}", level="warning")
            return result.returncode, result.stdout
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", level="error")
            self.log(f"Stderr: {e.stderr}", level="error")
            if check:
                raise
            return e.returncode, e.stderr

    def detect_current_java(self):
        self.log("Detecting current Java installation...")
        java_home = os.environ.get('JAVA_HOME')
        if java_home:
            self.log(f"Found JAVA_HOME: {java_home}")
        
        try:
            code, output = self.run_command(["java", "-version"], check=False)
            if code == 0:
                self.log(f"Current Java version output:\n{output}")
            else:
                self.log("Java not found in PATH.", level="warning")
        except Exception as e:
            self.log(f"Error checking java version: {e}", level="error")

        return java_home

    def backup_java(self, java_home):
        if not java_home or not os.path.exists(java_home):
            self.log("No JAVA_HOME to backup or path does not exist.", level="warning")
            return

        self.log(f"Backing up {java_home} to {self.backup_dir}...")
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"openjdk_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if self.dry_run:
            self.log(f"Dry run: Would backup {java_home} to {backup_path}.zip/tar.gz")
            return

        try:
            if self.os_type == 'windows':
                shutil.make_archive(backup_path, 'zip', java_home)
                self.backup_path = f"{backup_path}.zip"
                self.log(f"Backup created at {self.backup_path}")
            else:
                with tarfile.open(f"{backup_path}.tar.gz", "w:gz") as tar:
                    tar.add(java_home, arcname=os.path.basename(java_home))
                self.backup_path = f"{backup_path}.tar.gz"
                self.log(f"Backup created at {self.backup_path}")
        except Exception as e:
            self.log(f"Backup failed: {e}", level="error")
            raise

    def install_openjdk(self):
        self.log(f"Attempting to install OpenJDK {self.target_version}...")
        
        # Strategy 1: Package Manager
        if self.try_package_manager_install():
            return

        # Strategy 2: Manual Install (Side-install)
        self.manual_install()

    def try_package_manager_install(self):
        self.log("Checking for system package managers...")
        
        if self.os_type == 'linux':
            # Check for apt, yum, dnf
            if shutil.which('apt-get'):
                self.log("Detected apt-get. Attempting install...")
                # Need to map target version to package name, e.g., openjdk-17-jdk
                pkg_name = f"openjdk-{self.target_version}-jdk"
                try:
                    self.run_command(["sudo", "apt-get", "update"], check=False)
                    self.run_command(["sudo", "apt-get", "install", "-y", pkg_name])
                    return True
                except Exception as e:
                    self.log(f"Apt install failed: {e}", level="warning")
            
            elif shutil.which('yum'):
                self.log("Detected yum. Attempting install...")
                pkg_name = f"java-{self.target_version}-openjdk-devel"
                try:
                    self.run_command(["sudo", "yum", "install", "-y", pkg_name])
                    return True
                except Exception as e:
                    self.log(f"Yum install failed: {e}", level="warning")

        elif self.os_type == 'darwin': # macOS
            if shutil.which('brew'):
                self.log("Detected Homebrew. Attempting install...")
                # brew install openjdk@17
                pkg_name = f"openjdk@{self.target_version}"
                try:
                    self.run_command(["brew", "install", pkg_name])
                    return True
                except Exception as e:
                    self.log(f"Brew install failed: {e}", level="warning")

        elif self.os_type == 'windows':
            if shutil.which('choco'):
                self.log("Detected Chocolatey. Attempting install...")
                # choco upgrade openjdk --version ... (Chocolatey versions might differ)
                # Usually 'openjdk' package exists.
                try:
                    self.run_command(["choco", "upgrade", "openjdk", "--version", self.target_version, "-y"])
                    return True
                except Exception as e:
                    self.log(f"Chocolatey install failed: {e}", level="warning")
            
            if shutil.which('winget'):
                self.log("Detected Winget. Attempting install...")
                try:
                    # simplistic winget call
                    self.run_command(["winget", "install", "-e", "--id", "Microsoft.OpenJDK", "-v", self.target_version])
                    return True
                except Exception as e:
                    self.log(f"Winget install failed: {e}", level="warning")

        self.log("No suitable package manager found or installation failed.")
        return False

    def manual_install(self):
        self.log("Falling back to manual installation (Side-install)...")
        
        # Determine architecture
        machine = platform.machine().lower()
        if machine in ['x86_64', 'amd64']:
            arch = 'x64'
        elif machine in ['aarch64', 'arm64']:
            arch = 'aarch64'
        else:
            self.log(f"Unsupported architecture: {machine}", level="error")
            return
        
        # Map OS type to Adoptium API format
        os_map = {
            'linux': 'linux',
            'darwin': 'mac',
            'windows': 'windows'
        }
        
        os_name = os_map.get(self.os_type)
        if not os_name:
            self.log(f"Unsupported OS for manual install: {self.os_type}", level="error")
            return
        
        # Construct Adoptium API URL
        api_url = f"https://api.adoptium.net/v3/assets/latest/{self.target_version}/hotspot"
        self.log(f"Querying Adoptium API: {api_url}")
        
        try:
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                
            # Find the right binary for our OS and architecture
            download_url = None
            for asset in data:
                binary = asset.get('binary', {})
                if (binary.get('os') == os_name and 
                    binary.get('architecture') == arch and
                    binary.get('image_type') == 'jdk'):
                    download_url = binary.get('package', {}).get('link')
                    break
            
            if not download_url:
                self.log("Could not find suitable OpenJDK binary from Adoptium.", level="error")
                return
            
            self.log(f"Found download URL: {download_url}")
            
            if self.dry_run:
                self.log("Dry run: Would download and install from URL")
                return
            
            # Download the binary
            filename = download_url.split('/')[-1]
            download_path = os.path.join(tempfile.gettempdir(), filename)
            
            self.log(f"Downloading to {download_path}...")
            urllib.request.urlretrieve(download_url, download_path)
            self.log("Download complete.")
            
            # Extract and install
            install_dir = f"/opt/openjdk-{self.target_version}" if self.os_type != 'windows' else f"C:\\Program Files\\OpenJDK\\jdk-{self.target_version}"
            
            self.log(f"Extracting to {install_dir}...")
            if filename.endswith('.tar.gz'):
                with tarfile.open(download_path, 'r:gz') as tar:
                    tar.extractall(install_dir)
            elif filename.endswith('.zip'):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(install_dir)
            
            self.log(f"OpenJDK {self.target_version} installed to {install_dir}")
            self.log(f"You may need to update JAVA_HOME to {install_dir}")
            
        except Exception as e:
            self.log(f"Manual installation failed: {e}", level="error")

    def verify_installation(self):
        self.log("Verifying installation...")
        # Check if java -version returns the target version
        code, output = self.run_command(["java", "-version"], check=False)
        if self.target_version in output:
            self.log("Verification SUCCESS: Target version found in output.")
        else:
            self.log("Verification WARNING: Target version not found in 'java -version' output. You may need to update PATH.", level="warning")

    def health_check(self):
        if not self.health_url:
            self.log("No health URL provided, skipping health check.")
            return
        
        self.log(f"Running health check against {self.health_url}...")
        
        if self.dry_run:
            self.log("Dry run: Would perform health check")
            return
        
        try:
            # Simple connectivity check
            import socket
            host = self.health_url.replace('https://', '').replace('http://', '').split('/')[0]
            port = 443 if 'https' in self.health_url else 80
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                self.log(f"Health check PASSED: Successfully connected to {host}:{port}")
            else:
                self.log(f"Health check FAILED: Could not connect to {host}:{port}", level="warning")
        except Exception as e:
            self.log(f"Health check error: {e}", level="error")

    def generate_report(self):
        report_file = os.path.join(self.run_dir, "README.md")
        with open(report_file, "w") as f:
            f.write(f"# OpenJDK Upgrade Report\n\n")
            f.write(f"**Timestamp:** {self.report['timestamp']}\n")
            f.write(f"**Target Version:** {self.target_version}\n")
            f.write(f"**OS:** {self.os_type}\n")
            f.write(f"**Status:** {self.report['status']}\n\n")
            
            # Rollback instructions
            if self.backup_path:
                f.write("## Rollback Instructions\n\n")
                f.write(f"If you need to rollback this upgrade, restore from the backup:\n\n")
                f.write(f"**Backup Location:** `{self.backup_path}`\n\n")
                if self.os_type == 'windows':
                    f.write("Extract the ZIP file to restore the previous JAVA_HOME directory.\n\n")
                else:
                    f.write("```bash\n")
                    f.write(f"tar -xzf {self.backup_path} -C /path/to/restore\n")
                    f.write("```\n\n")
            
            f.write("## Actions Log\n\n")
            for action in self.report["actions"]:
                f.write(f"*   **{action['timestamp']}** [{action['level'].upper()}]: {action['message']}\n")
        
        self.log(f"Report generated at {report_file}")

    def detect_dependencies(self):
        if not self.app_path or not os.path.exists(self.app_path):
            self.log("No application path provided or path does not exist. Skipping dependency detection.")
            return []

        self.log(f"Analyzing dependencies for {self.app_path}...")
        dependencies = []

        if self.os_type == 'linux':
            if shutil.which('ldd'):
                code, output = self.run_command(["ldd", self.app_path], check=False)
                if code == 0:
                    for line in output.splitlines():
                        if "=>" in line:
                            parts = line.split("=>")
                            if len(parts) > 1:
                                lib_path = parts[1].strip().split(" ")[0]
                                if lib_path and os.path.exists(lib_path):
                                    dependencies.append(lib_path)
        elif self.os_type == 'darwin':
            if shutil.which('otool'):
                code, output = self.run_command(["otool", "-L", self.app_path], check=False)
                if code == 0:
                    for line in output.splitlines()[1:]: # Skip first line (file name)
                        lib_path = line.strip().split(" ")[0]
                        if lib_path and os.path.exists(lib_path):
                            dependencies.append(lib_path)
        elif self.os_type == 'windows':
            # Try dumpbin (Visual Studio tool)
            if shutil.which('dumpbin'):
                code, output = self.run_command(["dumpbin", "/DEPENDENTS", self.app_path], check=False)
                if code == 0:
                    in_deps_section = False
                    for line in output.splitlines():
                        if "dependencies:" in line.lower():
                            in_deps_section = True
                            continue
                        if in_deps_section and line.strip().endswith('.dll'):
                            dependencies.append(line.strip())
            else:
                # Fallback: Use PowerShell to check DLL dependencies
                ps_cmd = f"Get-Command '{self.app_path}' | Select-Object -ExpandProperty FileVersionInfo | Select-Object -ExpandProperty FileName"
                code, output = self.run_command(["powershell", "-Command", ps_cmd], check=False, shell=True)
                if code == 0:
                    self.log("Windows dependency detection limited without dumpbin. Consider installing Visual Studio Build Tools.", level="warning")
        
        self.log(f"Found {len(dependencies)} dependencies.")
        return dependencies

    def resolve_packages(self, dependencies):
        packages = set()
        if self.os_type == 'linux':
            if shutil.which('dpkg'): # Debian/Ubuntu
                for dep in dependencies:
                    code, output = self.run_command(["dpkg", "-S", dep], check=False)
                    if code == 0:
                        # Output format: "package: /path/to/file"
                        pkg = output.split(":")[0]
                        packages.add(pkg)
            elif shutil.which('rpm'): # RHEL/CentOS
                for dep in dependencies:
                    code, output = self.run_command(["rpm", "-qf", dep], check=False)
                    if code == 0:
                        packages.add(output.strip())
        elif self.os_type == 'darwin':
            # Use Homebrew to find packages
            if shutil.which('brew'):
                for dep in dependencies:
                    # Extract library name from path like /usr/local/Cellar/openssl/1.1.1/lib/libssl.dylib
                    if '/Cellar/' in dep:
                        parts = dep.split('/Cellar/')
                        if len(parts) > 1:
                            pkg_name = parts[1].split('/')[0]
                            packages.add(pkg_name)
        elif self.os_type == 'windows':
            # Windows DLL resolution is complex - typically managed by Chocolatey or manual installs
            # For now, just log the DLLs found
            self.log(f"Windows dependencies found: {', '.join(dependencies)}")
            self.log("Windows package resolution requires manual review or Chocolatey package names.", level="warning")
        
        return list(packages)

    def upgrade_dependencies(self, packages):
        if not packages:
            self.log("No packages identified for upgrade.")
            return

        self.log(f"The following packages were identified as dependencies: {', '.join(packages)}")
        
        if self.dry_run:
            self.log("Dry run: Would ask for confirmation and upgrade packages.")
            return

        # User consent
        if not self.force:
            print(f"Do you want to upgrade these {len(packages)} packages? (y/n): ", end='', flush=True)
            response = sys.stdin.readline().strip()
            if response.lower() != 'y':
                self.log("User skipped dependency upgrade.")
                return

        self.log("Upgrading packages...")
        if self.os_type == 'linux':
            if shutil.which('apt-get'):
                self.run_command(["sudo", "apt-get", "install", "--only-upgrade", "-y"] + packages, check=False)
            elif shutil.which('yum'):
                self.run_command(["sudo", "yum", "update", "-y"] + packages, check=False)
        elif self.os_type == 'darwin':
            if shutil.which('brew'):
                for pkg in packages:
                    self.run_command(["brew", "upgrade", pkg], check=False)
        elif self.os_type == 'windows':
            if shutil.which('choco'):
                for pkg in packages:
                    self.run_command(["choco", "upgrade", pkg, "-y"], check=False)
            else:
                self.log("Chocolatey not found. Cannot upgrade packages automatically on Windows.", level="warning")
        
        self.log("Dependency upgrade process finished.")

    def run(self):
        try:
            # CRITICAL: Check for vulnerabilities BEFORE any operations
            self.log("=" * 60)
            self.log("VULNERABILITY CHECK - Querying OSV.dev database...")
            self.log("=" * 60)
            
            vuln_checker = VulnerabilityChecker(logger=logging.getLogger())
            has_critical, vulnerabilities = vuln_checker.check_version(self.target_version)
            
            if has_critical:
                self.log("=" * 60, level="error")
                self.log("CRITICAL SECURITY ALERT!", level="error")
                self.log("=" * 60, level="error")
                self.log(f"OpenJDK version {self.target_version} has CRITICAL or HIGH severity vulnerabilities!", level="error")
                self.log("The upgrade process has been ABORTED for your security.", level="error")
                self.log("", level="error")
                self.log("Vulnerabilities found:", level="error")
                
                for vuln in vulnerabilities:
                    if vuln['severity'] in ['CRITICAL', 'HIGH']:
                        self.log(f"  - [{vuln['severity']}] {vuln['id']}", level="error")
                        self.log(f"    Summary: {vuln['summary']}", level="error")
                        if vuln.get('references'):
                            self.log(f"    References: {vuln['references'][0].get('url', 'N/A')}", level="error")
                
                self.log("", level="error")
                self.log("RECOMMENDATION: Choose a different OpenJDK version without known vulnerabilities.", level="error")
                self.log("=" * 60, level="error")
                
                self.report["status"] = "aborted_due_to_vulnerabilities"
                self.report["vulnerabilities"] = vulnerabilities
                
                # Generate report even on abort
                self.generate_report()
                
                # Exit with error code
                sys.exit(1)
            
            self.log("=" * 60)
            self.log(f"✓ Security check passed for OpenJDK {self.target_version}")
            self.log("=" * 60)
            
            # Proceed with normal operations
            current_java_home = self.detect_current_java()
            
            if self.backup_dir:
                self.backup_java(current_java_home)
            
            self.install_openjdk()
            self.verify_installation()
            self.health_check()
            
            if self.app_path:
                deps = self.detect_dependencies()
                pkgs = self.resolve_packages(deps)
                self.upgrade_dependencies(pkgs)
            
            self.report["status"] = "completed"
        except Exception as e:
            self.log(f"Agent run failed: {e}", level="error")
            self.report["status"] = "failed"
        finally:
            self.generate_report()

def main():
    parser = argparse.ArgumentParser(description="OpenJDK Upgrade Agent")
    parser.add_argument("--target-version", required=True, help="Target OpenJDK version (e.g., 17, 21)")
    parser.add_argument("--app-path", help="Path to application to inspect")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without changes")
    parser.add_argument("--backup-dir", default="temp/openjdk-backups", help="Directory for backups")
    parser.add_argument("--log-dir", default="temp/openjdk-agent-logs", help="Directory for logs")
    parser.add_argument("--health-url", help="URL for health check")
    parser.add_argument("--force", action="store_true", help="Force actions")

    args = parser.parse_args()

    run_dir = setup_logging(args.log_dir)
    agent = OpenJDKUpgradeAgent(args, run_dir)
    agent.run()

if __name__ == "__main__":
    main()
