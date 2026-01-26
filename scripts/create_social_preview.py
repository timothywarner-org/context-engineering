"""
Create social preview image for context-engineering repository.
GitHub recommended size: 1280x640 pixels
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Image dimensions (GitHub recommended)
WIDTH = 1280
HEIGHT = 640

# Color palette (Anthropic/Claude-inspired blues and purples)
COLORS = {
    'bg_gradient_start': (15, 23, 42),      # Dark slate blue
    'bg_gradient_end': (30, 41, 59),        # Slightly lighter slate
    'accent_purple': (139, 92, 246),        # Vibrant purple
    'accent_blue': (59, 130, 246),          # Bright blue
    'accent_cyan': (34, 211, 238),          # Cyan highlight
    'text_primary': (248, 250, 252),        # Near white
    'text_secondary': (148, 163, 184),      # Muted gray
    'text_accent': (167, 139, 250),         # Light purple
    'node_green': (74, 222, 128),           # Green for nodes
    'node_orange': (251, 146, 60),          # Orange for nodes
}

def create_gradient_background(width, height, color1, color2):
    """Create a horizontal gradient background."""
    img = Image.new('RGB', (width, height))
    pixels = img.load()

    for x in range(width):
        for y in range(height):
            # Blend based on position (diagonal gradient)
            ratio = (x / width * 0.7) + (y / height * 0.3)
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pixels[x, y] = (r, g, b)

    return img

def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_connection_line(draw, start, end, color, width=2):
    """Draw a line with arrows for connections."""
    draw.line([start, end], fill=color, width=width)

def draw_node(draw, center, radius, fill_color, border_color, label, font, text_color):
    """Draw a circular node with label."""
    x, y = center
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        fill=fill_color,
        outline=border_color,
        width=2
    )
    # Center the text
    bbox = draw.textbbox((0, 0), label, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        (x - text_width // 2, y - text_height // 2),
        label,
        font=font,
        fill=text_color
    )

def create_social_preview():
    # Create gradient background
    img = create_gradient_background(
        WIDTH, HEIGHT,
        COLORS['bg_gradient_start'],
        COLORS['bg_gradient_end']
    )
    draw = ImageDraw.Draw(img)

    # Try to load fonts (fallback to default if not available)
    try:
        # Try common Windows fonts
        title_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 56)
        subtitle_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 28)
        small_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
        label_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
        tech_font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
        author_font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    except:
        try:
            title_font = ImageFont.truetype("arial.ttf", 56)
            subtitle_font = ImageFont.truetype("arial.ttf", 28)
            small_font = ImageFont.truetype("arial.ttf", 18)
            label_font = ImageFont.truetype("arial.ttf", 14)
            tech_font = ImageFont.truetype("arialbd.ttf", 20)
            author_font = ImageFont.truetype("arial.ttf", 20)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            tech_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

    # Add very subtle grid pattern in background (barely visible)
    grid_color = (25, 35, 55)  # Very subtle, close to background
    for i in range(0, WIDTH, 60):
        draw.line([(i, 0), (i, HEIGHT)], fill=grid_color, width=1)
    for i in range(0, HEIGHT, 60):
        draw.line([(0, i), (WIDTH, i)], fill=grid_color, width=1)

    # Draw decorative elements - circuit-like patterns
    # Top left corner decoration
    draw.arc([20, 20, 120, 120], 180, 270, fill=COLORS['accent_purple'], width=2)
    draw.arc([30, 30, 130, 130], 180, 270, fill=COLORS['accent_blue'], width=2)

    # Bottom right corner decoration
    draw.arc([WIDTH-120, HEIGHT-120, WIDTH-20, HEIGHT-20], 0, 90, fill=COLORS['accent_purple'], width=2)
    draw.arc([WIDTH-130, HEIGHT-130, WIDTH-30, HEIGHT-30], 0, 90, fill=COLORS['accent_blue'], width=2)

    # === LEFT SIDE: MCP Protocol Flow Diagram ===
    diagram_x = 180
    diagram_y = 320

    # Draw "MCP Protocol" label
    draw.text((diagram_x - 60, diagram_y - 130), "MCP Protocol", font=small_font, fill=COLORS['text_secondary'])

    # Client box
    draw_rounded_rect(draw, [diagram_x - 70, diagram_y - 40, diagram_x + 70, diagram_y + 40],
                      radius=10, fill=(45, 55, 72), outline=COLORS['accent_blue'], width=2)
    draw.text((diagram_x - 30, diagram_y - 12), "Client", font=small_font, fill=COLORS['text_primary'])

    # Server box
    server_x = diagram_x + 200
    draw_rounded_rect(draw, [server_x - 70, diagram_y - 40, server_x + 70, diagram_y + 40],
                      radius=10, fill=(45, 55, 72), outline=COLORS['accent_purple'], width=2)
    draw.text((diagram_x + 170, diagram_y - 12), "Server", font=small_font, fill=COLORS['text_primary'])

    # Bidirectional arrows
    arrow_y1 = diagram_y - 15
    arrow_y2 = diagram_y + 15
    # Right arrow
    draw.line([(diagram_x + 75, arrow_y1), (server_x - 75, arrow_y1)], fill=COLORS['accent_cyan'], width=2)
    draw.polygon([(server_x - 75, arrow_y1), (server_x - 85, arrow_y1 - 6), (server_x - 85, arrow_y1 + 6)],
                 fill=COLORS['accent_cyan'])
    # Left arrow
    draw.line([(server_x - 75, arrow_y2), (diagram_x + 75, arrow_y2)], fill=COLORS['accent_cyan'], width=2)
    draw.polygon([(diagram_x + 75, arrow_y2), (diagram_x + 85, arrow_y2 - 6), (diagram_x + 85, arrow_y2 + 6)],
                 fill=COLORS['accent_cyan'])

    # === MEMORY LAYERS below MCP diagram ===
    memory_y = diagram_y + 100

    # Vector Store
    draw_rounded_rect(draw, [diagram_x - 70, memory_y, diagram_x + 70, memory_y + 50],
                      radius=8, fill=(55, 65, 81), outline=COLORS['node_green'], width=2)
    draw.text((diagram_x - 55, memory_y + 12), "Vector Store", font=label_font, fill=COLORS['text_primary'])

    # Graph Store
    draw_rounded_rect(draw, [server_x - 70, memory_y, server_x + 70, memory_y + 50],
                      radius=8, fill=(55, 65, 81), outline=COLORS['node_orange'], width=2)
    draw.text((server_x - 55, memory_y + 12), "Graph Store", font=label_font, fill=COLORS['text_primary'])

    # Memory label
    draw.text((diagram_x + 45, memory_y + 60), "Hybrid Memory", font=label_font, fill=COLORS['text_secondary'])

    # Connection lines from server to memory
    draw.line([(server_x, diagram_y + 40), (server_x, memory_y)], fill=COLORS['text_secondary'], width=1)
    draw.line([(server_x, diagram_y + 70), (diagram_x, diagram_y + 70), (diagram_x, memory_y)],
              fill=COLORS['text_secondary'], width=1)

    # === RIGHT SIDE: Main Text Content ===
    text_x = 520

    # Main title
    title = "Context Engineering"
    draw.text((text_x, 140), title, font=title_font, fill=COLORS['text_primary'])

    # Subtitle line 1
    subtitle1 = "with MCP"
    draw.text((text_x, 205), subtitle1, font=title_font, fill=COLORS['accent_purple'])

    # Tagline
    tagline = "Build AI Systems That Actually Remember"
    draw.text((text_x, 290), tagline, font=subtitle_font, fill=COLORS['text_secondary'])

    # Tech stack badges
    badge_y = 360
    badges = [
        ("FastMCP", COLORS['accent_blue']),
        ("LangGraph", COLORS['accent_purple']),
        ("Hybrid RAG", COLORS['node_green']),
    ]

    badge_x = text_x
    for badge_text, badge_color in badges:
        bbox = draw.textbbox((0, 0), badge_text, font=tech_font)
        badge_width = bbox[2] - bbox[0] + 24

        draw_rounded_rect(draw,
                         [badge_x, badge_y, badge_x + badge_width, badge_y + 36],
                         radius=18, fill=None, outline=badge_color, width=2)
        draw.text((badge_x + 12, badge_y + 6), badge_text, font=tech_font, fill=badge_color)
        badge_x += badge_width + 16

    # Teaching app name
    app_name = "WARNERCO Schematica"
    draw.text((text_x, 430), "Teaching App: ", font=small_font, fill=COLORS['text_secondary'])
    draw.text((text_x + 120, 427), app_name, font=tech_font, fill=COLORS['accent_cyan'])

    # Author info at bottom right
    author_line1 = "Tim Warner"
    author_line2 = "techtrainertim.com"

    # Draw author section with subtle background
    author_x = WIDTH - 280
    author_y = HEIGHT - 90

    draw_rounded_rect(draw, [author_x - 20, author_y - 10, WIDTH - 30, HEIGHT - 30],
                      radius=10, fill=(30, 41, 59), outline=None)

    draw.text((author_x, author_y), author_line1, font=author_font, fill=COLORS['text_primary'])
    draw.text((author_x, author_y + 28), author_line2, font=small_font, fill=COLORS['accent_cyan'])

    # Add subtle glow effect around title area
    # (simplified - just add some colored dots/circles for visual interest)
    import random
    random.seed(42)  # Consistent pattern
    for _ in range(30):
        x = random.randint(text_x - 50, WIDTH - 50)
        y = random.randint(100, 500)
        size = random.randint(1, 3)
        alpha = random.randint(30, 80)
        color = random.choice([COLORS['accent_purple'], COLORS['accent_blue'], COLORS['accent_cyan']])
        # Dim the color
        dim_color = tuple(int(c * 0.3) for c in color)
        draw.ellipse([x, y, x + size, y + size], fill=dim_color)

    # Save the image
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(os.path.dirname(output_dir), "images", "social-preview.png")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img.save(output_path, "PNG", quality=95)
    print(f"Social preview saved to: {output_path}")
    print(f"Image size: {img.size[0]}x{img.size[1]} pixels")

    return output_path

if __name__ == "__main__":
    create_social_preview()
