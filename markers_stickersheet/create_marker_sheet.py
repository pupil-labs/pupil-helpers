from pathlib import Path

import cv2
import numpy as np

# Configure script to print a specific page of 24 markers.
# The output file name will be:
#   apriltags_<FAMILY>_<FIRSTID>-<LASTID>.png
FAMILY = "tag36h11"
PAGE = 0

IMGS_DIR = "apriltag-imgs"

if __name__ == "__main__":

    # Setup constants, everything is in pixel size of the markers (unscaled)
    rows, cols = 6, 4  # a page has 6x4 markers
    extra_border = 1  # add border around markers
    global_border = 2  # add border around final grid image
    scale = 2 ** 5  # final upscale factor, should be a power of two for accuracy

    # Derived constants
    n_images = rows * cols
    first = PAGE * n_images
    last = first + n_images - 1

    # Load images
    files = sorted(str(path) for path in (Path(IMGS_DIR) / FAMILY).glob("tag*.png"))
    files = files[first : first + n_images]
    images = [cv2.imread(img_file, cv2.IMREAD_GRAYSCALE) for img_file in files]

    # Create white empty image for composing
    patch_size = images[0].shape[0]
    cell_size = patch_size + 2 * extra_border
    grid_img = 255 * np.ones(
        (rows * cell_size, cols * cell_size), dtype=images[0].dtype
    )

    # Add markers
    for i, img in enumerate(images):
        cell_row = i // cols
        cell_col = i % cols
        row = cell_row * cell_size + extra_border
        col = cell_col * cell_size + extra_border
        grid_img[row : row + patch_size, col : col + patch_size] = img

    # Wrap into bigger image for global border
    final_shape = [size + global_border * 2 for size in grid_img.shape]
    final = 255 * np.ones(final_shape, dtype=grid_img.dtype)
    final[
        global_border : global_border + grid_img.shape[0],
        global_border : global_border + grid_img.shape[1],
    ] = grid_img

    # Upscale
    final = cv2.resize(
        final, dsize=None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST
    )

    # Draw dashes cutting lines onto upscaled image
    dash_size = 10
    offset = global_border * scale
    for i in range(rows + 1):
        y = offset + i * cell_size * scale
        for x in range(0, final.shape[1] - 1, 2 * dash_size):
            cv2.line(
                final, pt1=(x, y), pt2=(x + dash_size, y), color=0, lineType=cv2.LINE_4
            )
    for i in range(cols + 1):
        x = offset + i * cell_size * scale
        for y in range(0, final.shape[0] - 1, 2 * dash_size):
            cv2.line(
                final, pt1=(x, y), pt2=(x, y + dash_size), color=0, lineType=cv2.LINE_4
            )

    # Save to PNG
    cv2.imwrite(f"apriltags_{FAMILY}_{first}-{last}.png", final)
