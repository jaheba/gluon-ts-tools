import sys


def main():
    try:
        import click
    except ImportError:
        print(
            "`click` not installed. Try `pip installl smily[cli]` to ensure all "
            "dependencies are installed."
        )
        sys.exit(1)

    from .cli import main

    main()


if __name__ == "__main__":
    main()
