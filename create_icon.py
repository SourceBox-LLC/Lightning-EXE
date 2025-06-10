from PIL import Image, ImageDraw
import os

# Create a 64x64 image with a transparent background
icon_size = (64, 64)
img = Image.new('RGBA', icon_size, color=(0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a lightning bolt
# Define lightning bolt shape
lightning_points = [
    (32, 8),   # Top point
    (20, 32),  # Middle left
    (28, 32),  # Middle center
    (16, 56),  # Bottom point
    (32, 32),  # Middle right point
    (24, 32),  # Middle center
    (36, 8),   # Back to top right
]

# Draw the lightning bolt in yellow with a dark outline
draw.polygon(lightning_points, fill=(255, 215, 0))  # Gold/yellow
draw.line(lightning_points + [lightning_points[0]], fill=(50, 50, 50), width=2)

# Save as PNG
img.save('lightning_icon.png')

# Try to save as ICO if PIL supports it
try:
    img.save('lightning_icon.ico', format='ICO', sizes=[(64, 64)])
    print("Icon files created successfully!")
except Exception as e:
    print(f"Created PNG icon. ICO format failed: {str(e)}")
    print("You may need to convert the PNG to ICO manually.")

print("Icon creation complete!")
