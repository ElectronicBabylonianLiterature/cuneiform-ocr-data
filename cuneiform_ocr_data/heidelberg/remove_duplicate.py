from pathlib import Path

if __name__ == "__main__":
    """
    Read all files in path and delete duplicate lines
    """
    path = Path("../../data/processed-data/heidelberg-merged/annotations")
    for file in path.iterdir():
        lines = open(file).readlines()
        lines_unique = list(set(lines))
        if len(lines) != len(lines_unique):
            print(f"File {file} has duplicate lines")
            with open(file, "w") as f:
                f.writelines(lines_unique)
