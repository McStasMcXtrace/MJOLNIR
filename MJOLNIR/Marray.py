import numpy as np
import itertools

class Marray(object):
    """Collection object for masked arrays"""
    def __init__(self, data=None, cls = np.ma.MaskedArray):
        if data is None:
            self._data = np.asarray(data).view(cls)
        elif isinstance(data,list):#len(data.shape) > 1:
            if len(data) >0:
                if isinstance(data[0],np.ndarray): # Something else than an array
                    self._data = [np.asarray(dat).view(cls) for dat in data]
                else:
                    self._data = np.asarray(data).view(cls)
            else:
                self._data = [np.asarray(data).view(cls)]
        else:
            self._data = [np.asarray(data).view(cls)]
        

    @property
    def multidimensional(self):
        return self._multidimensional
    
    @multidimensional.getter
    def multidimensional(self):
        if isinstance(self._data,list):
            return True
        else:
            return False
    
    @property
    def data(self):
        return self._data
    
    @data.getter
    def data(self):
        return self._data
    
    @data.setter
    def data(self,data):
        self._data = data
    
    
    
    @property
    def mask(self):
        return self._mask
    
    @mask.getter
    def mask(self):
        if self.multidimensional:
            mask = []
            for i in range(len(self)):
                mask.append(self._data[i].mask)
        else:
            mask = self._data.mask
            
        return mask
    
    @mask.setter
    def mask(self,mask):
        try:
            len(mask)
        except:
            if isinstance(mask,(bool,np.bool_)):
                if self.multidimensional:
                    for i in range(len(self)):
                        self._data[i].mask = mask
                else:
                    self._data.mask = mask
            else:
                return AttributeError('Provided mask does not fit the length of Marray.')
        else:
            if len(mask) != len(self._data):
                raise AttributeError('Provided mask does not fit the length of Marray. Mask has length {} while array has length {}'.format(len(mask),len(self)))
            else:
                if self.multidimensional:
                    for i in range(len(self)):
                        self._data[i].mask = mask[i]
                else:
                    self._data.mask = mask
    def __iter__(self):
        self._index=0
        return self
    
    def __next__(self):
        if self._index >= len(self):
            raise StopIteration
        result = self._data[self._index]
        self._index += 1
        return result

    def next(self):
        return self.__next__()
    
    
    
    def __len__(self):
        if self.multidimensional:
            return len(self._data)
        else:
            if not self._data.shape is ():
                return len(self._data)
            else:
                return 0
    

    def __getitem__(self,index):
        return self._data[index]
    
    def __setitem__(self,index,value):
        self._data[index] = value
        
    def __delitem__(self,index):
        del self._data[index]

    def extractData(self):
        if self.multidimensional:
            data = []
            for d in self:
                data.append(d.compressed())
            data = np.concatenate(data)
        else:
            data = self._data.compressed()
        return data
    
    def append(self,d):
        self._data.append(d)
        
    def __str__(self):
        return '\n'.join(str(x) for x in self)
    
    def compress(self):
        return self.extractData()
    
    def flatten(self):
        data = []
        for d in self:
            data.append(d)
        return data
    
    def max(self,axis=None,out=None):
        newAxis,zeroAxis = axisChecker(axis)
        if zeroAxis:
            am = []
            for d in self:
                am.append(np.max(d,axis=newAxis,out=out))
        else:
            am = [np.max(d,axis=newAxis,out=out) for d in self]
            am = am[np.argmax(am)]
        return am
    
    def min(self,axis=None,out=None):
        newAxis,zeroAxis = axisChecker(axis)
        if zeroAxis:
            am = []
            for d in self:
                am.append(np.min(d,axis=newAxis,out=out))
        else:
            am = [np.min(d,axis=newAxis,out=out) for d in self]
            am = am[np.argmin(am)]
        return am
    
    def reshape(self,shape):
        if self.multidimensional:
            try:
                shapeLen = len(shape)
            except TypeError: # If integer
                for d in self:
                    d.reshape(shape)
            else:
                if shape[0] == len(self):
                    data = []
                    try:
                        len(shape[1])
                    except:
                        for d in self:
                            data.append(d.reshape(shape[1:]))
                    else:
                        for d,s in zip(self._data,shape[1]):
                            data.append(d.reshape(s))
                    self.data = data
                else:
                    raise AttributeError('Shape provided ({}) does not fit Marray of length {}'.format(shape,len(self)))
        else:
            try:
                len(shape)
            except:
                shape = [shape]
            for d,sh in zip(self,shape):
                d.reshape(sh)

    def __mul__(self,other):
        if isinstance(other,Marray):
            data = [s*o for s,o in zip(self.data,other.data)]
            mask = combineMasks(self.mask,other.mask)
            returnMat = Marray(data)
            returnMat.mask = mask
            return returnMat
        else:
            data = [s*other for s in self.data]
            returnMat = Marray(data)
            returnMat.mask = self.mask
            return returnMat

    __rmul__ = __mul__#def __rmul__(self,other):
        #return self.__mul__(self,other)

    def __add__(self,other):
        if isinstance(other,Marray):
            data = [s+o for s,o in zip(self.data,other.data)]
            mask = combineMasks(self.mask,other.mask)
            returnMat = Marray(data)
            returnMat.mask = mask
            return returnMat
        else:
            data = [s+other for s in self.data]
            returnMat = Marray(data)
            returnMat.mask = self.mask
            return returnMat
    
    __radd__ = __add__#(self,other):
    def __sub__(self,other):
        if isinstance(other,Marray):
            data = [s-o for s,o in zip(self.data,other.data)]
            mask = combineMasks(self.mask,other.mask)
            returnMat = Marray(data)
            returnMat.mask = mask
            return returnMat
        else:
            data = [s-other for s in self.data]
            returnMat = Marray(data)
            returnMat.mask = self.mask
            return returnMat
    
    def __rsub__(self,other):
        """if isinstance(other,Marray):
            data = [o-s for s,o in zip(self.data,other.data)]
            mask = combineMasks(self.mask,other.mask)
            returnMat = Marray(data)
            returnMat.mask = mask
            return returnMat
        else:"""
        data = [other-s for s in self.data]
        returnMat = Marray(data)
        returnMat.mask = self.mask
        return returnMat

    @property
    def shape(self):
        return self._shape

    @shape.getter
    def shape(self):
        if self.multidimensional:
            return [x.shape for x in self]
        else:
            return self._data.shape
    
    @shape.setter
    def shape(self,shape):
        self.reshape(shape)
    
    def swapaxes(self,axis1,axis2):
        for d in self:
            d.swapaxes(axis1,axis2)
    
    def transpose(self,*axis):
        for d in self:
            d.transpose(*axis)

    @property
    def size(self):
        return self._size
    
    @size.getter
    def size(self):
        totalSize = np.sum([x.size for x in self])
        return totalSize

def axisChecker(axis):
    """Checks the axis provided in numpy functions. Returns axis decremented by one and boolean if 0 is in original axis."""
    if not axis is None:
        try:
            ax = np.asarray(axis)
        except TypeError:
            if axis == 0:
                returnAxis = None
                returnBool = True
            else:
                returnAxis = axis
                returnBool = False
        else:
            try:
                _ = len(ax)
            except TypeError:
                returnAxis = axis-1
            else:
                returnAxis = tuple([a-1 for a in ax if a!=0])
            returnBool = 0 in ax
    else:
        returnAxis = axis
        returnBool = False

    return returnAxis,returnBool

def combineMasks(ownMask,otherMask):
    if isinstance(ownMask,np.bool_):
        if isinstance(otherMask,np.bool_):
            mask = ownMask or otherMask
        else:
            mask = [sm + om for sm,om in itertools.zip_longest([ownMask],otherMask,fillvalue=ownMask)]
    elif isinstance(otherMask,np.bool_):
        mask = [sm + om for sm,om in itertools.zip_longest(ownMask,[otherMask],fillvalue=otherMask)]
    else:
        mask = [sm + om for sm,om in zip(ownMask,otherMask)]
    return mask

def test_Marray_initialize():
    Empty = Marray()
    assert(len(Empty)==0)

def test_Marray_1D():
    shortList = Marray([0,1,2,3,4])
    assert(shortList.multidimensional == False)

    shortList[0] = 10
    shortList[1] = -10
    assert(np.max(shortList) == 10)
    assert(np.min(shortList) == -10)

    shortList = 10*shortList
    assert(np.max(shortList) == 100)
    assert(np.min(shortList) == -100)

    shortList = 10+shortList-5
    assert(np.max(shortList) == 105)
    assert(np.min(shortList) == -95)
    try:
        shortList.mask = [0,0,0,0,0,0,0,0,0,0,0]
        assert False # Wrong shape for list
    except AttributeError:
        assert True

    shortList = shortList+shortList

    mask = np.zeros(len(shortList),dtype=bool)
    mask[-2:] = True
    shortList.mask = mask
    assert(np.all(shortList.mask == mask))
    assert(len(shortList.extractData())==np.sum(1-mask))
    assert(np.all(shortList.extractData() == shortList.compress()))

    shortList.mask = False
    assert(len(shortList)==5)
    assert(len(shortList.flatten())==5)

    shortList.shape = (-1)
    shortList.shape = -1
    assert(shortList.shape == (len(shortList),))

def test_Marray_multiD():
    A = Marray([np.random.rand(i,2,3) for i in [1,2,3]])
    assert(len(A) == 3)
    assert(np.all([np.all(np.isclose(AData,AD)) for AData,AD in zip(A._data,A)]))
    assert(A.multidimensional == True)

    _temp = A[-1].copy()
    del A[-1]
    assert(len(A) == 2)
    A.append(_temp)
    assert(len(A) == 3)

    string = str(A)

    A[2][0,1,1] = 20
    A[2][0,0,0] = -20

    assert(np.min(A) == -20)
    assert(np.max(A) == 20)

    assert(len(np.max(A,axis=0))==3)
    assert(len(np.min(A,axis=0))==3)
    A.mask = -1

    mask = [np.zeros(d.shape,dtype=bool) for d in A]
    mask[0][0,1,:] = True
    mask[2][1,0,1] = True
    A.mask = mask
    assert(len(A.extractData())==np.sum([np.array(M).size for M in mask])-np.sum([np.sum(M) for M in mask]))
    assert(np.all(A.extractData() == A.compress()))

    A.shape = (3,-1)
    assert(np.all(A.shape == np.array([(6,), (12,), (18,)])))
    A.shape = (3,[(1, 2, 3), (2, 2, 3), (3, 2, 3)])
    assert(np.all(A.shape == np.array([(1, 2, 3), (2, 2, 3), (3, 2, 3)])))

    0-A-A+2*A-0

    B = Marray([np.random.rand(i,2,3) for i in [1,2,3]])
    B.mask = False

    A+B
    B+A