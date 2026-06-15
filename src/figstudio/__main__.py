"""Command-line entrypoint for lightweight smoke testing."""

from figstudio.session import open


def main() -> None:
    session = open({}, open_browser=False)
    print(session.url)


if __name__ == "__main__":
    main()
