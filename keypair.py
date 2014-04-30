'''
Created on 30/04/2014

@author: Jesper
'''

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
            
    def __str__(self):
        return "KeyPair<Private:%X, Public:%s>" % ( self.private_key, self.public_key )