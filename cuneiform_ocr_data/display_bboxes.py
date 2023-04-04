import sys
from pathlib import Path
from typing import Union

import matplotlib

from cuneiform_ocr_data.bounding_boxes import BoundingBoxesContainer

from cuneiform_ocr_data.validate_data import is_valid_file_size

matplotlib.use("tkAgg")
from matplotlib import pyplot as plt
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
files_to_delete = []
finished = []
nearly_finished = []
medium_quality = []
bad_quality = []
manuel_fixing = []


def display_bboxes(
    first: Path,
    second: Union[Path, str] = "imgs",
    third: Union[Path, str] = "annotations",
) -> None:
    """
    Either two file paths or directory with subfolder names (optional)
    Args:
      first: data_directory or image_file_path
      second: subfolder_name of images_directory in data_directory or annotations_file_path
      third: subfolder_name of annotations_directory in data_directory

    """
    if first.is_file():
        assert isinstance(second, Path)
        assert second.is_file()
        show_img(first, second)
    elif first.is_dir():
        imgs_path = first / second
        annotations_path = first / third
        show_all_in_dir(imgs_path, annotations_path)
    else:
        raise ValueError(
            "arguments have to be either one directories with optional subfolder names or both single files"
        )


def show_all_in_dir(img_path: Path, annotations_path: Path) -> None:
    for image in img_path.iterdir():
        annotation = next(annotations_path.glob(f"gt_{image.stem}.txt"), None)
        if not annotation:
            raise FileNotFoundError(
                f"No annotations text file found corresponding to image: '{image.name}'"
            )
        show_img(image, annotation)


def on_press(image_path: Path):
    def on_press_(event):
        sys.stdout.flush()
        if event.key == "y":
            finished.append(image_path.stem)
        elif event.key == "a":
            manuel_fixing.append(image_path.stem)
        elif event.key == "escape":
            quit()
        else:
            if event.key == "q":
                nearly_finished.append(image_path.stem)
            elif event.key == "w":
                medium_quality.append(image_path.stem)
            elif event.key == "e":
                bad_quality.append(image_path.stem)
            files_to_delete.append(image_path.stem)
        plt.close()

    return on_press_


def plot_bbox_with_img(image_path: Path, gt_path: Path) -> None:
    bbox_containers = BoundingBoxesContainer.from_file(gt_path)
    image = Image.open(image_path)
    image = np.asarray(image)
    fig, ax = plt.subplots(frameon=False)
    DPI = 300
    fig.set_size_inches(image.shape[1] / DPI, image.shape[0] / DPI)
    ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    ax.set_axis_off()
    fig.add_axes(ax, aspect="auto")
    fig.canvas.mpl_connect("key_press_event", on_press(image_path))
    ax.imshow(image, cmap="Greys", aspect="auto")

    for bbox in bbox_containers.bounding_boxes:
        rectangle = plt.Rectangle(
            (bbox.bottom_left_x, bbox.bottom_left_y),
            width=bbox.width,
            height=-bbox.height,
            fill=True,
            edgecolor="black",
            alpha=0.3,
            linewidth=2,
        )
        ax.add_artist(rectangle)
        rx, ry = rectangle.get_xy()
        cx = rx + rectangle.get_width() / 2.0
        cy = ry + rectangle.get_height() / 2.0
        ax.annotate(
            bbox.sign,
            (cx, cy),
            color="w",
            weight="bold",
            fontsize=7,
            ha="center",
            va="top",
            alpha=0.5,
        )
    plt.title(image_path)
    fig.canvas.manager.set_window_title(image_path)
    plt.show()


def show_img(image_path: Path, gt_path: Path) -> None:
    if not is_valid_file_size(image_path, False):
        print(f"Image '{image_path.stem}' has size 0 bytes. Please check")
    elif not is_valid_file_size(gt_path, False):
        print(
            f"Annotation '{gt_path.stem}' has size 0 bytes. Annotations and image will be deleted"
        )
        files_to_delete.append(image_path.stem)
    else:
        plot_bbox_with_img(image_path, gt_path)


if __name__ == "__main__":
    """
    display annotations boxes and images. Skip through images with pressing "ESC" or pressing "k" which will
    log image id to console. This way one can manually skip through training data and exclude data samples
    which are not good!
    """

    """
    #Display single image + annotation
    img = Path("../data/processed-data/heidelberg-merged-extracted-cleaned/imgs/P314346.jpg")
    annotation = Path("../data/processed-data/heidelberg-merged-extracted-cleaned/annotations/gt_P314346-v2.txt")
    display_bboxes(img, annotation)
    quit()
    """
    data_path_str = "../data/processed-data/overfit"
    data_path = Path(data_path_str)
    display_bboxes(data_path)

    print("finished")
    print(finished)
    print("Nearly finished")
    print(nearly_finished)
    print("Medium Quality")
    print(medium_quality)
    print("Bad Quality")
    print(bad_quality)
    # delete_corrupt_images_and_annotations(data_path, files_to_delete)
    print("Manuel Fixing")
    print(manuel_fixing)
    # """