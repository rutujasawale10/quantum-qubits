"""
Environment Check Script for SIH26141 QDS Security Prototype
"""
import sys
import importlib.metadata

def check_environment():
    packages = [
        ("Python", None),
        ("qiskit", "Qiskit"),
        ("streamlit", "Streamlit"),
        ("numpy", "NumPy"),
        ("scipy", "SciPy")
    ]

    print("==================================================")
    print("PROTOTYPE ENVIRONMENT CHECK")
    print("==================================================")
    print(f"{'Package':<15} | {'Installed Version':<20} | {'Status':<10}")
    print("-" * 50)

    all_ok = True

    # Check Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"{'Python':<15} | {py_ver:<20} | {'PASS':<10}")

    for mod_name, disp_name in packages[1:]:
        try:
            ver = importlib.metadata.version(mod_name)
            status = "PASS"
        except Exception:
            try:
                mod = __import__(mod_name)
                ver = getattr(mod, "__version__", "Available")
                status = "PASS"
            except Exception:
                ver = "Not installed / unavailable"
                status = "FAIL"
                all_ok = False

        print(f"{disp_name:<15} | {ver:<20} | {status:<10}")

    print("=" * 50)
    if all_ok:
        print("ENVIRONMENT CHECK PASSED")
    else:
        print("ENVIRONMENT CHECK FAILED — MISSING DEPENDENCIES")
    
    return all_ok

if __name__ == "__main__":
    ok = check_environment()
    sys.exit(0 if ok else 1)
