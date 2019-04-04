#! python3
"""Module for BitVector class"""


class BitVector:
    """
    Class for manipulating bit vectors.  The vector is represented as a
    list of 1's and 0's.  Methods exist for translating the vector into strings,
    the numerical value, slicing subvectors, etc.  The downto parameter is
    used for determining the indexing orientation for slicing and bit selection.
    If downto is True, then the values are interpreted where the python list
    index 0 maps to len(_vlist)-1 and python list index max maps to 0.  This
    emulates manipulating vectors in HDL languages.
    """
    def __init__(self, vector_list=None, downto_val=True):
        self._vlist = []
        if vector_list is not None:
            for val in vector_list:
                self.validate(val)
            self._vlist = vector_list
        self._downto = downto_val

    @staticmethod
    def validate(bit):
        """Abstracting validation routine to make sure we only ever put in
        binary values into the list."""
        if not bit in (0, 1):
            raise ValueError("Vector list may only contain binary bit values (0,1).")

    @classmethod
    def from_int(cls, value):
        """This class method constructs a new instance of the class from
        an integer value."""
        binstr = "{:b}".format(value)
        binlist = [int(str) for str in list(binstr)]
        return cls(binlist)

    @property
    def downto(self):
        """Creating get/set pair for the direction variable."""
        return self._downto

    @downto.setter
    def downto(self, boolval):
        """Creating get/set pair for the direction variable."""
        self._downto = boolval

    def append(self, bit):
        """Appends a bit to the list on the right-hand side."""
        self._vlist.append(bit)

    @property
    def binstr(self):
        """Returns the vector as a string without any prefixed '0b'."""
        return "".join("{}".format(b) for b in self._vlist)

    @property
    def value(self):
        """Returns the integer value of the vector"""
        return int(self.binstr, 2)

    @property
    def hexstr(self):
        """Returns the vector as a string with a '0x' prefix."""
        return hex(self.value)

    @property
    def length(self):
        """Returns the vector length as an integer."""
        return len(self._vlist)

    @property
    def bit(self, start):
        """Returns a single bit value with index similar to HDL languages,
        paying attention to the slice direction."""
        if self._downto:
            vstart = self.length - start - 1
            return self._vlist[vstart]
        return self._vlist[start]

    def slice(self, start, stop):
        """Returns another BitVector object with the subslice within.  Pays
        attention to the slice direction for indexing."""
        if self._downto:
            vstart = self.length - start - 1
            vlen = start - stop + 1
            vstop = vstart + vlen
            return BitVector(self._vlist[vstart:vstop], self._downto)
        return BitVector(self._vlist[start : stop + 1], self._downto)
