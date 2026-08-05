import subprocess
import sys


def main():
    subprocess.run(["black", "agent/", "tests/", "scripts/"], check=True)
    subprocess.run(["ruff", "format", "agent/", "tests/", "scripts/"], check=True)


if __name__ == "__main__":
    main()