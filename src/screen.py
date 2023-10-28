import pygame


class Screen:
    def __init__(self) -> None:
        self.scaling_factor = 5
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
        
        for x in range(-pixel_size, pixel_size+1):
            for y in range(-pixel_size, pixel_size+1):
                self.screen.set_at((x_axis+x, y_axis+y), (0, 0, 0))
        
        pygame.display.flip()
    
    def clear_screen(self):
        self.screen.fill((0,0,0))
        pygame.display.flip()
    
        