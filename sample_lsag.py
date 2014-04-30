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

import hashlib
import time
from random import randint

from echelper import ECHelper
from curve import Curve
from keypair import KeyPair


CURVE = "secp256k1"
KEY_COUNT = 10000
DEBUG = False

def sign(curve, keys, signer_index, message="Hello message"):
    key_count = len( keys )

    # Set signer
    signer = keys[signer_index]

    # Make room for c_i, s_i, z'_i, and z''_i variables
    cs = [0] * key_count
    ss = [0] * key_count
    z_s = [0] * key_count
    z__s = [0] * key_count

    # Retrieve all public keys and their coordinates
    public_keys = map( lambda key: key.public_key, keys )
    public_keys_coords = map( lambda point: (point.x, point.y), public_keys )

    # Step 1
    public_keys_hash = curve.hash_to_field( "%s" % public_keys_coords )
    H = H2( curve, public_keys_coords )
    Y_tilde = signer.private_key * H

    # Step 2
    u = randint( 0, curve.order )
    pi_plus_1 = (signer_index+1) % key_count
    cs[pi_plus_1] = H1( curve, public_keys_hash, Y_tilde, message,
                        u * curve.G, u * H )

    # Step 3
    for i in range( signer_index+1, key_count ) + range( signer_index ):
        ss[i] = randint( 0, curve.order )
        next_i = (i+1) % key_count
        z_s[i] = ss[i] * curve.G + cs[i] * public_keys[i]
        z__s[i] = ss[i] * H + cs[i] * Y_tilde
        cs[next_i] = H1( curve, public_keys_hash, Y_tilde, message, z_s[i], z__s[i] )

    # Step 4
    ss[signer_index] = ( u - signer.private_key * cs[signer_index] ) % curve.order

    if DEBUG:
        print "SIGN H: %s" % H
        print "SIGN Y_tilde: %s" % Y_tilde
        for i in range( len( cs ) ):
            print "SIGN  c_%d:   %d" % ( i, cs[i] )
            print "SIGN  s_%d:   %d" % ( i, ss[i] )
            if z_s[i] != 0:
                print "SIGN  Z_%d: %s" % ( i, z_s[i] )
            if z__s[i] != 0:
                print "SIGN Z__%d: %s" % ( i, z__s[i] )
            print "-----------------------------------------"

    return ( public_keys, 
             message, 
             cs[0], 
             ss, 
             Y_tilde
           )

def verify( curve, public_keys, message, c_0, ss, Y_tilde ):
    public_keys_coords = map( lambda point: ( point.x, point.y ) , public_keys )

    n = len( public_keys )

    cs = [c_0] + [0] * ( n - 1 )
    z_s = [0] * n
    z__s = [0] * n

    # Step 1
    public_keys_hash = curve.hash_to_field( "%s" % public_keys_coords )
    H = H2( curve, public_keys_coords )
    for i in range( n ):
        z_s[i] = ss[i] * curve.G + cs[i] * public_keys[i]
        z__s[i] = ss[i] * H + cs[i] * Y_tilde
        if i < n - 1:
            cs[i+1] = H1( curve, public_keys_hash, Y_tilde, message, z_s[i], z__s[i] )

    H1_ver = H1( curve, public_keys_hash, Y_tilde, message, z_s[n-1], z__s[n-1] )

    if DEBUG:
        print "VERIFY H: %s" % H
        for i in range( len( cs ) ):
            print "VERIFY  c_%d:   %d" % ( i, cs[i] )
            print "VERIFY  s_%d:   %d" % ( i, ss[i] )
            print "VERIFY  Z_%d:   %s" % ( i, z_s[i] )
            print "VERIFY Z__%d:   %s" % ( i, z__s[i] )
            print "-----------------------------------------"

        print "VERIFY H1_ver==c_0: (%d == %d)" % ( H1_ver, cs[0] )

    return cs[0] == H1_ver

def H2( curve, in_str ):
    """
    Hash the input as a string and return the hash as an integer.
    """
    return curve.hash_to_point( "H2_salt%s" % in_str )

def H1( curve, keys, Y_tilde, message, P1, P2):
    """
    The H1 function that hashes a lot of variables
    and returns the hash as an integer.
    """
    str = "%s,%s,%s,%X,%X,%X,%X" % ( keys, Y_tilde, message,
                                     P1.x, P1.y, P2.x, P2.y)
    return curve.hash_to_field( "H1_salt%s" % str )

def get_signature_size( signature ):
    public_keys, message, c_0, ss, Y_tilde = signature
    # Each public key is 64 bytes (32 bytes per coordinate)
    size = 64 * len( public_keys )
    size += len( ECHelper.int2bin( c_0 ) )
    size += sum( map( lambda s: len( ECHelper.int2bin( s ) ), ss ) )
    # Y_tilde is also a point, which again requires 64 bytes
    size += 64
    return size

def run_test( curve, keys, signer_index ):
    signature = sign( curve, keys, signer_index )
    assert verify( curve, *signature )
    return get_signature_size( signature )

def run_multiple_tests( curve, keys, signer_index=0, tests=1 ):
    t_start = time.time()
    size = sum( map( lambda _: run_test( curve, keys, signer_index ), range( tests ) ) )
    t_end = time.time()
    t = t_end - t_start
    print "Signing and verifying %d messages with %d keys took %.3f seconds (%.3f s/msg, %.3f ms/msg/key)" \
                % ( tests, len( keys ), t, t / tests, 1000 * t / tests / len( keys ) )
    print "The %d signatures were %d bytes in total (%.3f b/test, %.3f b/test/key)" % ( tests, size, float(size) / tests, float(size) / tests / len(keys) )
    return ( len( keys ), tests, t, size )

def run():
    curve = Curve( CURVE )

    # Generate private/public key pairs
    print "Generating %d key pairs..." % KEY_COUNT
    t = time.time()
    key_gen_time = keys = map( lambda _: KeyPair( curve ), range( KEY_COUNT ) )
    print "Generating %d key pairs took %.3f seconds" % ( KEY_COUNT, time.time() - t )

    results = []

    for i in [ 2, 3, 5, 10, 20, 30, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000]:
        results.append( run_multiple_tests( curve, keys[0:i], tests=10 ) )

    print repr( results )   

if __name__ == "__main__":
    run()