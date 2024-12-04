import pygame
import os
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from OBDHandler import OBDHandler, MockOBD
from AudioLoop import AudioLoop
import threading

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def generate_graph(bass_volume, drum_volume, other_volume, vocal_volume):
    """Generate a Matplotlib graph based on current values."""
    # Data points
    x = [0, 1]  # Normalized throttle range
    
    #Initial Volumes
    y_bass = [0, bass_volume]
    y_drums = [0, drum_volume]
    y_other = [0, other_volume]
    y_vocal = [0, vocal_volume]

    # Create figure
    fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
    ax.plot(x, y_bass, color='red', label='Bass', marker='o')
    ax.plot(x, y_drums, color='green', label='Drums', marker='o')
    ax.plot(x, y_other, color='blue', label='Others', marker='o')
    ax.plot(x, y_vocal, color='yellow', label='Vocals', marker='o')

    # Annotations
    ax.text(x[1], y_bass[1], f'Bass (Volume: {bass_volume})', color='red')
    ax.text(x[1], y_drums[1], f'Drums (Volume: {drum_volume})', color='green')
    ax.text(x[1], y_other[1], f'Other (Volume: {other_volume})', color='blue')
    ax.text(x[1], y_vocal[1], f'Vocals (Volume: {vocal_volume})', color='yellow')

    # Customizations
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel('Throttle (0 to 1)')
    ax.set_ylabel('Normalized Values')
    ax.legend()
    ax.set_title("Audio Volumes Mapping")

    return fig

def render_graph(fig, surface, x, y):
    """Render the Matplotlib figure onto a Pygame surface."""
    canvas = FigureCanvas(fig)
    canvas.draw()
    raw_data = canvas.tostring_rgb()
    size = canvas.get_width_height()
    graph_surface = pygame.image.fromstring(raw_data, size, "RGB")
    surface.blit(graph_surface, (x, y))

def draw_slider(screen, x, y, width, height, value, color):
    """Draw a slider and return the slider's rectangle."""
    pygame.draw.rect(screen, GRAY, (x, y, width, height))  # Background
    fill_width = width * value
    pygame.draw.rect(screen, color, (x, y, fill_width, height))  # Filled part
    return pygame.Rect(x, y, width, height)

def draw_gauge(screen, x, y, radius, value, max_value, color, title):
    """Draw a circular gauge."""
    pygame.draw.circle(screen, GRAY, (x, y), radius, 5)  # Outer circle
    angle = (value / max_value) * 270 - 135  # Convert value to angle
    end_x = x + radius * 0.8 * math.cos(angle * math.pi / 180)
    end_y = y + radius * 0.8 * math.sin(angle * math.pi / 180)
    pygame.draw.line(screen, color, (x, y), (end_x, end_y), 5)  # Needle
    font = pygame.font.Font(None, 36)
    text = font.render(title, True, WHITE)
    screen.blit(text, (x - radius, y + radius + 10))

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Car Simulation")
    clock = pygame.time.Clock()

    # Load audio and OBD handler
    songname = input("Enter the folder name of the song you want to play: ")
    path = f"wavs/{songname}/"
    file_paths = [os.path.join(path, file) for file in os.listdir(path) if file.endswith(".wav")]
    if not file_paths:
        print("No audio files found in the specified folder.")
        return

    loop = AudioLoop(file_paths)
    loop.start()
    loop.adjust_volumes([0, 0, 0, 0])
    mock_connection = MockOBD()
    handler = OBDHandler(connection=mock_connection)

    # Slider values
    throttle_value = 0
    brake_value = 0

    running = True
    while running:
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check for slider interactions
                if throttle_rect.collidepoint(event.pos):
                    throttle_value = (event.pos[0] - throttle_rect.x) / throttle_rect.width
                elif brake_rect.collidepoint(event.pos):
                    brake_value = (event.pos[0] - brake_rect.x) / brake_rect.width

        # Adjust mock connection based on sliders
        mock_connection.set_speed(throttle_value * 70)  # Map throttle to speed
        mock_connection.set_rpm(throttle_value * 7000)  # Map throttle to RPM

        # Refresh OBD handler
        handler.refresh()
        volumes = handler.get_volumes()
        loop.adjust_volumes(volumes)

        # Generate and render graph
        fig = generate_graph(volumes[0] , volumes[1], volumes[2], volumes[3])
        render_graph(fig, screen, 100, 100)

        # Draw sliders
        throttle_rect = draw_slider(screen, 50, 500, 300, 20, throttle_value, GREEN)
        brake_rect = draw_slider(screen, 450, 500, 300, 20, brake_value, RED)

        # Draw gauges
        draw_gauge(screen, 200, 200, 100, handler.speed, 70, BLUE, "Speed (mph)")
        draw_gauge(screen, 600, 200, 100, handler.rpm, 7000, GREEN, "RPM")

        # Display updates
        pygame.display.flip()
        clock.tick(30)  # Limit to 30 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
