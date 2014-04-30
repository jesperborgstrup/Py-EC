# Py-EC

A wrapper of the OpenSSL elliptic curve functions for easy Python manipulation.

In Python, dealing directly with the OpenSSL library (through [PyElliptic](https://github.com/yann2192/pyelliptic)) easily becomes a hassle with the use of C pointers and string buffers.

To make things easier, I decided to make a wrapper for PyElliptic to make the manipulation of elliptic curves and points more Pythonic.

The wrapper has been tested with all recommended SEC curves (`secp192k1`, `secp192r1`, `secp224k1`, `secp224r1`, `secp256k1`, `secp256r1`, `secp384r1`, `secp521r1`, `sect163k1`, `sect163r1`, `sect163r2`, `sect233k1`, `sect233r1`, `sect239k1`, `sect283k1`, `sect283r1`, `sect409k1`, `sect409r1`, `sect571k1` and `sect571r1`).

Especially point addition and multiplication is way easier, as the following console example usage shows:

## Example use

```
>>> from curve import Curve
>>> c = Curve( 'secp256k1' )

>>> c
Curve<Equation: y^2 = x^3+7 (mod p), Field: Prime field, p: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F>

>>> c.p
115792089237316195423570985008687907853269984665640564039457584007908834671663L

>>> c.a
0

>>> c.b
7

>>> c.order
115792089237316195423570985008687907852837564279074904382605163141518161494337L

>>> c.G
Point<0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8>

>>> c.G.x
55066263022277343669578718895168534326250603453777594175500187360389116729240L

>>> c.G.y
32670510020758816978083085130507043184471273380659243275938904335757337482424L

>>> 4 * c.G + (255 * c.G)
Point<0xC2C80F844B70599812D625460F60340E3E6F36054A14546E6DC25D47376BEA9B, 0x86CA160D68F4D4E718B495B891D3B1B573B871A702B4CF6123ABD4483AA79C64>

>>> from keypair import KeyPair
>>> kp = KeyPair( c )

>>> kp
KeyPair<Private:0x5091AD80EEE3FB065A6E3FF126A112C4905F8E79566E22396807A55ADE1B5C6F, Public:Point<0x13FCF42341462150B8366F11659E396DF88D19F65D533CEEAC78C9EC6F94B45D, 0x18DDDF6DCA0C097FC0359E680BAED36403D77657ABE7F76E64E1B787D90C485A>>

>>> kp.private_key
36442418189203456142546292588071998273845228785350611568921618467649899682927L

>>> kp.public_key
Point<0x13FCF42341462150B8366F11659E396DF88D19F65D533CEEAC78C9EC6F94B45D, 0x18DDDF6DCA0C097FC0359E680BAED36403D77657ABE7F76E64E1B787D90C485A>
```

# API

## Curve

### Getting a curve instance
A curve can be initialized in three ways; by its name, id or by a pointer to an OpenSSL `EC_GROUP` instance:


```
>>> from curve import Curve

>>> Curve( curvename='secp256k1' )
Curve<Equation: y^2 = x^3+7 (mod p), Field: Prime field, p: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F>

>>> Curve( curveid=714 )
Curve<Equation: y^2 = x^3+7 (mod p), Field: Prime field, p: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F>

>>> from pyelliptic.openssl import OpenSSL
>>> Curve( openssl_group=OpenSSL.EC_GROUP_new_by_curve_name( 714 ) )
Curve<Equation: y^2 = x^3+7 (mod p), Field: Prime field, p: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F>
```

### Properties of a curve

Depending on whether the curve is over a prime field, F<sub>p</sub>, or a power-of-2 field, F<sub>2<sup>m</sup></sub>, the curve has slightly different properties:

* `prime_type`: Either `'prime'` or `'power-of-two'`
* `G`: The base `Point` (or generator) of the curve.
* `order`: The order of the curve (amount of elements)
* `h`: The cofactor of the curve
* `a`: The curve coefficient a
* `b`: The curve coefficient b
* `p` <b>(Only F<sub>p</sub>)</b>: The prime p specifying the field
* `m` <b>(Only F<sub>2<sup>m</sup></sub>)</b>: The integer m specifying the field
* `poly_coeffs` <b>(Only F<sub>2<sup>m</sup></sub>)</b>: The degrees of the polynomials specifying the field
* `os_group`: A pointer to the underlying `EC_GROUP` instance.

```
>>> from curve import Curve
>>> c1 = Curve( 'secp256k1' )
>>> c2 = Curve( 'sect239k1' )

>>> c1
Curve<Equation: y^2 = x^3+7 (mod p), Field: Prime field, p: 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F>
>>> c2
Curve<Equation: y^2+xy = x^3+1, Field: Power-of-two field, f(x): x^239+x^158+1>

>>> c1.field_type
'prime'
>>> c2.field_type
'power-of-two'

>>> c1.G
Point<0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8>
>>> c2.G
Point<0x29A0B6A887A983E9730988A68727A8B2D126C44CC2CC7B2A6555193035DC, 0x76310804F12E549BDB011C103089E73510ACB275FC312A5DC6B76553F0CA>

>>> c1.order
115792089237316195423570985008687907852837564279074904382605163141518161494337L
>>> c1.h
1
>>> c1.a
0
>>> c1.b
7

>>> c1.p
115792089237316195423570985008687907853269984665640564039457584007908834671663L

>>> c2.m
239
>>> c2.poly_coeffs
[158]
```

## Point

### Getting a point instance
You can get the base point from the `G` property of a curve as described above:

```
>>> from curve import Curve
>>> Curve( 'secp256k1' ).G
Point<0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8>
```

You can also create a point on a curve from either (1) the x and y coordinates of the point or (2) by a pointer to an OpenSSL `EC_POINT` instance:

```
>>> from curve import Curve
>>> from point import Point
>>> c = Curve( 'secp256k1' )

>>> Point( c, x=255, y=255 ) # Invalid coordinates, only a demonstration
Point<0xFF, 0xFF>

>>> from pyelliptic.openssl import OpenSSL
>>> Point( c, openssl_point=OpenSSL.EC_POINT_new( c.os_group ) )
Point<0x0, 0x0>
```

Finally, you can hash a string directly onto a curve (using the 'try-and-increment' method for finding points close to a certain x coordinate):

```
>>> from curve import Curve
>>> c = Curve( 'secp256k1' )

>>> c.hash_to_point( 'somestring' )
Point<0xE4998BB769D5AF19526738527E13ECF753F5CC7AA60DD0ADF94BB0A248CF577A, 0x79FCD45DD59999C5D916FB31C0F023B4A1A1BCD63F11FD3D3E31D5C5E7D79C1D>

>>> c.hash_to_point( 'someotherstring' )
Point<0xB661EE62474532EF1C8EA78B1CE3634E2EEC06B8E256E46A5CE25DF0FFABF332, 0x1DAB745A01B745CA9BF276D8E990E8EF11CFA954C5956DF9BF4C0684FABB00A6>
```

### Performing arithmetics
Point addition and multiplication is intuitive:

```
>>> from curve import Curve
>>> c = Curve( 'secp256k1' )

>>> c.G
Point<0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8>

>>> 2 * c.G
Point<0xC6047F9441ED7D6D3045406E95C07CD85C778E4B8CEF3CA7ABAC09B95C709EE5, 0x1AE168FEA63DC339A3C58419466CEAEEF7F632653266D0E1236431A950CFE52A>

>>> c.G + c.G
Point<0xC6047F9441ED7D6D3045406E95C07CD85C778E4B8CEF3CA7ABAC09B95C709EE5, 0x1AE168FEA63DC339A3C58419466CEAEEF7F632653266D0E1236431A950CFE52A>

>>> ( 5 * c.G ) + ( 256 * c.G )
Point<0x9CF606744CF4B5F3FDF989D3F19FB2652D00CFE1D5FCD692A323CE11A28E7553, 0x8147CBF7B973FCC15B57B6A3CFAD6863EDD0F30E3C45B85DC300C513C247759D>
```

### Properties of a point

* `x`: The x coordinate
* `y`: The y coordinate
* `os_point`: A pointer to the underlying `EC_POINT` instance.

## Key pair
A key pair is a structure that contains a private and a public key for a given curve.

### Getting a key pair instance
A key pair for a curve can be generated randomly or by providing a private key:

```
>>> from curve import Curve
>>> from keypair import KeyPair
>>> c = Curve( 'secp256k1' )

>>> KeyPair( c ) # Random key pair
KeyPair<Private:0x94087552C3C72CC867E555854B9DD6392A611A40C168B0C6B7AEFC63DD9F5818, Public:Point<0x7C3FF4B9AE4D4EFCD22185F5ED7B6C8EF79CFF83AC0A3DFA4A258CDDBFC2AC3E, 0xEBFD9904CB8398524022BCDC268D6B03207737F35E7591EE5ACEE338D5272733>>

>>> KeyPair( c, private_key=12345 )
KeyPair<Private:0x3039, Public:Point<0xF01D6B9018AB421DD410404CB869072065522BF85734008F105CF385A023A80F, 0xEBA29D0F0C5408ED681984DC525982ABEFCCD9F7FF01DD26DA4999CF3F6A295>>
```

Alternatively, you can provide a pointer to an OpenSSL `EC_KEY` instance:

```
>>> from curve import Curve
>>> from keypair import KeyPair
>>> from pyelliptic.openssl import OpenSSL
>>> c = Curve( 'secp256k1' )
>>> k = OpenSSL.EC_KEY_new_by_curve_name( 714 )
>>> OpenSSL.EC_KEY_generate_key( k )
1

>>> KeyPair( c, os_key=k )
KeyPair<Private:0xECBCB11DB69B0A8876986571E336A4F486E7B2C355712D2FA32C9836A153AAA, Public:Point<0x732F6911AC325F41CEAB478D4D5AE3EB033A06EA8ECC03AF58CF2FF022A1FE
5, 0x156B3C906BB70070B946F8565C425FEA00EA3350A71073F5B4818C96D41610C6>>
```

### Properties of a key pair

* `private_key`: The private key (an integer)
* `public_key`: The public key (a `Point`)
* `os_key`: A pointer to the underlying `EC_KEY` instance.

