from cpu import CPU
import os

def Emulator():
    game_folder = "games"
    game_list = os.listdir(game_folder)

    print("Available Games:")
    for i, game in enumerate(game_list, start=1):
        print(f"{i}. {game}")

    game_choice = input("What game do you want to play: ")
    rom_path = os.path.join(game_folder, game_choice)

    cpu = CPU(rom_path)

if __name__ == '__main__':
    Emulator()
