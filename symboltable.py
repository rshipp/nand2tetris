
class SymbolTable:
    def __init__(self):
        self._class = None
        self._function = None
        self.table = {}

    def track(self, name, type, kind):
        if kind in ['static', 'field']:
            num = len([v for v in self.table[self._class]['vars'] 
                       if v['kind'] == kind])
            self.table[self._class]['vars'][name] = {
                'type': type,
                'kind': kind,
                'num': num,
            }
        else:
            num = len([v for v in self.table[self._class]['functions'][self._function] 
                       if self.table[self._class]['functions'][self._function][v]['kind'] == kind])
            self.table[self._class]['functions'][self._function][name] = {
                'type': type,
                'kind': kind,
                'num': num,
            }

    def lookup(self, name, type, kind):
        pass

    def set_class(self, name):
        self.table[name] = {
            'functions': {},
            'vars': {},
        }
        self._class = name

    def set_function(self, name):
        self.table[self._class]['functions'][name] = {}
        self._function = name

    def get_class(self):
        return self._class

    def get_function(self):
        return self._function
