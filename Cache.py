from Block import Block
import  math

'''
MIT License

Copyright (c) 2018 Reza Baharani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
 
	A simple cache simulator developed by Reza Baharani
	This code is developed for Computer Architecture subject
	University of North Carolina, Charlotte, USA
'''

class Cache:
    def __init__(self,  addressBitSize, name,  size,  block_size,  associativity):
        self.name = name
        self.addressBitSize = addressBitSize
        self.size = size
        self.block_size=block_size
        self.associativity = associativity
        self.index = int(size /(block_size * associativity))
        self.indexBitSize = int(math.log(self.index,  2))
        self.offsetBitSize = int(math.log(block_size,  2))
        self.tagBitSize = self.addressBitSize-(self.offsetBitSize + self.indexBitSize)
        self.sets={}
        self.tagMask=0
        self.indexMask=0
        self.access = 0
        self.miss = 0
        
    def construct(self):
        for i in range(0,  (self.index)):
            for j in range(0,  self.associativity):
                b = Block(0,  0)
                self.sets[i,  j]={0:b} #tag value, block
        self.calculateTagMask()
        self.calculateIndexMask()
                
    def calculateTagMask(self):
        for i in range(0,  self.tagBitSize):
            self.tagMask = self.tagMask << 1
            self.tagMask = self.tagMask | 1
        for i in range(0,  self.addressBitSize - self.tagBitSize):
            self.tagMask = self.tagMask << 1
            
    def extractTagValue(self,  addr):
        return (addr & self.tagMask)
        
    def extractIndexValue(self,  addr):
        return (addr & self.indexMask)
    
    def calculateIndexMask(self):
        for i in range(0,  self.indexBitSize):
            self.indexMask = self.indexMask << 1
            self.indexMask = self.indexMask | 1
        for i in range(0,  self.offsetBitSize):
            self.indexMask = self.indexMask << 1
            
    def replaceBlock(self,  tag,  index):
        whichBlockIsBetter = -1 # associativity number
        LRU_Set = -1
        leastLRUVal = -1
        b = Block(0,  1)
        for i in range(0,  self.associativity):
            if(whichBlockIsBetter == -1):
                data = self.sets[index,  i]
                block = list(data.values())[0]
                if (block.isValid == True):
                    if(leastLRUVal < 0):
                        leastLRUVal = block.access
                        LRU_Set = i
                    else:
                        if(block.access < leastLRUVal):
                            leastLRUVal = block.access
                            LRU_Set = i
                else:
                    whichBlockIsBetter = i
                    break
        if(whichBlockIsBetter == -1):
            self.sets[index,  LRU_Set] = {tag : b}
        else:
            self.sets[index,  whichBlockIsBetter] = {tag : b}

    def read(self,  address, print_res = True):
        index = (self.extractIndexValue(address)>>self.offsetBitSize)
        tag = self.extractTagValue(address)
        self.access = self.access + 1
        hit = False
        for i in range(0,  self.associativity):
            data = self.sets[index,  i]
            block = data.get(tag)
            if(hit == False):
                if(block):
                    if (block.isValid == True):
                        block.read()
                        hit = True
                else:
                    if(i == (self.associativity-1)):
                        self.replaceBlock(tag, index)
        if(not(hit)):
            self.miss = self.miss + 1
