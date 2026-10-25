from PIL import Image, ImageDraw, ImageFont
import os

# Create assets/images directory if it doesn't exist
os.makedirs('assets/images', exist_ok=True)

# Colors
green = (46, 125, 50)  # Green #2E7D32
white = (255, 255, 255)

# Create main app icon (1024x1024)
size = 1024
img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Draw main green circle
circle_center = size // 2
circle_radius = 380
draw.ellipse(
    [circle_center - circle_radius, circle_center - circle_radius,
     circle_center + circle_radius, circle_center + circle_radius],
    fill=green
)

# Draw white border/ring around the circle
border_width = 15
draw.ellipse(
    [circle_center - circle_radius - border_width, circle_center - circle_radius - border_width,
     circle_center + circle_radius + border_width, circle_center + circle_radius + border_width],
    outline=white,
    width=border_width
)

# Draw "CIRP" text
try:
    # Try to use a nice bold font
    font_cirp = ImageFont.truetype("arialbd.ttf", 200)
except:
    try:
        font_cirp = ImageFont.truetype("arial.ttf", 200)
    except:
        font_cirp = ImageFont.load_default()

text_cirp = "CIRP"
# Get text bounding box with proper centering
bbox = draw.textbbox((0, 0), text_cirp, font=font_cirp, anchor='lt')
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center CIRP text perfectly
x = (size - text_width) // 2
y = circle_center - 110  # Move up a bit more

# Draw CIRP text
draw.text((x, y), text_cirp, fill=white, font=font_cirp, anchor='lt')

# Draw "Issue Reporter" text
try:
    font_subtitle = ImageFont.truetype("arial.ttf", 60)
except:
    font_subtitle = ImageFont.load_default()

text_subtitle = "Issue Reporter"
bbox_sub = draw.textbbox((0, 0), text_subtitle, font=font_subtitle, anchor='lt')
sub_width = bbox_sub[2] - bbox_sub[0]
sub_height = bbox_sub[3] - bbox_sub[1]

# Center subtitle text perfectly (below CIRP)
sub_x = (size - sub_width) // 2
sub_y = y + text_height + 10  # Small gap between texts

draw.text((sub_x, sub_y), text_subtitle, fill=white, font=font_subtitle, anchor='lt')

# Save main icon
img.save('assets/images/app_icon.png')
print("Created app_icon.png")

# Create foreground for adaptive icon (same design)
img.save('assets/images/app_icon_foreground.png')
print("Created app_icon_foreground.png")

print("\nNew logo generated successfully!")
print("The logo now has:")
print("- Green circular background")
print("- White 'CIRP' text in large font")
print("- White 'Issue Reporter' subtitle")
print("- White border ring around the circle")
