import time
import scanner

class fi_5110Cdj(scanner.direct_scanner):
    def __init__(self, config):
        scanner.direct_scanner.__init__(self, config)
        self.doc                = None
        self.default_buttons    = {}
        self.name = "fi-5110Cdj"
        for i in range(1,10):
            button = config.parser.get('fi-5110Cdj', str(i))
            button = button.split(' ')
            button[1] = 'ADF '+button[1]
            button[2] = int(button[2])
            self.default_buttons[i] = button 

    def get_sources(self):
        return ('ADF Front', 'ADF Back', 'ADF Duplex')

    def get_colorspaces(self):
        return ('Color', 'Gray', 'Halftone', 'Lineart')

    def set_parameters(self, scanner, mode='Color', source='ADF Front', resolution=300):
        scanner.source     = source
        scanner.mode       = mode
        scanner.resolution = resolution
                
        scanner.pageheight = 297
        scanner.pagewidth  = 210
        scanner.br_y       = 297
        scanner.br_x       = 210

    def scan(self, buttons_pressed = None, doc = None):
        print buttons_pressed

    def wait_for_button(self, scanner):
        pressed_scan = 0
        pressed_send = 0
        while (not (pressed_scan or pressed_send)) and self.connected:
            pressed_scan = scanner.button_scan
            pressed_send = scanner.button_send
            self.event.wait(2)
        if not self.connected:
            return None
        return pressed_scan, pressed_send, scanner.button_function

