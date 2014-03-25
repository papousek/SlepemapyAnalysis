# -*- coding: utf-8 -*-

import StringIO

''' Kartograph accepts stream to write generated map. However it tries to close 
    the stream after writing, which is not what we would want if we want edit to
    the map straight away. 
'''
class MyStringIO(StringIO.StringIO):
    def __init__(self):
        StringIO.StringIO.__init__(self)
    
    def close(self):
        pass

    def real_close(self):
        super(StringIO.StringIO,self).close()