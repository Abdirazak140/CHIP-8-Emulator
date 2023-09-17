# import pygame
import time


class CPU:
    def __init__(self, file_name):
        self.memory = [0] * 4096 
        self.register_v = [0] * 16
        self.register_I = 0
        self.pc = 0x200
        font = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]
        
        for i in range(len(font)):
            self.memory[i] = font[i]
        
        self.pixels_on_screen = [[0]*32]*64
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
        
        while self.pc < len(self.memory):  
             
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
        print("Instruction type: {0}".format(instruction_type))
        X = (instruction >> 8) & 0xf
        Y = (instruction >> 4) & 0xfff & 0xf
        N = instruction & 0xf
        NN = instruction & 0xff
        NNN = instruction & 0xfff
        
        print(hex(X), hex(Y), hex(N), hex(NN), hex(NNN))
        match instruction_type:
            case 0x0:
                print("Screen Cleared")
                
            case 0x1:
                self.pc = NNN
                print("PC Jump")
                
            case 0x6:
                self.register_v[X] = NN
                print("Set register vx to NN")
                
            case 0x7:
                self.register_v[X] += NN
                print("Add NN to register vx")
                            
            case 0xA:
                self.register_I = NNN
                print("Set register I to NNN")
                
            case 0xD:
                # Display/Draw
                x_axis = self.register_v[X] & 64
                y_axis = self.register_v[Y] & 31
                self.register_v[0xf] = 0
                
                last_sprite = self.register_I + N
                i = 0
                
                while True:
                    current_sprite = i + self.register_I
                    current_sprite_str = "{0:08b}".format(current_sprite)
                    
                    for pixel in current_sprite_str:
                        if pixel == "1" and self.pixels_on_screen[x_axis][y_axis] == 1:
                            self.pixels_on_screen[x_axis][y_axis] = 0
                            self.register_v[0xf] = 1
                            
                        if pixel == "1" and self.pixels_on_screen[x_axis][y_axis] == 0:
                            print("Draw at {0} {1}".format(x_axis,y_axis))
                        
                        if y_axis == 32:
                            break
                        
                        x_axis+=1
                
                    if last_sprite == current_sprite:
                        break
                    
                    i+= 1
                
            case _:
                print("Unknown instruction {:x}".format(instruction))
                
                  
# class Screen:
#     def __init__(self) -> None:
#         pygame.init()
#         self.x_axis = 0
#         self.y_axis = 0
#         self.clear = False
#         self.screen = pygame.display.set_mode((64,32))
#         pygame.display.set_caption("CHIP 8 Emulator")
#         running = True
        
#         while running:
#             for event in pygame.event.get():
                
#                 if event.type == pygame.QUIT:
#                     running = False
                    
#             if self.clear is True:
#                 self.screen.fill((0,0,0))
#                 pygame.display.flip()
#                 self.clear = False
                
#             if self.x_axis != 0 and self.y_axis != 0:
#                 self.screen.set_at((self.x_axis, self.y_axis), (255, 255, 255))
            
            
    
    # def draw_pixel(self, x_axis, y_axis, n):
    #     self.x_axis = x_axis
    #     self.y_axis = y_axis
    
    # def clear_screen(self):
    #     self.clear = True
        

    
def Emulator():
    cpu = CPU("logo.ch8")
    


if __name__ == '__main__':
    Emulator()