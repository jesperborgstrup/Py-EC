'''
Created on 30/04/2014

@author: Jesper
'''

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
        return "BigNum<%X>" % self.get_value()

    __repr__ = __str__
