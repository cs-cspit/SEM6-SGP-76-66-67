import os
from PIL import Image, ImageDraw, ImageFont

def create_icon():
    # Create directory if not exists
    if not os.path.exists('assets'):
        os.makedirs('assets')

    # Create a new image with a white background
    size = (256, 256)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    # Draw a blue rounded rectangle (like a modern app icon)
    blue_color = (0, 120, 215, 255)
    rect_coords = [(20, 20), (236, 236)]
    draw.rounded_rectangle(rect_coords, radius=40, fill=blue_color)

    # Draw a simple "A" or shield-like shape
    # Let's draw a white shield outline or just text "Admin"
    # Drawing a shield
    shield_coords = [
        (128, 40),  # Top point
        (200, 70),  # Top right
        (200, 160), # Bottom right side
        (128, 220), # Bottom point
        (56, 160),  # Bottom left side
        (56, 70)    # Top left
    ]
    draw.polygon(shield_coords, fill=(255, 255, 255, 255))
    
    # Inner blue shield
    shield_inner = [
        (128, 55),
        (185, 80),
        (185, 150),
        (128, 200),
        (71, 150),
        (71, 80)
    ]
    draw.polygon(shield_inner, fill=blue_color)

    # Save as PNG
    png_path = os.path.join('assets', 'icon.png')
    image.save(png_path)
    print(f"Icon saved to {png_path}")

    # Save as ICO
    ico_path = os.path.join('assets', 'icon.ico')
    image.save(ico_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Icon converted to {ico_path}")

if __name__ == "__main__":
    create_icon()
