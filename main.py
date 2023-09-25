import pygame
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
        self.delay_timer = 0
        self.sound_timer = 0
        self.display = Screen()
        self.init_ROM(file_name)
        
        
        
    def init_ROM(self, file_name):
        try:
            with open(file_name, "rb") as file:
                program_data = file.read()
        
                for i, byte in enumerate(program_data):
                    self.memory[0x200 + i] = byte

                self.fetch_instructions()                
        except Exception as e:
            print(e)
            exit()
        
    
    def fetch_instructions(self):
        num_of_intructions = 0
        start = time.time()

        while self.pc < len(self.memory):
        # while self.pc < 644:
            num_of_intructions+=1
            
            first_byte = self.memory[self.pc]
            second_byte = self.memory[self.pc + 1]
            combinedBytes = (first_byte << 8) | second_byte
            
            current_pc = self.pc
            
            self.decode_instruction(combinedBytes)

            if current_pc == self.pc:
                self.pc += 2
        
        end = time.time()
        time_took = end-start
        print("Number of Instructions: {0} \nTime took: {1}".format(num_of_intructions,time_took))
        
            
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
                self.clear_screen()
                
            case 0x1:
                self.jump_program_counter(NNN)
                
            case 0x6:
                self.set_register_vx(X, NN)
                
            case 0x7:
                self.add_to_register_vx(X, NN)
                            
            case 0xA:
                self.set_index(NNN)
                
            case 0xD:
                self.draw_sprite(X, Y, N)
                
            case _:
                print("Unknown instruction {:x}".format(instruction))
                
    def clear_screen(self):
        print("Screen Cleared\n\n")
    
    def jump_program_counter(self, NNN):
        self.pc = NNN
        print("PC Jump\n\n")
    
    def set_register_vx(self, X, NN):
        self.register_v[X] = NN
        print("Set register vx to NN\n\n")
    
    def add_to_register_vx(self, X, NN):
        self.register_v[X] += NN
        print("Add NN to register vx\n\n")

    
    def set_index(self, NNN):
        self.register_I = NNN
        print("Set register I to NNN\n\n")
    
    
    def draw_sprite(self, X, Y, N):
        x_axis = self.register_v[X] % 64
        y_axis = self.register_v[Y] % 32
        self.register_v[0xf] = 0   

        for row in range(N):
            current_sprite = "{0:08b}".format(self.memory[self.register_I + row])
            print("\nSprite: {0}".format(current_sprite))
            
            for pixel in current_sprite:
                
                if x_axis >= 64:
                    break
                
                screen_pixel = self.pixels_on_screen[x_axis][y_axis]
                print("Sprite Pixel: {0}  Screen Pixel: {1}".format(pixel, screen_pixel))
                 
                if pixel == "1" and screen_pixel == 1:
                    self.pixels_on_screen[x_axis][y_axis] = 0      
                    self.register_v[0xf] = 1
                    self.display.delete_pixel(x_axis, y_axis)
                    print("Delete at {0} {1}".format(x_axis,y_axis))
                    
                if pixel == "1" and screen_pixel == 0:
                    self.pixels_on_screen[x_axis][y_axis] = 1
                    self.display.draw_pixel(x_axis, y_axis)
                    print("Draw at {0} {1}".format(x_axis,y_axis))
                
                x_axis+=1
            y_axis+=1
            
            if y_axis >= 32:
                break
                
                  
class Screen:
    def __init__(self) -> None:
        pygame.init()
        self.x_axis = 0
        self.y_axis = 0
        self.clear = False
        self.screen = pygame.display.set_mode((640,320))
        pygame.display.set_caption("CHIP 8 Emulator")    
    
    def draw_pixel(self, x_axis, y_axis):
        self.screen.set_at((x_axis, y_axis), (255, 255, 255))
        pygame.display.flip()
        
    def delete_pixel(self, x_axis, y_axis):
        self.screen.set_at((x_axis, y_axis), (0, 0, 0))
        pygame.display.flip()
    
    def clear_screen(self):
        self.screen.fill((0,0,0))
        pygame.display.flip()
        
    def quit(self):
        pygame.quit()
        

    
def Emulator():
    cpu = CPU("logo.ch8")
    


if __name__ == '__main__':
    Emulator()