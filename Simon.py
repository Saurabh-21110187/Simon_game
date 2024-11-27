import pygame
import random
import sys
import time
import csv
import pandas as pd
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simon Game")
FONT = pygame.font.Font(None, 48)
CLOCK = pygame.time.Clock()

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Positions for the buttons
BUTTONS = {
    "RED": pygame.Rect(50, 50, 200, 200),
    "GREEN": pygame.Rect(350, 50, 200, 200),
    "BLUE": pygame.Rect(50, 350, 200, 200),
    "YELLOW": pygame.Rect(350, 350, 200, 200),
}

# Mapping colors to names
COLOR_MAP = {"RED": RED, "GREEN": GREEN, "BLUE": BLUE, "YELLOW": YELLOW}
COLOR_LIST = ["RED", "GREEN", "BLUE", "YELLOW"]

# Load sounds
def load_sound(file_name):
    try:
        return pygame.mixer.Sound(file_name)
    except FileNotFoundError:
        print(f"Warning: {file_name} not found. Skipping sound.")
        return None

SOUNDS = {
    "RED": load_sound("red.wav"),
    "GREEN": load_sound("green.wav"),
    "BLUE": load_sound("blue.wav"),
    "YELLOW": load_sound("yellow.wav"),
    "START": load_sound("start.mp3"),
    "GAME_OVER": load_sound("game_over.mp3")
}

# Store data for each player session
game_data = []

def save_game_data(data):
    """Saves the game data into a CSV file."""
    with open('game_data.csv', 'a', newline='') as csvfile:
        fieldnames = ['player_id', 'level', 'reaction_time', 'correct_clicks', 'score', 'with_sound']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header only once
        if csvfile.tell() == 0:
            writer.writeheader()
        
        writer.writerows(data)

def track_performance(player_id, level, reaction_time, correct_clicks, score, with_sound):
    """Tracks the player's performance during the game."""
    game_data.append({
        'player_id': player_id,
        'level': level,
        'reaction_time': reaction_time,
        'correct_clicks': correct_clicks,
        'score': score,
        'with_sound': with_sound
    })

def draw_buttons(active=None):
    """Draws the game buttons."""
    for color, rect in BUTTONS.items():
        pygame.draw.rect(screen, COLOR_MAP[color], rect)
        if active == color:
            pygame.draw.rect(screen, WHITE, rect, 5)
        else:
            pygame.draw.rect(screen, BLACK, rect, 5)

def flash_color(color, with_sound=True):
    """Flashes a specific button."""
    if with_sound and SOUNDS[color]:
        SOUNDS[color].play()
    draw_buttons(active=color)
    pygame.display.flip()
    pygame.time.delay(500)
    draw_buttons()
    pygame.display.flip()
    pygame.time.delay(250)

def display_message(message, color=WHITE, font_size=36):
    """Displays a message on the screen, supports multi-line text."""
    screen.fill(BLACK)
    font = pygame.font.Font(None, font_size)
    lines = message.split('\n')
    for i, line in enumerate(lines):
        text = font.render(line, True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 50))
        screen.blit(text, text_rect)
    pygame.display.flip()

def display_score(score):
    """Displays the current score on the screen."""
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    pygame.display.flip()

def show_initial_buttons():
    """Display all buttons for a brief moment before the game starts."""
    draw_buttons()
    display_message("Get Ready!", color=WHITE)
    pygame.display.flip()
    pygame.time.delay(2000)  # Show the buttons for 2 seconds

def main():
    """Main game loop with improved menu options."""
    # Play the start sound immediately when the game starts
    if SOUNDS["START"]:
        SOUNDS["START"].play()

    # Main Menu
    display_message("1. Play with Sound\n2. Play without Sound\n3. Quit")
    waiting_for_input = True
    with_sound = True  # Default is sound on

    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    with_sound = True
                    waiting_for_input = False
                elif event.key == pygame.K_2:
                    with_sound = False
                    waiting_for_input = False
                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

    # Stop the start music once the game officially begins
    if SOUNDS["START"]:
        SOUNDS["START"].stop()

    # Show all buttons for 2 seconds before starting
    show_initial_buttons()

    sequence = []
    player_sequence = []
    level = 1
    score = 0
    player_id = 1  # Assign player_id (or unique identifier)

    while True:
        display_score(score)
        display_message(f"Level {level}", color=WHITE)

        # Generate and play sequence
        sequence.append(random.choice(COLOR_LIST))
        for color in sequence:
            flash_color(color, with_sound=with_sound)

        # Player's turn
        player_sequence.clear()
        correct_clicks = 0
        start_time = time.time()

        for i in range(len(sequence)):
            clicked_color = None
            while clicked_color is None:
                draw_buttons()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        for color, rect in BUTTONS.items():
                            if rect.collidepoint(event.pos):
                                clicked_color = color

            flash_color(clicked_color, with_sound=with_sound)
            player_sequence.append(clicked_color)

            if player_sequence[i] == sequence[i]:
                correct_clicks += 1
            else:
                if with_sound and SOUNDS["GAME_OVER"]:
                    SOUNDS["GAME_OVER"].play()
                display_message(f"Game Over!\nTotal Score: {score}", color=RED)
                pygame.time.delay(3000)
                track_performance(player_id, level, time.time() - start_time, correct_clicks, score, with_sound)
                save_game_data(game_data)
                pygame.quit()
                sys.exit()

        reaction_time = time.time() - start_time
        track_performance(player_id, level, reaction_time, correct_clicks, score, with_sound)

        score += 10
        level += 1
        CLOCK.tick(2)

# Function to load and analyze game data
def load_data():
    """Loads the game data from the CSV file."""
    data = pd.read_csv('game_data.csv')
    return data

def get_basic_statistics(data):
    """Generates basic descriptive statistics for the game data."""
    print("Descriptive Statistics:")
    print(data.describe())

def average_reaction_time_by_level(data):
    """Calculates average reaction time for each level."""
    avg_reaction_time = data.groupby('level')['reaction_time'].mean()
    print("\nAverage Reaction Time by Level:")
    print(avg_reaction_time)

    # Plot reaction time by level
    avg_reaction_time.plot(kind='bar', title="Average Reaction Time by Level", color='skyblue')
    plt.xlabel('Level')
    plt.ylabel('Average Reaction Time (seconds)')
    plt.show()

def score_distribution(data):
    """Displays the score distribution of players."""
    score_by_player = data.groupby('player_id')['score'].sum()
    print("\nTotal Score by Player:")
    print(score_by_player)

    # Plot score distribution
    score_by_player.plot(kind='hist', bins=10, title="Score Distribution by Player", color='lightgreen')
    plt.xlabel('Score')
    plt.ylabel('Number of Players')
    plt.show()

def compare_performance_by_sound(data):
    """Compares player performance with and without sound."""
    avg_score_by_sound = data.groupby('with_sound')['score'].mean()
    avg_reaction_time_by_sound = data.groupby('with_sound')['reaction_time'].mean()

    print("\nAverage Score by Sound Presence:")
    print(avg_score_by_sound)
    
    print("\nAverage Reaction Time by Sound Presence:")
    print(avg_reaction_time_by_sound)

    # Plot the performance comparison
    fig, ax = plt.subplots(1, 2, figsize=(14, 6))

    avg_score_by_sound.plot(kind='bar', ax=ax[0], title="Average Score by Sound Presence", color=['red', 'blue'])
    ax[0].set_ylabel('Average Score')
    ax[0].set_xticklabels(['With Sound', 'Without Sound'])

    avg_reaction_time_by_sound.plot(kind='bar', ax=ax[1], title="Average Reaction Time by Sound Presence", color=['red', 'blue'])
    ax[1].set_ylabel('Average Reaction Time (seconds)')
    ax[1].set_xticklabels(['With Sound', 'Without Sound'])

    plt.show()

def main_analysis():
    """Main function to run the analysis."""
    data = load_data()
    get_basic_statistics(data)
    average_reaction_time_by_level(data)
    score_distribution(data)
    compare_performance_by_sound(data)

# Run the game or analysis
if __name__ == "__main__":
    choice = input("Run Game (G) or Analysis (A): ").strip().upper()
    if choice == 'G':
        main()
    elif choice == 'A':
        main_analysis()
