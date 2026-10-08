from PIL import Image, ImageDraw, ImageFont
import os

# Create assets/images directory if it doesn't exist
os.makedirs('assets/images', exist_ok=True)

# Colors
bg_color = (46, 125, 50)  # Green #2E7D32
white = (255, 255, 255)

# Create main app icon (1024x1024)
size = 1024
img = Image.new('RGB', (size, size), bg_color)
draw = ImageDraw.Draw(img)

# Draw a circle for the background
circle_margin = 100
draw.ellipse([circle_margin, circle_margin, size - circle_margin, size - circle_margin], 
             fill=bg_color, outline=white, width=20)

# Draw "CIRP" text
try:
    # Try to use a nice font
    font = ImageFont.truetype("arial.ttf", 280)
except:
    # Fallback to default font
    font = ImageFont.load_default()

text = "CIRP"
# Get text bounding box
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

# Center the text
x = (size - text_width) // 2
y = (size - text_height) // 2 - 50

# Draw text with shadow for depth
draw.text((x + 5, y + 5), text, fill=(0, 0, 0, 100), font=font)
draw.text((x, y), text, fill=white, font=font)

# Add a small subtitle/tagline
try:
    small_font = ImageFont.truetype("arial.ttf", 80)
except:
    small_font = ImageFont.load_default()

subtitle = "Issue Reporter"
bbox = draw.textbbox((0, 0), subtitle, font=small_font)
sub_width = bbox[2] - bbox[0]
sub_x = (size - sub_width) // 2
sub_y = y + text_height + 40

draw.text((sub_x, sub_y), subtitle, fill=white, font=small_font)

# Save main icon
img.save('assets/images/app_icon.png')
print("Created app_icon.png")

# Create foreground for adaptive icon (simpler version, just the logo)
fg_img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
fg_draw = ImageDraw.Draw(fg_img)

# Draw CIRP text
try:
    font = ImageFont.truetype("arial.ttf", 280)
except:
    font = ImageFont.load_default()

text = "CIRP"
bbox = fg_draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x = (size - text_width) // 2
y = (size - text_height) // 2

# Draw text
fg_draw.text((x, y), text, fill=white, font=font)

# Save foreground icon
fg_img.save('assets/images/app_icon_foreground.png')
print("Created app_icon_foreground.png")

print("\nIcons generated successfully!")
print("Now run: flutter pub get")
print("Then run: flutter pub run flutter_launcher_icons")
