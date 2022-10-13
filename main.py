import pathlib
from pprint import pprint
from typing import Any, Dict, List, Optional

import requests
from environs import Env
from tqdm import tqdm

env = Env()
env_file = pathlib.Path(__file__).parent / ".env"

if env_file.exists():
    env.read_env()

API_KEY: str = env("API_KEY")
BASE_URL: str = env("BASE_URL")

API_HEADERS = {
    "Authorization": f"token {API_KEY}",
}


class APIClient:
    def problems(self) -> List[Dict[str, Any]]:
        res = requests.get(
            f"{BASE_URL}/problem/problems",
            headers=API_HEADERS,
        )
        res.raise_for_status()
        return res.json()

    def problem(self, pk: str) -> Dict[str, Any]:
        res = requests.get(
            f"{BASE_URL}/problem/problems/{pk}",
            headers=API_HEADERS,
        )
        res.raise_for_status()
        return res.json()

    def download(
        self,
        pk: str,
        file_name: Optional[str] = None,
        path: Optional[str] = None,
    ) -> None:
        res = requests.get(
            f"{BASE_URL}/problem/problems/{pk}/download",
            headers=API_HEADERS,
            stream=True,
        )
        res.raise_for_status()
        if not path:
            path = pathlib.Path(__file__).parent

        if not file_name:
            problem_data = self.problem(pk)
            short_name = problem_data["short_name"]
            file_name = f"{short_name}.zip".replace("-", "").lower()
        else:
            file_name = file_name.replace(".zip", "").lower().strip() + ".zip"

        with tqdm.wrapattr(
            open(path / file_name, "wb"),
            "write",
            miniters=1,
            desc=file_name,
            total=int(res.headers.get("content-length", 0)),
        ) as fout:
            for chunk in res.iter_content(chunk_size=4096):
                fout.write(chunk)


if __name__ == "__main__":
    print("Functions:")
    print("(1)\t Show all problems.")
    print("(2)\t Get a problem by problem id.")
    print("(3)\t Download problem zip file by problem id.")
    print("-" * 50)
    function_key = input("Enter function:")
    if function_key not in {"1", "2", "3"}:
        function_key = "1"
    else:
        function_key = function_key.strip()[0]

    client = APIClient()

    if function_key == "3":
        problem_id = input("* Enter problem id:")

        assert problem_id, "Fail problem id."

        file_name = input("Enter file name:")
        path = input("Enter file path:")

        client.download(problem_id, file_name, path)
    elif function_key == "2":
        problem_id = input("* Enter problem id:")

        assert problem_id, "Fail problem id."
        data = client.problem(problem_id)
        pprint(data)
    else:
        data = client.problems()
        pprint(data)
