import subprocess
import sys


def main():
    subprocess.run(["ruff", "check", "agent/", "tests/", "scripts/"], check=True)


if __name__ == "__main__":
    main()