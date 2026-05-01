import os
from PIL import Image, ImageDraw

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def create_icon(name, color, shape_func):
    size = (64, 64)
    image = Image.new('RGBA', size, (0, 0, 0, 0)) # Transparent
    draw = ImageDraw.Draw(image)
    
    # Draw shape
    shape_func(draw, size, color)
    
    return image

def draw_dashboard(draw, size, color):
    # 4 squares
    w, h = size
    gap = 8
    box_w = (w - 3*gap) // 2
    
    # Top Left
    draw.rounded_rectangle([gap, gap, gap+box_w, gap+box_w], radius=4, fill=color)
    # Top Right
    draw.rounded_rectangle([gap*2+box_w, gap, gap*2+box_w*2, gap+box_w], radius=4, fill=color)
    # Bottom Left
    draw.rounded_rectangle([gap, gap*2+box_w, gap+box_w, gap*2+box_w*2], radius=4, fill=color)
    # Bottom Right
    draw.rounded_rectangle([gap*2+box_w, gap*2+box_w, gap*2+box_w*2, gap*2+box_w*2], radius=4, fill=color)

def draw_student(draw, size, color):
    w, h = size
    # Head
    draw.ellipse([w//2-12, 10, w//2+12, 34], fill=color)
    # Body
    draw.pieslice([w//2-24, 38, w//2+24, 78], 180, 360, fill=color)

def draw_train(draw, size, color):
    w, h = size
    # Brain logic / Gears? Let's do a simple chip/brain logic
    margin = 12
    draw.rounded_rectangle([margin, margin, w-margin, h-margin], radius=8, outline=color, width=4)
    # Inner logic lines
    draw.line([w//2, margin, w//2, h-margin], fill=color, width=3)
    draw.line([margin, h//2, w-margin, h//2], fill=color, width=3)
    draw.ellipse([w//2-6, h//2-6, w//2+6, h//2+6], fill=color)

def draw_report(draw, size, color):
    w, h = size
    margin = 12
    # Document shape
    draw.rounded_rectangle([margin, 8, w-margin, h-8], radius=4, fill=color)
    # Lines (subtracted or drawn on top with transparent (not possible) or white/bg color)
    # Since we need transparent, we just draw lines as "gaps"? 
    # Actually simpler: Draw rectangle, then draw lines on it? 
    pass

def draw_report_better(draw, size, color):
    w, h = size
    margin = 14
    # Outline of doc
    # draw.rounded_rectangle([margin, 8, w-margin, h-8], radius=4, outline=color, width=4)
    # Content lines
    draw.rectangle([margin+8, 16, w-margin-8, 22], fill=color)
    draw.rectangle([margin+8, 30, w-margin-8, 36], fill=color)
    draw.rectangle([margin+8, 44, w-margin-16, 50], fill=color)

def draw_logout(draw, size, color):
    w, h = size
    # Arrow properties
    arrow_w = 4
    start_x = 24
    end_x = 52
    
    # Door/Bracket
    draw.line([32, 12, 12, 12], fill=color, width=4) # Top
    draw.line([12, 12, 12, 52], fill=color, width=4) # Left
    draw.line([12, 52, 32, 52], fill=color, width=4) # Bottom
    
    # Arrow
    draw.line([start_x, h//2, end_x, h//2], fill=color, width=4)
    # Arrow head
    draw.polygon([(end_x, h//2), (end_x-8, h//2-8), (end_x-8, h//2+8)], fill=color)

def main():
    icons_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
    create_directory(icons_dir)
    
    # Color = White for dark mode icons
    color = (255, 255, 255, 255) 
    
    icons = [
        ('dashboard.png', draw_dashboard),
        ('student.png', draw_student),
        ('train.png', draw_train),
        ('reports.png', draw_report_better),
        ('logout.png', draw_logout)
    ]
    
    for name, func in icons:
        path = os.path.join(icons_dir, name)
        img = create_icon(name, color, func)
        img.save(path)
        print(f"Generated {name}")

if __name__ == "__main__":
    main()
