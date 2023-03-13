from pathlib import Path
from xml.dom import minidom

from PIL import Image

"""
<?xml version="1.0"?>
<imageList>
    <total>4</total>
    <image>
        <id>1</id>
        <name type="NA">VAT10657</name>
        <file>VAT10657</file>
        <annotation info="partial" version="1">VAT10657</annotation>
    </image>
    <image>
        <id>2</id>
        <name type="NA">VAT10601</name>
        <file>VAT10601</file>
        <annotation info="partial" version="1">VAT10601</annotation>
    </image>
    <image>
        <id>3</id>
        <name type="NA">test-1</name>
        <file>test-1</file>
        <annotation info="none">empty</annotation>
    </image>
    <image>
        <id>4</id>
        <name type="NA">test-2</name>
        <file>test-2</file>
        <annotation info="partial" version="1">test-2</annotation>
    </image>
</imageList>
"""


def create_xml(image_path: Path, xml_path: Path) -> None:
    doc = minidom.Document()
    image_list = doc.createElement("imageList")
    doc.appendChild(image_list)
    total = doc.createElement("total")
    total.appendChild(doc.createTextNode("1"))
    image_list.appendChild(total)
    image = doc.createElement("image")
    image_list.appendChild(image)
    id = doc.createElement("id")
    id.appendChild(doc.createTextNode("1"))
    image.appendChild(id)
    name = doc.createElement("name")
    name.setAttribute("type", "NA")
    name.appendChild(doc.createTextNode(image_path.stem))
    image.appendChild(name)
    file = doc.createElement("file")
    file.appendChild(doc.createTextNode(image_path.stem))
    image.appendChild(file)
    annotation = doc.createElement("annotation")
    annotation.setAttribute("info", "none")
    annotation.appendChild(doc.createTextNode("empty"))
    image.appendChild(annotation)
    with open(xml_path, "w") as f:
        f.write(doc.toprettyxml())


"""
<?xml version="1.0"?>
<imageList>
    <total>4</total>
    <image>
        <id>1</id>
        <name type="NA">VAT10657</name>
        <file>VAT10657</file>
        <annotation info="partial" version="1">VAT10657</annotation>
    </image>
    <image>
        <id>2</id>
        <name type="NA">VAT10601</name>
        <file>VAT10601</file>
        <annotation info="partial" version="1">VAT10601</annotation>
    </image>
    <image>
        <id>3</id>
        <name type="NA">test-1</name>
        <file>test-1</file>
        <annotation info="none">empty</annotation>
    </image>
    <image>
        <id>4</id>
        <name type="NA">test-2</name>
        <file>test-2</file>
        <annotation info="partial" version="1">test-2</annotation>
    </image>
</imageList>
"""


def create_xml_file(images, xml_path: Path) -> None:
    xml_file = minidom.Document()
    image_list = xml_file.createElement("imageList")
    xml_file.appendChild(image_list)
    total = xml_file.createElement("total")
    total.appendChild(xml_file.createTextNode(str(len(images))))
    image_list.appendChild(total)
    for i, image in enumerate(images):
        image_element = xml_file.createElement("image")
        image_list.appendChild(image_element)
        id = xml_file.createElement("id")
        id.appendChild(xml_file.createTextNode(str(i + 1)))
        image_element.appendChild(id)
        name = xml_file.createElement("name")
        name.setAttribute("type", "NA")
        name.appendChild(xml_file.createTextNode(image))
        image_element.appendChild(name)
        file = xml_file.createElement("file")
        file.appendChild(xml_file.createTextNode(image))
        image_element.appendChild(file)
        annotation = xml_file.createElement("annotation")
        annotation.setAttribute("info", "none")
        annotation.setAttribute("version", "1")
        annotation.appendChild(xml_file.createTextNode(image))
        image_element.appendChild(annotation)

    with open(xml_path, "w"):
        xml_file.writexml(open(xml_path, "w"), indent="\t", addindent="\t", newl="\n")


def create_thumbnail(image_path: Path, thumbnail_path: Path) -> None:
    img = Image.open(image_path)
    img.thumbnail((200, 200))
    img.save(thumbnail_path)


if __name__ == "__main__":
    save_path_file = "imagesList.xml"
    img_path = Path("../../temp/heidelberg/imgs")
    images = [image.stem for image in img_path.iterdir()]

    create_xml_file([image.stem for image in img_path.iterdir()], save_path_file)
    for image in img_path.iterdir():
        create_thumbnail(
            image, image.parent.parent.parent / "thumbnails" / f"{image.stem}-thumb.jpg"
        )
