# MIT License
#
# Copyright (C) 2014 Jesper Borgstrup
# -------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

from pyelliptic.openssl import OpenSSL
from echelper import ECHelper

class BigNum:
    '''
    classdocs
    '''

    def __init__(self, os_bn=None,decval=None,binval=None):
        """
        Constructs a new BN object
        and fills it with the value given.
        """
        if os_bn is not None:
            self.bn = os_bn
            self.__created_bn = False
        else:
            self.bn = OpenSSL.BN_new()
            self.__created_bn = True
            if decval is None and binval is None:
                decval = 0
                
            if decval is not None:
                binval = ECHelper.int2bin( decval )
                
            if binval is not None:
                OpenSSL.BN_bin2bn( binval, len( binval ), self.bn )
        
    def get_value(self):
        binary = OpenSSL.malloc(0, OpenSSL.BN_num_bytes( self.bn ) )
        OpenSSL.BN_bn2bin( self.bn, binary )
        return int( binary.raw.encode('hex') or '0', 16 )
    
    def __del__(self):
        if self.__created_bn:
            OpenSSL.BN_free( self.bn )
        
    def __str__(self):
        return "BigNum<0x%X>" % self.get_value()

    __repr__ = __str__
