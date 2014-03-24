import StringIO

class MyStringIO(StringIO.StringIO):
    def __init__(self):
        StringIO.StringIO.__init__(self)
    
    def close(self):
        pass
