from pathlib import Path


class Load:

    def __init__(self):

        self.base = Path(__file__).resolve().parent.parent

    def save(self, dataframe, filename):

        folder = self.base / "datasets" / "final"

        folder.mkdir(exist_ok=True)

        dataframe.to_csv(folder / filename, index=False)

        print(f"{filename} saved successfully.")