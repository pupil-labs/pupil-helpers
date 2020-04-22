import re
from pathlib import Path

from fpdf import FPDF


IMGS_DIR = "apriltag-imgs"  # location of the original images
FAMILY = "tag36h11"  # set to "ALL" to generate PDFs for all available families


for family_folder in Path(IMGS_DIR).iterdir():
    if family_folder.is_dir():
        family = family_folder.name

        if FAMILY not in ("ALL", family):
            continue

        img_files = sorted(str(img_path) for img_path in family_folder.glob("tag*.png"))

        print(f"Creating PDF for family '{family}' with {len(img_files)} tags...")

        pdf = FPDF(orientation="P", unit="mm")
        pdf.set_font("helvetica", size=48)

        # 10% padding around tag image. Note that some tags have an additional
        # white border, so the padding might appear lager.
        offset = pdf.w * 0.1
        img_size = pdf.w - 2 * offset

        # Set text margins
        pdf.set_top_margin(offset)
        pdf.set_left_margin(offset)
        pdf.set_right_margin(offset)

        for i, img in enumerate(img_files):
            print(f"Processing image {i + 1}/{len(img_files)}...", end="\r")

            # Extract tag ID with regex
            match = re.match(r".*_(?P<id>\d{5})\.png", img)
            if not match:
                raise RuntimeError(f"Error: could not parse image file name! -> {img}")
            img_id = int(match.group("id"))

            pdf.add_page()

            # Note, the image does not affect the text cursor, so we need to
            # draw a blank cell afterwards with the correct offset.
            pdf.image(img, x=offset, y=offset, w=img_size, h=img_size)
            pdf.cell(w=0, h=img_size + offset, ln=1)

            # Height values do not seem to be mm (as selected above), I picked
            # something that looked good.
            pdf.set_font("helvetica", size=48)
            pdf.cell(w=0, h=25, txt=f"ID: {img_id}", align="C", ln=1)
            pdf.set_font("helvetica", size=18)
            pdf.cell(w=0, h=20, txt=f"family: {family}", align="C")

        if len(img_files) > 10000:
            print(
                "Writing PDF... this can take a very long time for > 10,000 images!"
                " Consider using a different family!",
                end="\r",
            )
        elif len(img_files) > 1000:
            print("Writing PDF... this can take a bit for > 1,000 images!", end="\r")

        pdf.output(f"{family}_full.pdf")

        if FAMILY == family:
            break
