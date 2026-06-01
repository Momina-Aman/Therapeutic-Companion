"""
Deployment Verification Script for Therapeutic Companion.

Run this to verify all Phase 2 components are properly installed and configured.

Usage:
    python verify_deployment.py
"""

import os
import sys
from pathlib import Path
import importlib


def check_python_version():
    """Verify Python version is 3.9+"""
    version = sys.version_info
    print(f"\n✓ Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("  ⚠️  WARNING: Python 3.9+ recommended")
        return False
    return True


def check_directories():
    """Verify all required directories exist."""
    print("\n📁 Checking Directories:")

    required_dirs = [
        "pages",
        "dataa",
        "logs",
        "user_data"
    ]

    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ⚠️  {dir_name}/ missing (will be created on first use)")

    return True


def check_files():
    """Verify all required files exist."""
    print("\n📄 Checking Files:")

    required_files = [
        "app.py",
        "auth.py",
        "brain.py",
        "ingest.py",
        "styles.py",
        "requirements.txt",
        "pages/01_Companion_Chat.py",
        "pages/02_Activities.py",
        "pages/03_Clinic_Finder.py",
        "README.md",
        "PHASE_2_SETUP.md"
    ]

    all_present = True
    for file_name in required_files:
        file_path = Path(file_name)
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {file_name} ({size:,} bytes)")
        else:
            print(f"  ❌ {file_name} MISSING")
            all_present = False

    return all_present


def check_dependencies():
    """Verify all required packages are installed."""
    print("\n📦 Checking Dependencies:")

    required_packages = {
        "streamlit": "1.28.1",
        "bcrypt": "4.1.1",
        "pandas": "2.1.3",
        "folium": "0.14.0",
        "langchain": "0.1.7",
        "chromadb": "0.4.17",
        "sentence_transformers": "2.2.2",
        "google": "google-generativeai",  # Different import name
    }

    all_installed = True
    for package, version in required_packages.items():
        try:
            mod = importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} NOT INSTALLED")
            all_installed = False

    return all_installed


def check_database():
    """Check if database exists."""
    print("\n💾 Checking Database:")

    db_file = Path("therapeutic_companion.db")
    if db_file.exists():
        size = db_file.stat().st_size
        print(f"  ✓ therapeutic_companion.db exists ({size:,} bytes)")
        return True
    else:
        print(f"  ℹ️  therapeutic_companion.db will be created on first signup")
        return None


def check_vector_store():
    """Check if vector store exists."""
    print("\n🔍 Checking Vector Store:")

    vector_db = Path("./vector_db")
    if vector_db.exists():
        print(f"  ✓ Vector store exists at ./vector_db/")
        try:
            import chromadb
            from chromadb.config import Settings
            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=str(vector_db),
                anonymized_telemetry=False
            )
            client = chromadb.Client(settings)
            collection = client.get_collection(name="therapeutic_companion")
            count = collection.count()
            print(f"  ✓ Collection 'therapeutic_companion' loaded ({count} documents)")
            return True
        except Exception as e:
            print(f"  ⚠️  Could not load collection: {e}")
            print(f"     Run 'python ingest.py' to create vector store")
            return None
    else:
        print(f"  ℹ️  Vector store not found at ./vector_db/")
        print(f"     Run 'python ingest.py' to create it")
        return None


def check_api_key():
    """Check if Google API key is configured."""
    print("\n🔑 Checking API Configuration:")

    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        masked_key = api_key[:7] + "..." + api_key[-4:]
        print(f"  ✓ GOOGLE_API_KEY configured ({masked_key})")
        return True
    else:
        print(f"  ⚠️  GOOGLE_API_KEY not found in environment")
        print(f"     Set it with: $env:GOOGLE_API_KEY='your-key-here'")
        print(f"     Or create .env file with: GOOGLE_API_KEY=your-key-here")
        return None


def check_sample_data():
    """Check if sample data exists."""
    print("\n📊 Checking Sample Data:")

    dataa_dir = Path("./dataa")
    if dataa_dir.exists():
        files = list(dataa_dir.glob("*.*"))
        if files:
            print(f"  ✓ Found {len(files)} data files in ./dataa/")
            for f in files:
                print(f"    - {f.name}")
            return True
        else:
            print(f"  ℹ️  ./dataa/ is empty")
            print(f"     Run 'python generate_sample_data.py' to create samples")
            return None
    else:
        print(f"  ℹ️  ./dataa/ directory not found (will be created)")
        return None


def main():
    """Run all verification checks."""
    print("=" * 80)
    print("🌿 THERAPEUTIC COMPANION - DEPLOYMENT VERIFICATION")
    print("=" * 80)

    results = {
        "Python Version": check_python_version(),
        "Files": check_files(),
        "Directories": check_directories(),
        "Dependencies": check_dependencies(),
        "Database": check_database(),
        "Vector Store": check_vector_store(),
        "API Key": check_api_key(),
        "Sample Data": check_sample_data(),
    }

    print("\n" + "=" * 80)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 80)

    for check_name, result in results.items():
        if result is True:
            status = "✓ READY"
        elif result is None:
            status = "ℹ️  OPTIONAL"
        else:
            status = "❌ NEEDS ATTENTION"
        print(f"{check_name:.<30} {status}")

    print("\n" + "=" * 80)
    print("🚀 NEXT STEPS")
    print("=" * 80)

    if not results["Dependencies"]:
        print("1. Install dependencies: pip install -r requirements.txt")

    if not results["API Key"]:
        print("2. Set API key: $env:GOOGLE_API_KEY='your-key'")

    if not results["Sample Data"]:
        print("3. Generate samples: python generate_sample_data.py")

    if not results["Vector Store"]:
        print("4. Create vector store: python ingest.py")

    print("5. Run app: streamlit run app.py")

    print("\n" + "=" * 80)

    # Return success if critical items are ready
    critical_checks = [
        results["Python Version"],
        results["Files"],
        results["Dependencies"]
    ]

    if all(critical_checks):
        print("✅ SYSTEM READY FOR DEPLOYMENT\n")
        return 0
    else:
        print("⚠️  SYSTEM NOT READY - Please address items above\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
