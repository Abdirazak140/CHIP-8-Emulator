from cpu import CPU
import os

def Emulator():
    game_folder = "games"
    game_list = os.listdir(game_folder)

    print("Available Games:")
    for i, game in enumerate(game_list, start=1):
        print(f"{i}. {game}")

    try:
        game_choice = int(input("What game do you want to play (enter the number): "))
        if 1 <= game_choice <= len(game_list):
            rom_path = os.path.join(game_folder, game_list[game_choice - 1])
            print(f"Loading: {rom_path}")
            cpu = CPU(rom_path)
        else:
            print("Invalid choice. Please select a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")

if __name__ == '__main__':
    Emulator()