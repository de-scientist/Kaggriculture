import subprocess
import sys


def main():
    subprocess.run(["pytest", "--cov=agent", "--cov-report=html", "tests/"], check=True)


if __name__ == "__main__":
    main()