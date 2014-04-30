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

import ctypes
from pyelliptic.openssl import OpenSSL
from echelper import ECHelper
import curve as ec_curve
import bignum as ec_bignum

class Point:
    '''
    classdocs
    '''


    def __init__(self, curve, openssl_point=None, x=None, y=None):
        '''
        Constructor
        '''
        if not isinstance( curve, ec_curve.Curve ):
            raise Exception( 'Provided curve is not a Curve object' )
        
        self.curve = curve
        self.os_group = curve.os_group
        
        if openssl_point is not None:
            self.__set_to_openssl_point( openssl_point )
        elif x is not None and y is not None:
            self.__set_to_coordinates( x, y )
        else:
            raise Exception( 'No point given' )

    def __set_to_openssl_point(self, point):
        try:
            x, y = ec_bignum.BigNum(), ec_bignum.BigNum()

            # Put X and Y coordinates of public key into x and y vars
            OpenSSL.EC_POINT_get_affine_coordinates_GFp( self.os_group, point, x.bn, y.bn, None )

            self.x, self.y = x.get_value(), y.get_value()
            self.os_point = point
        finally:
            del x, y
            
    def __set_to_coordinates(self, x_val, y_val):
        try:
            point= OpenSSL.EC_POINT_new( self.os_group )
            x, y = ec_bignum.BigNum( decval=x_val ), ec_bignum.BigNum( decval=y_val )
            
            if self.curve.field_type == 'prime':
                OpenSSL.EC_POINT_set_affine_coordinates_GFp( self.os_group, point, x.bn, y.bn, None )
            elif self.curve.field_type == 'characteristic-two':
                OpenSSL.EC_POINT_set_affine_coordinates_GF2m( self.os_group, point, x.bn, y.bn, None )
                
            self.x, self.y = x_val, y_val
            self.os_point = point
        finally:
            del x, y
            
    def __eq__(self, other):
        if type(other) is type(self):
            return self.x == other.x and self.y == other.y
        return False
    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        """
        Add two EC points together
        """
        if isinstance( other, Point ):
            result = OpenSSL.EC_POINT_new( self.os_group )
            OpenSSL.EC_POINT_add( self.os_group, result, self.os_point, other.os_point, 0 )
            return Point( self.curve, openssl_point=result )
        else:
            return NotImplemented
            
    def __mul__(self, other):
        """
        Multiply an EC point by a scalar value
        and returns the multiplication result
        """
        if isinstance( other, int ) or isinstance( other, long ):
            try:
                o = ec_bignum.BigNum( decval=other )
                result = OpenSSL.EC_POINT_new( self.os_group )
                OpenSSL.EC_POINT_mul( self.os_group, result, 0, self.os_point, o.bn, 0 )
                return Point( self.curve, openssl_point=result )
            finally:
                del o
        else:
            return NotImplemented
            
    __rmul__ = __mul__
            
    def __str__(self):
        return "Point<0x%X, 0x%X>" % ( self.x, self.y )

    __repr__ = __str__
