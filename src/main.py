from math import floor
import pygame
import time
import random
# import keyboard
import threading


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
        
        self.pixels_on_screen = [[0] * 32 for i in range(64)]

        self.delay_timer = 0
        self.sound_timer = 0
        self.display = Screen()
        
        main_thread = threading.Thread(target=self.init_ROM, args=(file_name,))
        sound_thread = threading.Thread(target=self.init_sound_timer, args=())
        delay_thread = threading.Thread(target=self.init_delay_timer, args=())
        
        main_thread.start()
        sound_thread.start()
        delay_thread.start()
        
        
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
    
    def init_sound_timer(self):
        
        while True:
            if self.sound_timer > 0:
                self.sound_timer -= 1
            time.sleep(0.02)
                
    def init_delay_timer(self):
        
        while True:
            if self.delay_timer > 0:
                self.delay_timer -= 1
            time.sleep(0.02)
    
    def fetch_instructions(self):
        num_of_intructions = 0
        start = time.time()
    
        while self.pc < len(self.memory):
            time.sleep(0.01)
            num_of_intructions+=1
                
            first_byte = self.memory[self.pc]
            second_byte = self.memory[self.pc + 1]
            combinedBytes = (first_byte << 8) | second_byte
            
            self.pc_flag = False
            
            self.decode_instruction(combinedBytes)
            
            if not self.pc_flag:
                self.pc += 2
            
        end = time.time()
        time_took = end-start
        print("Number of Instructions: {0} \nTime took: {1}".format(num_of_intructions,time_took))
        exit()
            
    def decode_instruction(self, instruction):
        opcode = instruction >> 12
        
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
                    match NNN:
                        case 0xE0: # 00E0 
                            self.clear_screen()
                        case 0xEE: # 00EE
                            self.return_from_subroutine()
                    
                case 0x1: # 1NNN 
                    self.jump_program_counter(NNN)
                    
                case 0x2: # 2NNN 
                    self.call_subroutine(NNN)
                    
                case 0x3: # 3XNN 
                    if self.register_v[X] == NN:
                        self.skip_instruction()
                
                case 0x4: # 4XNN
                    if self.register_v[X] != NN:
                        self.skip_instruction()
                
                case 0x5: # 5XY0
                    if self.register_v[X] == self.register_v[Y]:
                        self.skip_instruction()
                    
                case 0x6: # 6XNN
                    self.set_register_v(X, NN)
                    
                case 0x7: # 7XNN
                    self.add_to_register_v(X, NN)
                    
                case 0x8:
                    match N:
                        case 0x0: # 8XY0
                            self.set_register_v(X, self.register_v[Y])
                            
                        case 0x1: # 8XY1
                            self.set_register_v(X, self.register_v[X] | self.register_v[Y])
                        
                        case 0x2: # 8XY2 
                            self.set_register_v(X, self.register_v[X] & self.register_v[Y])
                        
                        case 0x3: # 8XY3 
                            self.set_register_v(X, self.register_v[X] ^ self.register_v[Y])
                            
                        case 0x4: # 8XY4 
                            self.set_register_v(X, self.register_v[X] + self.register_v[Y])
                            if (self.register_v[X] + self.register_v[Y]) > 255:
                                self.set_register_v(0xF, 1)
                            else:
                                self.set_register_v(0xF, 0)
                            
                        case 0x5: # 8XY5 
                            self.add_to_register_v(X, -self.register_v[Y])
                            if self.register_v[Y] < self.register_v[X]:
                                self.set_register_v(0xF, 1)
                            else:
                                self.set_register_v(0xF, 0)
                            
                        case 0x6: # 8XY6 
                            if (self.register_v[Y] & 1) == 1:
                                self.set_register_v(0xF, 1)
                            else:
                                self.set_register_v(0xF, 0)
                            self.set_register_v(X, self.register_v[Y] >> 1)
                        
                        case 0x7: # 8XY7
                            self.set_register_v(X, self.register_v[Y] - self.register_v[X])
                            if self.register_v[Y] > self.register_v[X]:
                                self.set_register_v(0xF, 1)
                            else:
                                self.set_register_v(0xF, 0)
                        
                        case 0xE: # 8XYE 
                            if ((self.register_v[Y] >> 7) & 1) == 1:
                                self.set_register_v(0xF, 1)
                            else:
                                self.set_register_v(0xF, 0)
                            self.set_register_v(X, self.register_v[Y] << 1)
                        
                        
                case 0x9: # 9XY0
                    if self.register_v[X] != self.register_v[Y]:
                        self.skip_instruction()
                                
                case 0xA: # ANNN
                    self.set_register_I(NNN)
                    
                case 0xB: # BNNN
                    self.jump_program_counter(NNN+self.register_v[0])
                
                case 0xC: # CXNN 
                    self.random_set(X, NN)
                
                case 0xE: 
                    match NN:
                        case 0x9E: # EX9E
                            pass
                            
                        case 0xA1: # EXA1
                            pass
                
                case 0xD: # DXYN 
                    self.draw_sprite(X, Y, N)     
                    
                case 0xF: 
                    match NN:
                        case 0x07: # FX07
                            self.set_register_v(X, self.delay_timer)
                            
                        case 0x0A: # FX0A
                            pass
                            
                        case 0x15: # FX15
                            self.set_delay_timer(X)
                            
                        case 0x18: # FX18
                            self.set_sound_timer(X)
                            
                        case 0x1E: # FX1E 
                            self.add_to_register_I(X)
                            
                        case 0x29: # FX29
                            self.set_register_I(5*self.register_v[X])
                            
                        case 0x33: # FX33 
                            self.binary_coded_decimal(X)
                        
                        case 0x55: # FX55 
                            self.store_memory(X)
                            
                        case 0x65: # FX65 
                            self.load_memory(X)

                
    def clear_screen(self):
        print("Clear display")
        self.display.clear_screen()
        
    def call_subroutine(self, value):
        print("Call subroutine")
        self.memory_stack.append(self.pc+2)
        self.pc = value
        self.pc_flag = True
    
    def return_from_subroutine(self):
        print("Return from subroutine")
        self.pc = self.memory_stack.pop(-1)
        self.pc_flag = True
    
    def jump_program_counter(self, value):
        print("Jump")
        self.pc = value
        self.pc_flag = True
            
    def set_register_v(self, address, value):
        print("Set register v")
        value = value % 256
        self.register_v[address] = value
    
    def add_to_register_v(self, address, value):
        print("Add to register v")
        value += self.register_v[address]
        value = value % 256
        self.register_v[address] = value

    def set_register_I(self, value):
        print("Set register I")
        self.register_I = value
        
    def add_to_register_I(self, address):
        print("Add to register I")
        self.register_I += self.register_v[address]
     
    def skip_instruction(self):
        print("Skip Instruction") 
        self.pc += 4
        self.pc_flag = True
            
    def random_set(self, X, value):
        print("Random Set")
        num = random.randrange(255)
        self.register_v[X] = num & value
        
    def draw_sprite(self, X, Y, N):
        print("Draw Sprite")
        x_axis = self.register_v[X] % 64
        y_axis = self.register_v[Y] % 32
        
        self.register_v[0xF] = 0   
        
        for row in range(N):
            current_sprite = "{0:08b}".format(self.memory[self.register_I + row])
            
            for column, pixel in enumerate(current_sprite):
                
                if (x_axis+column) >= 64:
                    break

                screen_pixel = self.pixels_on_screen[x_axis+column][y_axis]
                 
                if pixel == "1" and screen_pixel == 1:
                    self.pixels_on_screen[x_axis+column][y_axis] = 0      
                    self.register_v[0xF] = 1
                    self.display.delete_pixel(x_axis+column, y_axis)
                    
                if pixel == "1" and screen_pixel == 0:
                    self.pixels_on_screen[x_axis+column][y_axis] = 1
                    self.display.draw_pixel(x_axis+column, y_axis)
            
                
            y_axis+=1
            
            if y_axis >= 32:
                break
            
    def set_sound_timer(self, X):
        print("Set sound timer")
        self.sound_timer = self.register_v[X]
        
    def set_delay_timer(self, X):
        print("Set delay timer")
        self.delay_timer = self.register_v[X]

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
        self.scaling_factor = 6
        self.screen = pygame.display.set_mode((64*self.scaling_factor,32*self.scaling_factor))
        pygame.display.set_caption("CHIP 8 Emulator")    
    
    def draw_pixel(self, x_axis, y_axis):
        pixel_size = self.scaling_factor-1
        x_axis = x_axis*self.scaling_factor
        y_axis = y_axis*self.scaling_factor
        self.screen.set_at((x_axis, y_axis), (255, 255, 255))

        for x in range(-pixel_size, pixel_size+1):
            for y in range(-pixel_size, pixel_size+1):
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
        

    
def Interpreter():
    path = r"/home/abdi/Documents/GitHub/CHIP-8-emulator/test/flags.ch8"
    cpu = CPU(path)
    


if __name__ == '__main__':
    Interpreter()