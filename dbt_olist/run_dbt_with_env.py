"""
Run dbt with env vars loaded from project .env so POSTGRES_PASSWORD is set.
Usage (from repo root or dbt_olist):  python dbt_olist/run_dbt_with_env.py run
                                       python dbt_olist/run_dbt_with_env.py test
"""
import os
import subprocess
import sys

# Project root (parent of dbt_olist)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(ROOT, ".env")

def load_dotenv():
    if not os.path.isfile(ENV_FILE):
        return
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                elif v.startswith("'") and v.endswith("'"):
                    v = v[1:-1]
                os.environ[k] = v

def main():
    load_dotenv()
    cmd = ["dbt"] + sys.argv[1:]
    sys.exit(subprocess.run(cmd, cwd=os.path.dirname(__file__)).returncode)

if __name__ == "__main__":
    main()
