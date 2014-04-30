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

class ECHelper:
	@staticmethod
	def int2bin(i):
		"""
		Takes an integer and returns a bitstring (big endian)
		representing the integer.
		"""
		result = []
		while i:
			result.append(chr(i&0xFF))
			i >>= 8
		result.reverse()
		return ''.join(result)

	@staticmethod
	def modular_sqrt(a, p):
		""" Find a quadratic residue (mod p) of 'a'. p
			must be an odd prime.

			Solve the congruence of the form:
				x^2 = a (mod p)
			And returns x. Note that p - x is also a root.

			0 is returned is no square root exists for
			these a and p.

			The Tonelli-Shanks algorithm is used (except
			for some simple cases in which the solution
			is known from an identity). This algorithm
			runs in polynomial time (unless the
			generalized Riemann hypothesis is false).

			Originally taken from
			http://eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python/
		"""
		# Simple cases
		#
		if ECHelper.legendre_symbol(a, p) != 1:
			return 0
		elif a == 0:
			return 0
		elif p == 2:
			return p
		elif p % 4 == 3:
			return pow(a, (p + 1) / 4, p)

		# Partition p-1 to s * 2^e for an odd s (i.e.
		# reduce all the powers of 2 from p-1)
		#
		s = p - 1
		e = 0
		while s % 2 == 0:
			s /= 2
			e += 1

		# Find some 'n' with a legendre symbol n|p = -1.
		# Shouldn't take long.
		#
		n = 2
		while ECHelper.legendre_symbol(n, p) != -1:
			n += 1

		# Here be dragons!
		# Read the paper "Square roots from 1; 24, 51,
		# 10 to Dan Shanks" by Ezra Brown for more
		# information
		#

		# x is a guess of the square root that gets better
		# with each iteration.
		# b is the "fudge factor" - by how much we're off
		# with the guess. The invariant x^2 = ab (mod p)
		# is maintained throughout the loop.
		# g is used for successive powers of n to update
		# both a and b
		# r is the exponent - decreases with each update
		#
		x = pow(a, (s + 1) / 2, p)
		b = pow(a, s, p)
		g = pow(n, s, p)
		r = e

		while True:
			t = b
			m = 0
			for m in xrange(r):
				if t == 1:
					break
				t = pow(t, 2, p)

			if m == 0:
				return x

			gs = pow(g, 2 ** (r - m - 1), p)
			g = (gs * gs) % p
			x = (x * gs) % p
			b = (b * g) % p
			r = m


	@staticmethod
	def legendre_symbol(a, p):
		""" Compute the Legendre symbol a|p using
			Euler's criterion. p is a prime, a is
			relatively prime to p (if p divides
			a, then a|p = 0)

			Returns 1 if a has a square root modulo
			p, -1 otherwise.

			Originally taken from
			http://eli.thegreenplace.net/2009/03/07/computing-modular-square-roots-in-python/
		"""
		ls = pow(a, (p - 1) / 2, p)
		return -1 if ls == p - 1 else ls
