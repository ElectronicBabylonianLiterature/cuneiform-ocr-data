from pathlib import Path

from cuneiform_ocr_data.utils import create_directory

if __name__ == "__main__":
    """
    Merge files from temp/heidelberg/annotations and temp/heidelberg-xml/annotations
    and save them at temp/heidelberg/annotations_merged
    """
    original_files_path = Path("../../data/processed-data/heidelberg/annotations")
    refined_files_path = Path("../../data/processed-data/heidelberg/heidelberg-xml/annotations")
    write_path = Path("../../data/processed-data/heidelberg/heidelberg-merged/annotations")
    create_directory(write_path, overwrite=True)
    refined_files = list([elem.stem for elem in refined_files_path.iterdir()])
    for file in original_files_path.iterdir():
        file_content = open(file).read().rstrip() + "\n"
        # find file with same filename in temp/heidelberg-xml/annotations
        _refined_files = [f for f in refined_files if file.stem == f.split("-v")[0]]
        for refined_file in _refined_files:
            refined_files.remove(refined_file)
            file_content += (
                open(refined_files_path / f"{refined_file}.txt").read() + "\n"
            )
        with open(write_path / file.name, "w") as f:
            f.write(file_content)
    print(f"Following Files were not merged from 'heidelberg-xml' {refined_files}")
