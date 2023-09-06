import pygame
import time


class CPU:
    def __init__(self, file_name):
        self.memory = [0] * 4096 
        self.register_v = [0] * 16
        self.register_I = 0
        self.pc = 0x200
        self.font = [
            [0xF0, 0x90, 0x90, 0x90, 0xF0], # 0
            [0x20, 0x60, 0x20, 0x20, 0x70], # 1
            [0xF0, 0x10, 0xF0, 0x80, 0xF0], # 2
            [0xF0, 0x10, 0xF0, 0x10, 0xF0], # 3
            [0x90, 0x90, 0xF0, 0x10, 0x10], # 4
            [0xF0, 0x80, 0xF0, 0x10, 0xF0], # 5
            [0xF0, 0x80, 0xF0, 0x90, 0xF0], # 6
            [0xF0, 0x10, 0x20, 0x40, 0x40], # 7
            [0xF0, 0x90, 0xF0, 0x90, 0xF0], # 8
            [0xF0, 0x90, 0xF0, 0x10, 0xF0], # 9
            [0xF0, 0x90, 0xF0, 0x90, 0x90], # A
            [0xE0, 0x90, 0xE0, 0x90, 0xE0], # B
            [0xF0, 0x80, 0x80, 0x80, 0xF0], # C
            [0xE0, 0x90, 0x90, 0x90, 0xE0], # D
            [0xF0, 0x80, 0xF0, 0x80, 0xF0], # E
            [0xF0, 0x80, 0xF0, 0x80, 0x80]  # F
        ]
        self.screen = Screen()
        self.init_ROM(file_name)
        self.delay_timer = 0
        self.sound_timer = 0
        
        
    def init_ROM(self, file_name):
        try:
            with open(file_name, "rb") as file:
                program_data = file.read()
                
                for i, byte in enumerate(program_data):
                    self.memory[0x200 + i] = byte
                    
            self.fetch_instructions()
            
        except:
            print("File does not exist")
            exit()
        
    
    def fetch_instructions(self):
        # counter = 0
        start = time.time()
        
        while True:
            if self.pc > len(self.memory):
                break
            
            first_byte = self.memory[self.pc]
            second_byte = self.memory[self.pc + 1]
            combinedBytes = (first_byte << 8) | second_byte
            
            current_pc = self.pc
            
            self.decode_instruction(combinedBytes)
            
            if current_pc == self.pc:
                self.pc += 2
        
        end = time.time()
        
        print(end-start)
            
    def decode_instruction(self, instruction):
        print(hex(instruction))
        instruction_type = instruction >> 12
        
        X = (instruction >> 8) & 0xf
        Y = (instruction >> 4) & 0xfff & 0xf
        N = instruction & 0xf
        NN = instruction & 0xff
        NNN = instruction & 0xfff
        
        match instruction_type:
            case 0x0:
                # Clear screen
                self.screen.clear_screen()
                print("clear")
                
            case 0x1:
                # PC jumps
                self.pc = NNN
                
            case 0x6:
                # Set register vx to NN
                self.register_v[X] = NN
                
            case 0x7:
                # Add NN to register vx
                self.register_v[X] += NN
                            
            case 0xA:
                # Set register I to NNN
                self.register_I = NNN
                
            case 0xD:
                # Display/Draw
                x_axis = self.register_v[X] & 64
                y_axis = self.register_v[Y] & 31
                address = self.register_I
                
                # self.screen.draw(x_axis, y_axis, N)
                
            case _:
                print("Unknown instruction {:x}".format(instruction))
                
                  
class Screen:
    def __init__(self) -> None:
        pygame.init()
        self.x_axis = 0
        self.y_axis = 0
        self.clear = False
        self.screen = pygame.display.set_mode((64,32))
        pygame.display.set_caption("CHIP 8 Emulator")
        running = True
        
        while running:
            for event in pygame.event.get():
                
                if event.type == pygame.QUIT:
                    running = False
                    
            if self.clear is True:
                self.screen.fill((0,0,0))
                pygame.display.flip()
                self.clear = False
                
            if self.x_axis != 0 and self.y_axis != 0:
                self.screen.set_at((self.x_axis, self.y_axis), (255, 255, 255))
            
            
    
    def draw_pixel(self, x_axis, y_axis, n):
        self.x_axis = x_axis
        self.y_axis = y_axis
    
    def clear_screen(self):
        self.clear = True
        

    
def main():
    cpu = CPU("IBM Logo.ch8")
    


if __name__ == '__main__':
    main()