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
import math
import hashlib

from pyelliptic.openssl import OpenSSL
from echelper import ECHelper
from asnhelper import ASNHelper
import point as ec_point

class Curve:
    '''
    classdocs
    '''


    def __init__(self, curvename=None, curveid=None, openssl_group=None):
        '''
        Constructor
        '''
        if curvename != None:
            curve = OpenSSL.get_curve( curvename )
            self.os_group = OpenSSL.EC_GROUP_new_by_curve_name( curve )
        elif curveid != None:
            self.os_group = OpenSSL.EC_GROUP_new_by_curve_name( curveid )
        elif openssl_group != None:
            self.os_group = openssl_group
        else:
            raise Exception('No curve provided')
        self.__set_parameters()
        self.__set_base_point()
        
    def __set_parameters(self):
        size = OpenSSL.i2d_ECPKParameters(self.os_group, 0)
        mb = ctypes.create_string_buffer(size)
        OpenSSL.i2d_ECPKParameters(self.os_group, ctypes.byref(ctypes.pointer(mb)))
        asntree = [x for x in ASNHelper.consume( mb.raw )][0]
        self.ver, self.field, self.curve, self.G_raw, self.order, self.h = asntree
        
        if self.field[0] == '42.134.72.206.61.1.1': # Prime field
            self.field_type = 'prime'
            self.p = self.field[1]
            self.bitlength = int( math.ceil( math.log( self.p, 2 ) ) )
            self.a = self.curve[0]
            self.b = self.curve[1]
            self.f = lambda x: x**3 + self.a*x + self.b
        elif self.field[0] == '42.134.72.206.61.1.2': # Characteristic two field
            self.field_type = 'power-of-two'
            self.m = self.field[1][0]
            # Maybe bitlength below is not correct..?
            self.bitlength = self.m + 1
            if self.field[1][1] == '42.134.72.206.61.1.2.3.2': # Only one coefficient
                self.poly_coeffs = [self.field[1][2]]
            elif self.field[1][1] == '42.134.72.206.61.1.2.3.3': # Several coefficients
                self.poly_coeffs = self.field[1][2]
            else:
                raise Exception('Unknown field OID %s' % self.field[1][1])
            self.a = self.curve[0]
            self.b = self.curve[1]
        else:
            raise Exception( 'Unknown curve field' )
        
    def __set_base_point(self):
        self.G = ec_point.Point( self, openssl_point=OpenSSL.EC_GROUP_get0_generator( self.os_group ) )
        
    def hash_to_field(self, in_str):
        return int( hashlib.sha512( in_str ).hexdigest()[:self.bitlength//4], 16 )
    
    def hash_to_point(self, in_str):
        return self.find_point_try_and_increment( self.hash_to_field( in_str ) )
        
    def find_point_try_and_increment(self, x):
        if self.field_type != 'prime':
            raise Exception( "find_point_try_and_increment is only implemented for curves over prime fields")
        
        ## HUSK AT FREE BIGNUMS
        found = False
        x -= 1
        while not found:
            x += 1
            f_x = self.f( x )
            y = ECHelper.modular_sqrt( f_x, self.p )
            if y != 0:
                return ec_point.Point( self, x=x, y=y )
                    
    def __eq__(self, other):
        if type(other) is type(self):
            return self.ver == other.ver and \
                   self.field == other.field and \
                   self.curve == other.curve and \
                   self.G_raw == other.G_raw and \
                   self.order == other.order and \
                   self.h == other.h
        return False
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.field_type == 'prime':
            field = "Prime field, p: 0x%X" % self.p
            equation = "y^2 = x^3"
            if self.a != 0:
                equation += "%+dx" % ( self.a )
            if self.b != 0:
                equation += "%+d" % ( self.b )
            equation += " (mod p)"
        elif self.field_type == 'power-of-two':
            field = "Power-of-two field, f(x): x^%d+%s1" % ( self.m, "".join( map( lambda x: "x^%d+" % x, reversed( self.poly_coeffs ) ) ) )
            equation = "y^2+xy = x^3"
            if self.a != 0:
                equation += "%+dx" % ( self.a )
            if self.b != 0:
                equation += "%+d" % ( self.b )
            
        return "Curve<Equation: %s, Field: %s>" % ( equation, field )

    __repr__ = __str__
