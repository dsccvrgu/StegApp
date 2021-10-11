#!/usr/bin/env python3

import cv2

class AppError(BaseException):
  pass

def i2bin(i, l):
  actual = bin(i)[2:]
  if len(actual) > l:
    raise AppError("bit size is larger than expected.")

  while len(actual) < l:
    actual = "0"+actual

  return actual

def char2bin(c):
  return i2bin(ord(c), 8)

# LSB used to do image manipulation especially embedding secret message
# using LSB method
class LSB():

  # before embedding secret message on image, we need
  # to know which cell is used or will be used to store
  # secret message, to achive that, we will use 16 first cell
  # to store length, this value will be converted to binary
  # and no more that 16 bit which means max length of message is
  # 2^16 = 65536
  MAX_BIT_LENGTH = 16

  def __init__(self, img):
    self.size_x, self.size_y, self.size_channel = img.shape

    self.image = img
    # pointer used to refer which cell on image will be read or write
    self.cur_x = 0
    self.cur_y = 0
    self.cur_channel = 0

  # move pointer to next cell
  def next(self):
    if self.cur_channel != self.size_channel-1:
      self.cur_channel += 1
    else:
      self.cur_channel = 0
      if self.cur_y != self.size_y-1:
        self.cur_y += 1
      else:
        self.cur_y = 0
        if self.cur_x != self.size_x-1:
          self.cur_x += 1
        else:
          raise AppError("need larger image")

  # replace last bit from value of cell referred by pointer
  # and move pointer to next cell
  def put_bit(self, bit):
    v = self.image[self.cur_x, self.cur_y][self.cur_channel]

    binaryV = bin(v)[2:]

    # replace last bit if different
    if binaryV[-1] != bit:
      binaryV = binaryV[:-1]+bit

    self.image[self.cur_x, self.cur_y][self.cur_channel] = int(binaryV,2)
    self.next()

  # put_bits put array of bit to designated cell respectively
  def put_bits(self, bits):
    for bit in bits:
      self.put_bit(bit)

  # read_bit read last bit from value of cell referred by pointer
  # return bit as result
  def read_bit(self):
    v = self.image[self.cur_x, self.cur_y][self.cur_channel]
    return bin(v)[-1]

  # read_bits read last bit for every cell referred by pointer until length
  # return array of bit as result
  def read_bits(self, length):
    bits = ""
    for _ in range(0, length):
      bits += self.read_bit()
      self.next()

    return bits

  # embed embed text to image
  def embed(self, text):
    # calculate text length and convert it to binary with length 16 bit
    text_length = i2bin(len(text), self.MAX_BIT_LENGTH)
    # put length to first 16 cell
    self.put_bits(text_length)

    # put every character on text to image
    for c in text:
      # convert character into binary with 8 length
      bits = char2bin(c)
      # put every bit to cell respectively
      self.put_bits(bits)

  # extract extract text from image
  def extract(self):
    # read 16 first cell as length of text that contained on image
    length = int(self.read_bits(self.MAX_BIT_LENGTH), 2)
    text = ""
    for _ in range(0, length):
      # read every 8 bit as a character
      c = int(self.read_bits(8), 2)
      # convert binary as a character
      text += chr(c)

    return text

  # save save image to dstPath
  def save(self, dstPath):
    cv2.imwrite(dstPath, self.image)

if __name__ == "__main__":
  # obj = LSB(cv2.imread('src.jpg'))
  # obj.embed("I'm sure that one day everything will happen, you will love me and will never let me go I want to be with you, I want to love your flaws, always willing to make you happy no matter what happens, I promise I am...")

  obj = LSB(cv2.imread('dst.png'))
  text = obj.extract()
  print(text)
