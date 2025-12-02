"""
Test suite for OpenJDK Upgrade Agent
Run this to validate the agent functionality
"""

import subprocess
import sys
import os
import platform

def run_test(description, command, expected_in_output=None, should_fail=False):
    """Run a test command and validate output"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\nReturn Code: {result.returncode}")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout[:500]}")
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr[:500]}")
        
        # Validate
        if should_fail:
            if result.returncode != 0:
                print("✓ PASSED - Command failed as expected")
                return True
            else:
                print("✗ FAILED - Command should have failed but succeeded")
                return False
        else:
            if result.returncode == 0:
                if expected_in_output:
                    if expected_in_output in result.stdout or expected_in_output in result.stderr:
                        print(f"✓ PASSED - Found expected output: {expected_in_output}")
                        return True
                    else:
                        print(f"✗ FAILED - Expected output not found: {expected_in_output}")
                        return False
                else:
                    print("✓ PASSED - Command succeeded")
                    return True
            else:
                print(f"✗ FAILED - Command failed with code {result.returncode}")
                return False
                
    except subprocess.TimeoutExpired:
        print("✗ FAILED - Command timed out")
        return False
    except Exception as e:
        print(f"✗ FAILED - Exception: {e}")
        return False

def main():
    print("="*60)
    print("OpenJDK Upgrade Agent - Test Suite")
    print("="*60)
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Help message
    if run_test(
        "Display help message",
        "python openjdk_upgrade_agent.py --help",
        expected_in_output="OpenJDK Upgrade Agent"
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 2: Dry run with version 17
    if run_test(
        "Dry run for OpenJDK 17",
        "python openjdk_upgrade_agent.py --target-version 17 --dry-run",
        expected_in_output="Dry run"
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 3: Dry run with health check
    if run_test(
        "Dry run with health check",
        "python openjdk_upgrade_agent.py --target-version 17 --dry-run --health-url google.com",
        expected_in_output="health check"
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 4: Missing required argument (should fail)
    if run_test(
        "Missing target version (should fail)",
        "python openjdk_upgrade_agent.py --dry-run",
        should_fail=True
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: Custom directories
    if run_test(
        "Custom backup and log directories",
        "python openjdk_upgrade_agent.py --target-version 17 --dry-run --backup-dir ./test-backup --log-dir ./test-logs",
        expected_in_output="Dry run"
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 6: Dry run with non-existent app path
    if run_test(
        "Non-existent app path",
        "python openjdk_upgrade_agent.py --target-version 17 --dry-run --app-path /nonexistent/path",
        expected_in_output="does not exist"
    ):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Total Tests: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n✗ {tests_failed} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
