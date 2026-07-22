__version__ = "0.0.1"


def print_version() -> None:
    """Print the current app version, then return (the app exits after)."""
    print(f"v{__version__}")


def main() -> None:
    print_version()


if __name__ == "__main__":
    main()
