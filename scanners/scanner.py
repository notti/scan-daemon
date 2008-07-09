class scanner:
    def __init__(self, config):
        pass

    def get_sources(self):
        pass

    def get_colorspaces(self):
        pass

    def set_parameters(self, scanner, mode, source, resolution):
        pass

    def wait_for_button(self, scanner):
        pass

    def status_change(self, status):
        print str(self) + " " + status
