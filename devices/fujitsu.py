import time
import device


class fi_5110Cdj(device.usb_scanner):
    USB_ID_VENDOR  = 0x04c5
    USB_ID_PRODUCT = 0x1097
    IN_ENDPOINT    = 0x02
    OUT_ENDPOINT   = 0x81

    GET_OPTIONS    = '\x43\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc2\x00\x00\x00\x00\x00\x00\x00\x0c\x00\x00\x00'

    def __init__(self, config, worker):
        device.usb_scanner.__init__(self, config, worker)
        self.doc                = None
        self.default_buttons    = {}
        self.name = "fi-5110Cdj"
        for i in range(1,11):
            button = config.parser.get('fi-5110Cdj', str(i))
            button = button.split(' ')
            button[1] = 'ADF '+button[1]
            self.default_buttons[i] = button 

    def get_sources(self):
        return ('ADF Front', 'ADF Back', 'ADF Duplex')

    def get_colorspaces(self):
        return ('Color', 'Gray', 'Halftone', 'Lineart')

    def read_buttons(self):
        self.send(self.GET_OPTIONS)
        data   = self.recieve(12)
        status = self.recieve(13)
        ret = {}
        ret["function"]     = data[5]
        ret["button_send"]  = (data[4]>>2)&1
        ret["button_scan"]  = (data[4])&1
        ret["top_edge"]     = (data[2]>>7)&1
        ret["adf_loaded"]   = not ((data[3]>>7)&1)
        ret["omr"]          = (data[3]>>6)&1
        ret["adf_open"]     = (data[3]>>5)&1
        ret["powersave"]    = (data[4]>>7)&1
        ret["doublefeed"]   = (data[6])&1
        ret["errorcode"]    = data[7]
        return ret

    def get_sane_name(self):
        return 'fujitsu:'+self.get_address()

    def wait_for_button(self, scanner):
        pressed_scan = 0
        pressed_send = 0
        while (not (pressed_scan or pressed_send)) and self.connected:
            try:
                status = self.read_buttons()
            except:
                self.connected = False
                break
            pressed_scan = status["button_scan"]
            pressed_send = status["button_send"]
            self.event.wait(2)
        if not self.connected:
            return None
        button = self.default_buttons[status["function"]]
        return {'document-type': button[3], 'source': button[1], 'mode': button[0], 'resolution': button[2], 'document-finish': pressed_scan}

devices = {'fi-5110Cdj': fi_5110Cdj}
