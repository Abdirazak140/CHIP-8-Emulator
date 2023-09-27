from math import floor
import pygame
import time
import random

class CPU:
    def __init__(self, file_name):
        self.memory = [0] * 4096 
        self.memory_stack = []
        self.register_v = [0] * 16
        self.register_I = 0
        self.pc = 0x200
        self.pc_flag = False
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
            time.sleep(0.1)
            num_of_intructions+=1
                
            first_byte = self.memory[self.pc]
            second_byte = self.memory[self.pc + 1]
            combinedBytes = (first_byte << 8) | second_byte
            
            self.pc_flag = False
            
            self.decode_instruction(combinedBytes)
            print(self.register_v)
            if not self.pc_flag:
                self.pc += 2
            
        end = time.time()
        time_took = end-start
        print("Number of Instructions: {0} \nTime took: {1}".format(num_of_intructions,time_took))
        exit()
            
    def decode_instruction(self, instruction):
        opcode = instruction >> 12
        # print(hex(instruction))
        # print("Instruction type: {0}".format(opcode))
        
        X = (instruction >> 8) & 0xf           # Second nibble
        Y = (instruction >> 4) & 0xfff & 0xf   # Third nibble
        N = instruction & 0xf                  # Fourth nibble
        NN = instruction & 0xff                # Second byte
        NNN = instruction & 0xfff              # Second, third, and fourth nibbles
        
        if instruction == 0x0000:
            print("No instruction")
        else:
            match opcode:
                case 0x0: 
                    match NN:
                        case 0xE0: # 00E0 - Done
                            self.clear_screen()
                        case 0xEE: # 00EE - Done
                            self.return_from_subroutine()
                    
                case 0x1: # 1NNN - Done
                    self.jump_program_counter(NNN)
                    
                case 0x2: # 2NNN - Done
                    self.call_subroutine(NNN)
                    
                case 0x3: # 3XNN - Done
                    if self.register_v[X] == NN:
                        self.skip_instruction()
                
                case 0x4: # 4XNN - Done
                    if self.register_v[X] != NN:
                        self.skip_instruction()
                
                case 0x5: # 5XY0 - Done
                    if self.register_v[X] == self.register_v[Y]:
                        self.skip_instruction()
                    
                case 0x6: # 6XNN - Done
                    self.set_register_vx(X, NN)
                    
                case 0x7: # 7XNN - Done
                    self.add_to_register_vx(X, NN)
                    
                case 0x8:
                    match N:
                        case 0x0: # 8XY0 - Done
                            self.set_register_vx(X, self.register_v[Y])
                            
                        case 0x1: # 8XY1 - Done
                            value = self.register_v[X] | self.register_v[Y]
                            self.set_register_vx(X, value)
                        
                        case 0x2: # 8XY2 - Done
                            value = self.register_v[X] & self.register_v[Y]
                            self.set_register_vx(X, value)
                        
                        case 0x3: # 8XY3 - Done
                            value = self.register_v[X] ^ self.register_v[Y]
                            self.set_register_vx(X, value)
                            
                        case 0x4: # 8XY4 - Done
                            value = self.register_v[X] + self.register_v[Y]
                            if value > 255:
                                self.set_register_vx(0xF, 1)
                            else:
                                self.set_register_vx(0xF, 0)
                            self.set_register_vx(X, value)
                            
                        case 0x5: # 8XY5 - Done
                            value = self.register_v[X] - self.register_v[Y]
                            if self.register_v[X] > self.register_v[Y]:
                                self.set_register_vx(0xF, 1)
                            else:
                                self.set_register_vx(0xF, 0)
                                
                            self.set_register_vx(X, value)
                        
                        case 0x6: # 8XY6 - Done
                            value = self.register_v[Y] >> 1
                            bit  = self.register_v[Y] & 1
                            if bit == 1:
                                self.set_register_vx(0xF, 1)
                            else:
                                self.set_register_vx(0xF, 0)
                            self.set_register_vx(X, value)
                        
                        case 0x7: # 8XY7 - Done
                            value = self.register_v[Y] - self.register_v[X]
                            if self.register_v[Y] > self.register_v[X]:
                                self.set_register_vx(0xF, 1)
                            else:
                                self.set_register_vx(0xF, 0)
                                
                            self.set_register_vx(X, value)
                        
                        case 0xE: # 8XYE - Done
                            value = self.register_v[Y] << 1
                            bit  = (self.register_v[Y] >> 7) & 1
                            if bit == 1:
                                self.set_register_vx(0xF, 1)
                            else:
                                self.set_register_vx(0xF, 0)
                            self.set_register_vx(X, value)
                        
                        
                case 0x9: # 9XY0 - Done
                    if self.register_v[X] != self.register_v[Y]:
                        self.skip_instruction()
                                
                case 0xA: # ANNN - Done
                    self.set_index(NNN)
                    
                case 0xB: # BNNN
                    pass
                
                case 0xC: # CXNN - Done
                    self.random_set(NN, X)
                
                case 0xE: 
                    match NN:
                        case 0x9E: # EX9E
                            print("Not implemented")
                            
                        case 0xA1: # EXA1
                            print("Not implemented")
                
                case 0xD: # DXYN - Done
                    self.draw_sprite(X, Y, N)     
                    
                case 0xF: 
                    match NN:
                        case 0x07: # FX07
                            print("Not implemented")
                            
                        case 0x0A: # FX0A
                            print("Not implemented")
                            
                        case 0x15: # FX15
                            print("Not implemented")
                            
                        case 0x18: # FX18
                            print("Not implemented")
                            
                        case 0x1E: # FX1E - Done
                            self.add_to_index(X)
                            
                        case 0x29: # FX29
                            print("Not implemented")
                            
                        case 0x33: # FX33 - Done
                            self.binary_coded_decimal(X)
                        
                        case 0x55: # FX55 - Done
                            self.store_memory(X)
                            
                        case 0x65: # FX65 - Done
                            self.load_memory(X)

                case _: # Unknown
                    print("Unknown instruction {:x}".format(instruction))
                
    def clear_screen(self):
        print("Clear display")
        self.display.clear_screen()
        
    def call_subroutine(self, NNN):
        print("Call subroutine")
        self.memory_stack.append(self.pc+2)
        self.pc = NNN
        self.pc_flag = True
    
    def return_from_subroutine(self):
        print("Return from subroutine")
        self.pc = self.memory_stack.pop(-1)
        self.pc_flag = True
    
    def jump_program_counter(self, NNN):
        print("Jump")
        self.pc = NNN
        self.pc_flag = True
            
    def set_register_vx(self, X, value):
        print("Set register vx")
        self.register_v[X] = value
    
    def add_to_register_vx(self, X, NN):
        print("Add to register vx")
        self.register_v[X] += NN

    def set_index(self, NNN):
        print("Set Index")
        self.register_I = NNN
        
    def add_to_index(self, X):
        self.register_I += self.register_v[X]
     
    def skip_instruction(self):
        print("Skip Instruction") 
        self.pc += 2
        self.pc_flag = True
            
    def random_set(self, NN, X):
        print("Random Set")
        num = random.randrange(255)
        self.register_v[X] = num & NN
        
    def draw_sprite(self, X, Y, N):
        print("Draw Sprite")
        x_axis = self.register_v[X] % 64
        y_axis = self.register_v[Y] % 32
        self.register_v[0xf] = 0   
        
        for row in range(N):
            current_sprite = "{0:08b}".format(self.memory[self.register_I + row])
            
            for column, pixel in enumerate(current_sprite):
                
                if (x_axis+column) >= 64:
                    break

                screen_pixel = self.pixels_on_screen[x_axis+column][y_axis]
                 
                if pixel == "1" and screen_pixel == 1:
                    self.pixels_on_screen[x_axis+column][y_axis] = 0      
                    self.register_v[0xf] = 1
                    self.display.delete_pixel(x_axis+column, y_axis)
                    
                if pixel == "1" and screen_pixel == 0:
                    self.pixels_on_screen[x_axis+column][y_axis] = 1
                    self.display.draw_pixel(x_axis+column, y_axis)
                
            y_axis+=1
            
            if y_axis >= 32:
                break
    
    def binary_coded_decimal(self, X):
        print("BCD")
        value = self.register_v[X]
        for n in reversed(range(3)):
            self.memory[self.register_I+n] = floor(value % 10)
            value = value / 10
        
    def store_memory(self, X):
        print("Store Memory")
        for n in range(X+1):
            self.memory[self.register_I+n] = self.register_v[n]
    
    def load_memory(self, X):
        print("Load Memory")
        for n in range(X+1):
            self.register_v[n] = self.memory[self.register_I+n]
    
                
                  
class Screen:
    def __init__(self) -> None:
        pygame.init()
        self.scaling_factor = 3
        self.screen = pygame.display.set_mode((64*self.scaling_factor,32*self.scaling_factor))
        pygame.display.set_caption("CHIP 8 Emulator")    
    
    def draw_pixel(self, x_axis, y_axis):
        pixel_size = self.scaling_factor-1
        x_axis = x_axis*self.scaling_factor
        y_axis = y_axis*self.scaling_factor
        self.screen.set_at((x_axis, y_axis), (255, 255, 255))
        
        for x in [-pixel_size, 0, pixel_size]:
            for y in [-pixel_size, 0, pixel_size]:
                 self.screen.set_at((x_axis+x, y_axis+y), (255, 255, 255))
            
        pygame.display.flip()
        
    def delete_pixel(self, x_axis, y_axis):
        pixel_size = self.scaling_factor-1
        x_axis = x_axis*self.scaling_factor
        y_axis = y_axis*self.scaling_factor
        self.screen.set_at((x_axis, y_axis), (0, 0, 0))
        
        for x in [-pixel_size, 0, pixel_size]:
            for y in [-pixel_size, 0, pixel_size]:
                self.screen.set_at((x_axis+x, y_axis+y), (0, 0, 0))
        
        pygame.display.flip()
    
    def clear_screen(self):
        self.screen.fill((0,0,0))
        pygame.display.flip()
        
    def quit(self):
        pygame.quit()
        

    
def Emulator():
    path = r"C:\Users\YusufAbd\Libraries\Documents\GitHub\CHIP-8-emulator\test\IBM_logo2.ch8"
    cpu = CPU(path)
    


if __name__ == '__main__':
    Emulator()