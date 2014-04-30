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
import curve as ec_curve
import point as ec_point
import bignum as ec_bignum

class KeyPair:
    '''
    classdocs
    '''


    def __init__(self, curve, os_key=None, private_key=None):
        '''
        Constructor
        '''
        if not isinstance( curve, ec_curve.Curve ):
            raise Exception( 'Provided curve is not a Curve object' )
        
        self.curve = curve
        self.os_group = curve.os_group

        if os_key is not None:
            self.os_key = os_key
        else:
            self.os_key = OpenSSL.EC_KEY_new()
            OpenSSL.EC_KEY_set_group( self.os_key, self.os_group )
            if private_key is not None:
                privk = ec_bignum.BigNum( decval=private_key )
                pubk = private_key * curve.G
                OpenSSL.EC_KEY_set_private_key( self.os_key, privk.bn )
                OpenSSL.EC_KEY_set_public_key( self.os_key, pubk.os_point )
            else:
                OpenSSL.EC_KEY_generate_key( self.os_key )

        try:
            priv_key = ec_bignum.BigNum( OpenSSL.EC_KEY_get0_private_key( self.os_key ) )
            self.private_key = priv_key.get_value()
            self.public_key = ec_point.Point( self.curve, openssl_point=OpenSSL.EC_KEY_get0_public_key( self.os_key ) )
        finally:
            del priv_key
            
    def __eq__(self, other):
        if type(other) is type(self):
            return self.private_key == other.private_key and \
                   self.public_key == other.public_key
        return False
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "KeyPair<Private:0x%X, Public:%s>" % ( self.private_key, self.public_key )

    __repr__ = __str__
