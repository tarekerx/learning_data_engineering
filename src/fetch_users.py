import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from dotenv import load_dotenv

load_dotenv()

def main( ) -> None:
    api_url = os.getenv("USERS_API_URL")

    if not api_url:
        print("USERS_API_URL is not configured")
        return


    headers = {
        "Accept": "application/json",
    }


    request = Request(
        api_url,
        headers=headers,
        method="GET",
    )

    try:
        with urlopen(request, timeout=10) as response:
            users = json.load(response)

        if not isinstance(users, list):
            raise ValueError("Expected the API response to be a list")

        output_path = Path("data/users.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(users, file, indent=2)

        print(f"Retrieved {len(users)} customer records")
        print(f"Saved API response to {output_path}")

    except HTTPError as error:
        print(f"API returned HTTP {error.code}: {error.reason}")

    except URLError as error:
        print(f"Could not reach API: {error.reason}")

    except TimeoutError:
        print("The API request timed out")

    except ValueError as error:
        print(f"Invalid API response: {error}")



if __name__ == "__main__":
    main()
