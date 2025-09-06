# standard imports
from itertools import islice
# package imports
from pathlib import Path
from PIL import Image
import readchar  # pip install readchar

# local imports
########################################################
def get_last_line_of_txt(output_file):
	if not Path(output_file).exists(): return '' 
	with open(output_file, 'r', encoding="utf-8") as f:
		for line in f :
			pass 
		last_jpg_checked = line

		return last_jpg_checked
	
def get_image_paths_to_check(text_file, output_file, start_line_idx):
	image_paths = [] 
	
	with open(text_file) as f:
		for line in islice(f, start_line_idx - 1, None):
			image_paths.append(Path(line.strip()))
	return image_paths

def check_img_paths(image_paths, output_file):

	for img_path in image_paths:
		# Open image
		img = Image.open(img_path)
		img.show()  # Opens image in default viewer

		print(f"Showing {img_path.name}. Press 'd' to mark, any other key to skip.")
		
		key = readchar.readkey()  # Wait for a single key press

		if key.lower() == 'd':
			print(f"Marked {img_path.name} for deletion")
			# Append to file
			with open(output_file, "a", encoding="utf-8") as f:
				f.write(str(img_path) + "\n")
			print(f"Marked {img_path} for deletion.")		
		else:
			print(f"Skipped {img_path.name}")

		img.close()  # Close the image viewer if needed
		
def get_start_line_index(search_text):
	if not search_text: return 1
	with open(text_file, "r", encoding="utf-8") as f:
		start_line = None
		for i, line in enumerate(f, start=1):
			if search_text in line:
				start_line = i + 1

				return start_line

if __name__ == '__main__':
	text_file = 'utils/images_to_delete/no_partial_order_x1.txt' 
	output_file = 'utils/images_to_delete/to_delete_after_checking.txt'
	# last_jpg_checked = 
	last_jpg_checked = get_last_line_of_txt(output_file)
	start_line_idx = get_start_line_index(last_jpg_checked)
	
	image_paths = get_image_paths_to_check(text_file, output_file, start_line_idx)
	check_img_paths(image_paths, output_file)
	breakpoint()