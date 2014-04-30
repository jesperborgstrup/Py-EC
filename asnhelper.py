class ASNHelper:
    CLASS_UNIVERSAL = 0
    CLASS_APPLICATION = 1
    CLASS_CONTEXT_SPECIFIC = 2
    CLASS_PRIVATE = 3
    
    PC_PRIMITIVE = 0
    PC_CONSTRUCTED = 1
    
    TAG_INTEGER = 0x02
    TAG_OCTET_STRING = 0x04
    TAG_OBJECT_IDENTIFIER = 0x06
    TAG_SEQUENCE = 0x10
    
    @staticmethod
    def consume(buf):
        while len( buf ) > 0:
            buf, (cls, pc, tag) = ASNHelper.consume_type( buf )
            buf, length = ASNHelper.consume_length( buf )
            data, buf = buf[:length], buf[length:]
#            print (cls, pc, tag, length)
            if tag == ASNHelper.TAG_INTEGER or tag == ASNHelper.TAG_OCTET_STRING:
                yield int( "".join( map( lambda x: "%X" % ord(x), data ) ), 16 )
            elif tag == ASNHelper.TAG_OCTET_STRING:
                yield data
            elif tag == ASNHelper.TAG_OBJECT_IDENTIFIER:
                yield ".".join( map( lambda x: "%d" % ord(x), data ) )
            elif tag == ASNHelper.TAG_SEQUENCE:
                yield tuple( [ x for x in ASNHelper.consume( data ) ] )
    
    @staticmethod
    def consume_type(buf):
        type_octet, buf = ord(buf[0]), buf[1:]
        cls, type_octet = type_octet >> 6, type_octet & 0x3F
        pc, type_octet = type_octet >> 5, type_octet & 0x1F
        tag = type_octet
        return buf, (cls, pc, tag)
    
    @staticmethod
    def consume_length(buf):
        first_octet, buf = ord(buf[0]), buf[1:]
        long_form = first_octet & 0x80 == 0x80
        if not long_form:
            return buf, int(first_octet)
        else:
            octet_count = int(first_octet) - 0x80
            length_octets, buf = buf[:octet_count], buf[octet_count:]
            length = int( "".join( map( lambda x: "%X" % ord(x), length_octets )), 16 )
            return buf, length
            
