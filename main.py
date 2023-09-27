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
            time.sleep(0.05)
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
        exit()
            
    def decode_instruction(self, instruction):
        opcode = instruction >> 12
        print(hex(instruction))
        # print("Instruction type: {0}".format(opcode))
        
        X = (instruction >> 8) & 0xf           # Second nibble
        Y = (instruction >> 4) & 0xfff & 0xf   # Third nibble
        N = instruction & 0xf                  # Fourth nibble
        NN = instruction & 0xff                # Second byte
        NNN = instruction & 0xfff              # Second, third, and fourth nibbles
        
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
                self.skip_instruction(0x3, X, Y, NN)
            
            case 0x4: # 4XNN - Done
                self.skip_instruction(0x4, X, Y, NN)
            
            case 0x5: # 5XY0 - Done
                self.skip_instruction(0x5, X, Y, NN)
                
            case 0x6: # 6XNN - Done
                self.set_register_vx(X, NN)
                
            case 0x7: # 7XNN - Done
                self.add_to_register_vx(X, NN)
                
            case 0x8:
                match N:
                    case 0x0: # 8XY0
                        self.set_register_vx(X, self.register_v[Y])
                        
                    case 0x1: # 8XY1
                        value = self.register_v[X] | self.register_v[Y]
                        self.set_register_vx(X, value)
                    
                    case 0x2: # 8XY2
                        value = self.register_v[X] & self.register_v[Y]
                        self.set_register_vx(X, value)
                    
                    case 0x3: # 8XY3
                        value = self.register_v[X] ^ self.register_v[Y]
                        self.set_register_vx(X, value)
                        
                    case 0x4: # 8XY4
                        value = self.register_v[X] + self.register_v[Y]
                        value = value if value < 255 else 0
                        self.set_register_vx(X, value)
                        
                    case 0x5: # 8XY5
                        pass
                    
                    case 0x6: # 8XY6
                        pass
                    
                    case 0x7: # 8XY7
                        pass
                    
                    case 0xE: # 8XYE
                        pass
                    
                    
            case 0x9: # 9XY0 - Done
                self.skip_instruction(0x9, X, Y, NN)
                            
            case 0xA: # ANNN - Done
                self.set_index(NNN)
                
            case 0xB: # BNNN
                pass
            
            case 0xC: # CXNN - Done
                self.random_set(NN, X)
            
            case 0xE: 
                match NN:
                    case 0x9E: # EX9E
                        pass
                    case 0xA1: # EXA1
                        pass
               
            case 0xD: # DXYN - Done
                self.draw_sprite(X, Y, N)     
                
            case 0xF: 
                match NN:
                    case 0x07: # FX07
                        pass
                    case 0x0A: # FX0A
                        pass  
                    case 0x15: # FX15
                        pass
                    case 0x18: # FX18
                        pass
                    case 0x1E: # FX1E
                        pass  
                    case 0x29: # FX29
                        pass
                    case 0x33: # FX33
                        pass
                    case 0x55: # FX55
                        pass  
                    case 0x65: # FX65
                        pass

            case _: # Unknown
                print("Unknown instruction {:x}".format(instruction))
                
    def clear_screen(self):
        self.display.clear_screen()
        
    def call_subroutine(self,NNN):
        self.memory_stack.append(self.pc)
        self.pc = NNN
    
    def return_from_subroutine(self):
        self.pc = self.memory_stack.pop(-1)
    
    def jump_program_counter(self, NNN):
        self.pc = NNN
            
    def set_register_vx(self, X, value):
        self.register_v[X] = value
    
    def add_to_register_vx(self, X, NN):
        self.register_v[X] += NN

    def set_index(self, NNN):
        self.register_I = NNN
     
    def skip_instruction(self, opcode, X, Y, NN):
        if opcode == 0x3 and self.register_v[X] == NN:
            self.pc += 2
        
        if opcode == 0x4 and self.register_v[X] != NN:
            self.pc += 2
        
        if opcode == 0x5 and self.register_v[X] == self.register_v[Y]:
            self.pc += 2
        
        if opcode == 0x9 and self.register_v[X] != self.register_v[Y]:
            self.pc += 2
            
    def random_set(self, NN, X):
        num = random.randrange(255)
        self.register_v[X] = num & NN
        
    def draw_sprite(self, X, Y, N):
        x_axis = self.register_v[X] % 64
        y_axis = self.register_v[Y] % 32
        self.register_v[0xf] = 0   
        print("\nNew Draw")
        
        for row in range(N):
            current_sprite = "{0:08b}".format(self.memory[self.register_I + row])
            print("Sprite: {0}".format(current_sprite))
            
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
                
                  
class Screen:
    def __init__(self) -> None:
        pygame.init()
        scaling_factor = 10
        self.screen = pygame.display.set_mode((64*scaling_factor,32*scaling_factor))
        self.w = pygame.Surface((64,32))
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