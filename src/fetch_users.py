import json
import os
from urllib.request import Request, urlopen


def main( ) -> None:
    api_url = os.environ["USERS_API_URL"]

    request = Request(
        api_url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    with urlopen(request, timeout=10) as response:
        users = json.load(response)

    print(f"Retrieved {len(users)} customer records")


if __name__ == "__main__":
    main()
