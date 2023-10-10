import keyboard


class Keypad:
    
    def __init__(self) -> None:
        self.keys = {
            "1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
            "Q": 0x4, "W": 0x5, "E": 0x6, "R": 0xD,
            "A": 0x7, "S": 0x8, "D": 0x9, "F": 0xE,
            "Z": 0xA, "X": 0x0, "C": 0xB, "V": 0xF,
        }
    
    def getKeyEvent(self):
        while True:
            key = keyboard.read_key()
            
            if key in self.keys:
                break

        return self.keys[key]
    
    def keyOperationEvent(self, value):
        key = list(self.keys.values()).index(value)
        print(key)
        if keyboard.is_pressed(key):
            return True
        else:
            return False
        