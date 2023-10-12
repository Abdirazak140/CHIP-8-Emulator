import keyboard


class Keypad:
    
    def __init__(self) -> None:
        self.values_dict = {
            "1": 0x1, "2": 0x2, "3": 0x3, "4": 0xC,
            "Q": 0x4, "W": 0x5, "E": 0x6, "R": 0xD,
            "A": 0x7, "S": 0x8, "D": 0x9, "F": 0xE,
            "Z": 0xA, "X": 0x0, "C": 0xB, "V": 0xF,
        }
        self.keys_dict = {
            0x1: "1", 0x2: "2", 0x3: "3", 0xC: "4",
            0x4: "Q", 0x5: "W", 0x6: "E", 0xD: "R",
            0x7: "A", 0x8: "S", 0x9: "D", 0xE: "F",
            0xA: "Z", 0x0: "X", 0xB: "C", 0xF: "V",
        }
    
    def getKey(self):
        print("Get Value from key")
        while True:
            key = keyboard.read_key()
            
            if key.upper() in self.values_dict:
                break

        return self.values_dict[key.upper()]
    
    def keyOperation(self, value):
        print("Key operation")
        
        if keyboard.is_pressed(self.keys_dict[value].lower()):
            return True
        else:
            return False
        