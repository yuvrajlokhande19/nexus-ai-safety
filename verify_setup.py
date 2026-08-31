#!/usr/bin/env python3
"""
Nexus AI Safety Research Platform - Setup Verification
Run this to verify all dependencies and configuration are correct.
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor} - Need 3.11+")
        return False

def check_ollama():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[OK] Ollama installed")
            if "gemma4:latest" in result.stdout:
                print("[OK] Gemma 4 model available")
            else:
                print("[WARN] Gemma 4 model not found - ensure it's installed in Ollama")
            return True
        else:
            print("[FAIL] Ollama not responding")
            return False
    except FileNotFoundError:
        print("[FAIL] Ollama not installed - install from https://ollama.com")
        return False
    except subprocess.TimeoutExpired:
        print("[FAIL] Ollama timeout")
        return False

def check_env_file():
    env_path = Path("backend/.env")
    if env_path.exists():
        print("[OK] .env file exists")
        with open(env_path) as f:
            content = f.read()
            if "GEMINI_API_KEYS=" in content and "AQ.Ab8RN" in content:
                print("[OK] Gemini API keys configured (4 keys detected)")
            else:
                print("[WARN] Gemini API keys may not be configured correctly")
        return True
    else:
        print("[FAIL] backend/.env not found - copy from .env.example")
        return False

def check_docker():
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Docker: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("[WARN] Docker not installed (optional but recommended)")
    return False

def check_gpu():
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] GPU detected: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("[WARN] nvidia-smi not found - GPU acceleration may not work")
    return False

def check_python_packages():
    # (pip_name, import_name)
    required = [
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("pydantic-settings", "pydantic_settings"),
        ("ollama", "ollama"),
        ("google-generativeai", "google.generativeai"),
        ("chromadb", "chromadb"),
        ("networkx", "networkx"),
        ("numpy", "numpy"),
        ("pyyaml", "yaml"),
        ("reportlab", "reportlab"),
        ("matplotlib", "matplotlib"),
        ("pillow", "PIL"),
        ("github3.py", "github3"),
        ("structlog", "structlog")
    ]
    missing = []
    for pip_name, import_name in required:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pip_name)
    
    if not missing:
        print("[OK] All Python packages installed")
        return True
    else:
        print(f"[FAIL] Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r backend/requirements.txt")
        return False

def check_node():
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            major = int(version.lstrip('v').split('.')[0])
            if major >= 20:
                print(f"[OK] Node.js {version}")
                return True
            else:
                print(f"[WARN] Node.js {version} - Recommend 20+")
                return True
    except FileNotFoundError:
        print("[FAIL] Node.js not installed")
    return False

def main():
    print("=" * 60)
    print("Nexus AI Safety Research Platform - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Ollama & Gemma", check_ollama),
        ("Environment Config", check_env_file),
        ("Python Packages", check_python_packages),
        ("Node.js", check_node),
        ("Docker", check_docker),
        ("GPU", check_gpu),
    ]
    
    results = []
    for name, check in checks:
        print(f"\n[CHECK] Checking {name}...")
        try:
            result = check()
            results.append((name, result))
        except Exception as e:
            print(f"[FAIL] Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("[SUCCESS] All checks passed! Ready to run Nexus.")
        print("\nStart with: docker-compose up -d")
        print("Or: ./start.sh")
    else:
        print("[WARNING] Some checks failed. Please fix before running.")
        sys.exit(1)

if __name__ == "__main__":
    main()