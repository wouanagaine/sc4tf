
import wx
import sys
import struct
import time
import QFS
import tools3D
import Numeric
import Image
import ImageFilter
import ImageDraw
import PngImagePlugin
import JpegImagePlugin
import BmpImagePlugin
import GradientReader
import math

Image._initialized=2

import dircache
import os.path
from math import *

generic_saveValue = 3
COMPRESSED_SIG = 0xFB10

def Dot( v1, v2 ):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def Distance( n1, n2 ):
    dx = n1[0] - n2[0]
    dy = n1[1] - n2[1]
    return sqrt( dx*dx + dy*dy )

def Distance3D( p1, p2 ):
    dx = float(p1[0]-p2[0])
    dy = float(p1[1]-p2[1])
    dz = float(p1[2]-p2[2])
    return sqrt( dx*dx + dy*dy + dz*dz )

def Normalize( p1 ):
    dx = float(p1[0])
    dy = float(p1[1])
    if len( p1 ) == 3:
        dz = float(p1[2])
    else:
        dz = 0        
    norm = sqrt( dx*dx + dy*dy + dz*dz )
    try:
        if len( p1 ) == 3:
            return ( p1[0]/norm, p1[1]/norm, p1[2]/norm )
        else:
            return ( p1[0]/norm, p1[1]/norm )
    except:
        if len( p1 ) == 3:
            return ( 0, 0, 0 )
        else:
            return ( 0, 0 )

def ComputeNormal( height ):
  rawNorms = tools3D.generateNormals( height.shape, height.tostring() )
  norms = Numeric.fromstring( rawNorms, Numeric.Float32 )
  rawNorms = None
  norms = Numeric.reshape( norms, ( height.shape[0], height.shape[1], 3 )  )
  return norms

def ComputeShadowMap(  bLight, height, norms ):
  lightDir = Normalize( (1, -5, -1) )
  shadow = Numeric.zeros( height.shape, Numeric.Int8  )
  shadow[:] = 255
  rawShadow = shadow.tostring()
  yStart = 0
  yMax = height.shape[0]
  #tools3D.generateShadows( bLight,(yStart, yMax), lightDir, height.shape, height.tostring(), norms.tostring(), rawShadow )
  tools3D.generateShadows( bLight,(yStart, yMax), lightDir, height.shape, height.tostring(), "", rawShadow )
  print 'out of shadow',height.shape
  shadow = Numeric.fromstring( rawShadow, Numeric.Int8 )
  rawShadow = None  
  shadow = Numeric.reshape( shadow, height.shape  )
  print 'reshaped'
  
  return shadow
  
def ComputeOneRGB( bLight ,height, waterLevel):      
  lightDir = Normalize( (1, -5, -1) )
  rawRGB = tools3D.onePassColors( bLight, height.shape, waterLevel, height, GradientReader.paletteWater, GradientReader.paletteLand, lightDir )
  rgb = Numeric.fromstring( rawRGB, Numeric.Int8 )
  rgb = Numeric.reshape( rgb, ( height.shape[0], height.shape[1], 3 )  )
  return rgb
    
def ComputeRGB( height, normals, shadow, waterLevel ):    
  #rawRGB = tools3D.generateColors( height.shape, waterLevel, height, normals, shadow, GradientReader.paletteWater, GradientReader.paletteLand )
  rawRGB = tools3D.generateColors( height.shape, waterLevel, height, "", shadow, GradientReader.paletteWater, GradientReader.paletteLand )
  print "regeneration"
  rgb = Numeric.fromstring( rawRGB, Numeric.Int8 )
  rgb = Numeric.reshape( rgb, ( height.shape[0], height.shape[1], 3 )  )
  print "reshaped"
  return rgb
  
class SC4Entry( object ):
  def __init__( self, buffer, idx ):
    self.compressed = False
      
    self.buffer = buffer
    self.ident = struct.unpack( "H", buffer[ 0x0A:0x0A+2 ] )[0]    
    self.fileLocation = struct.unpack( "l", buffer[ 0x0C:0x0C+4 ] )[0]
    self.initialFileLocation = self.fileLocation
    self.filesize = struct.unpack( "l", buffer[ 0x10:0x10+4 ] )[0]
    self.order = idx
    t = struct.unpack( "L", buffer[ 0x00:0x00+4 ] )[0]
    g = struct.unpack( "L", buffer[ 0x04:0x04+4 ] )[0]
    i = struct.unpack( "L", buffer[ 0x08:0x08+4 ] )[0]    
    self.TGI = { 't':t ,'g':g,'i':i }
    #print 'reading ', hex( self.TGI['t'] ), hex( self.TGI['g'] ), hex( self.TGI['i'] ), self.filesize, hex( self.fileLocation ), self.order
    
  #def __del__( self ):
  #  print 'entry deleted'
    
  def ReadFile( self, sc4, readWhole = True , decompress = False ):    
    self.rawContent = None
    if readWhole:
      sc4.seek( self.fileLocation )
      self.rawContent = sc4.read( self.filesize )
      if decompress:
        if len( self.rawContent ) >= 8:
              compress_sig = struct.unpack( "H", self.rawContent[ 0x04:0x04+2 ] )[0]    
              if compress_sig == COMPRESSED_SIG:
                self.compressed = True    
      if self.compressed:
        if decompress: print 'Compressed file'
        uncompress = QFS.decode( self.rawContent[4:] )
        self.content = uncompress
      else:
        if decompress: print 'Uncompressed file'
        self.content = self.rawContent
      
  
  def IsItThisTGI( self, tgi ):
    return tgi[0] == self.TGI['t'] and tgi[1] == self.TGI['g'] and tgi[2] == self.TGI['i']
    
  def GetDWORD( self, pos ):
    return struct.unpack( "I", self.content[ pos:pos+4 ] )[0]

  def GetFloat( self, pos ):
    return struct.unpack( "f", self.content[ pos:pos+4 ] )[0]
     
  def GetString( self, pos, length ):
    return self.content[ pos:pos+length ]
      
def convheightmap( xS, yS, h ):
  r = ""
  for y in xrange( yS ):
    for x in xrange( xS ):
      r += struct.pack( "f", h[y,x] )
  return r

class SaveFile( object ):      
  def __init__( self, fileName ):
    self.fileName = fileName
    self.sc4 = open( self.fileName,"rb" )
    self.ReadHeader()
    self.ReadEntries()      

  def ReadHeader( self ):    
    self.header = self.sc4.read( 96 )
    self.header = self.header[0:0x30]+'\0'*12+self.header[0x30+12:96]
    header = self.header
    self.indexRecordEntryCount = struct.unpack( "l", header[ 0x24 : 0x28 ] )[0] 
    self.indexRecordPosition = struct.unpack( "l", header[ 0x28 : 0x28+4 ] )[0] 
    self.indexRecordLength = struct.unpack( "l", header[ 0x2C : 0x2C+4 ] ) [0]
    self.holeRecordEntryCount = struct.unpack( "l", header[ 0x30 : 0x30+4 ] )[0] 
    self.holeRecordPosition = struct.unpack( "l", header[ 0x34 : 0x34+4 ] )[0] 
    self.holeRecordLength = struct.unpack( "l", header[ 0x38 : 0x38+4 ] )[0] 
    
    self.dateCreated = struct.unpack( "I", header[ 0x18 : 0x18+4 ] )[0] 
    self.dateUpdated = struct.unpack( "I", header[ 0x1C : 0x1C+4 ] )[0] 
    
    self.fileVersionMajor = struct.unpack( "l", header[ 0x04 : 0x04+4 ] )[0]
    self.fileVersionMinor = struct.unpack( "l", header[ 0x08 : 0x08+4 ] )[0] 
    
    self.indexRecordType = struct.unpack( "l", header[ 0x20 : 0x20+4 ] )[0] 
    header = None
    self.regionView = None
    
  def ReadEntries( self ):
    self.entries = []
    self.sc4.seek( self.indexRecordPosition )    
    header = self.sc4.read( self.indexRecordLength )
    for idx in xrange( self.indexRecordEntryCount ):      
      entry = SC4Entry( header[ idx*20: idx*20+20], idx )
      if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ) or entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
        entry.ReadFile( self.sc4, True, True )
      else:
        entry.ReadFile( self.sc4 )
      self.entries.append( entry )
    self.sc4.close();

  def Save( self, cityXPos, cityYPos, heightMap, saveName ):
    global generic_saveValue
    time.sleep(.1)
    self.heightMap = heightMap
    xSize = self.heightMap.shape[0]
    ySize = self.heightMap.shape[1]
    newData = QFS.encode( struct.pack( 'H', 0x2 ) + convheightmap( xSize, ySize, self.heightMap ) )
    newData = struct.pack( "l", len( newData ) ) + newData 
    self.indexRecordPosition = 96
    self.dateUpdated = int( time.time() )+generic_saveValue*65535
    
    generic_saveValue += 1
    self.header = self.header[0:0x1C]+struct.pack( "I", self.dateUpdated )+self.header[0x1C+4:0x28]+struct.pack( "l", self.indexRecordPosition )+self.header[0x28+4:96]
    self.sc4 = open( self.fileName,"rb" )   
    for entry in self.entries:
      if entry.rawContent == None:
        entry.ReadFile( self.sc4, True )     
    self.sc4.close()       
    while 1:
        try:
            self.sc4 = open( saveName,"wb" )
            break
        except IOError:        
          dlg = wx.MessageDialog( None, "file %s seems to be ReadOnly\nDo you want to skip?(Yes)\nOr retry ?(No)"%(saveName),"Warning",wx.YES_NO|wx.ICON_QUESTION)
          result = dlg.ShowModal()
          dlg.Destroy()
          if result == wx.ID_YES:
            return False
    
    self.sc4.write( self.header )
    self.sc4.truncate( self.indexRecordPosition )
    self.sc4.seek( self.indexRecordPosition )
    
    pos = self.indexRecordPosition + self.indexRecordLength
    for entry in self.entries:
      entry.fileLocation = pos
      newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "l", entry.fileLocation ) + entry.buffer[ 0x0C+4: ]
      
      if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ):
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "l", entry.fileLocation ) + struct.pack( "l", len( newData ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = newData
        entry.compressed = 1
        entry.filesize = len( newData )
        
      if entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
        v = self.dateUpdated
        entry.content = entry.content[ 0 : 0x04 ] + struct.pack( "I", cityXPos ) + struct.pack( "I", cityYPos ) + entry.content[ 0x0C:39 ] + struct.pack( "I", v ) + entry.content[ 39+4: ]
        newDataCity  = entry.rawContent[:]
        newDataCity  = QFS.encode( entry.content )
        newDataCity  = struct.pack( "l", len( newDataCity ) ) + newDataCity 
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "l", entry.fileLocation ) + struct.pack( "l", len( newDataCity ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = newDataCity
        entry.compressed = 1
        entry.filesize = len( newDataCity )

      if entry.IsItThisTGI( (0x8a2482b9,0x4a2482bb,0x00000000) ):
        n = os.path.splitext( saveName )[0]
        print 'updating region view '+n+'.PNG for savegame ',saveName
        png = open( n+".PNG","rb" )
        pngData = png.read()
        png.close()
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( pngData ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = pngData
        entry.compressed = 0
        entry.filesize = len( pngData )

      if entry.IsItThisTGI( (0x8a2482b9,0x4a2482bb,0x00000002) ):
        n = os.path.splitext( saveName )[0]
        print 'updating region view overlay '+n+'_alpha.PNG for savegame ',saveName
        png = open( n+"_alpha.PNG","rb" )
        
        pngData = png.read()
        png.close()
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( pngData ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = pngData
        entry.compressed = 0
        entry.filesize = len( pngData )
        
      self.sc4.write( newbuffer)
      pos += entry.filesize
                    
    for entry in self.entries:
      self.sc4.write( entry.rawContent )
      if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ) or entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
        pass
      else:
        entry.rawContent = None
    self.sc4.close()
    return True
    
              
class SC4File( object ):
  def __init__( self, fileName ):
    self.fileName = fileName
    self.sc4 = open( self.fileName,"rb" )
    self.haveTree = False
    self.mayorMod = False
    self.protected = False
    

  def AtPos( self, x,y ):
    return x == self.cityXPos and y == self.cityYPos

  def Protected( self, b ):
    self.protected = b
    
  def IsProtected( self ):
    return self.protected 
  def HaveTrees( self ):
    return self.haveTree

  def InMayorMod( self ):
    return self.mayorMod
    
  def ReadHeader( self ):    
    self.header = self.sc4.read( 96 )
    self.header = self.header[0:0x30]+'\0'*12+self.header[0x30+12:96]
    header = self.header
    self.indexRecordEntryCount = struct.unpack( "I", header[ 0x24 : 0x28 ] )[0] 
    self.indexRecordPosition = struct.unpack( "I", header[ 0x28 : 0x28+4 ] )[0] 
    self.indexRecordLength = struct.unpack( "I", header[ 0x2C : 0x2C+4 ] ) [0]
    self.holeRecordEntryCount = struct.unpack( "I", header[ 0x30 : 0x30+4 ] )[0] 
    self.holeRecordPosition = struct.unpack( "I", header[ 0x34 : 0x34+4 ] )[0] 
    self.holeRecordLength = struct.unpack( "I", header[ 0x38 : 0x38+4 ] )[0] 
    
    self.dateCreated = struct.unpack( "I", header[ 0x18 : 0x18+4 ] )[0] 
    self.dateUpdated = struct.unpack( "I", header[ 0x1C : 0x1C+4 ] )[0] 
    
    self.fileVersionMajor = struct.unpack( "I", header[ 0x04 : 0x04+4 ] )[0]
    self.fileVersionMinor = struct.unpack( "I", header[ 0x08 : 0x08+4 ] )[0] 
    
    self.indexRecordType = struct.unpack( "I", header[ 0x20 : 0x20+4 ] )[0] 
    header = None
    print self.fileName, self.indexRecordPosition, self.holeRecordEntryCount, self.holeRecordPosition, self.holeRecordLength

    
  def ReadEntries( self ):
    self.entries = []
    self.sc4.seek( self.indexRecordPosition )    
    header = self.sc4.read( self.indexRecordLength )
    for idx in xrange( self.indexRecordEntryCount ):      
      entry = SC4Entry( header[ idx*20: idx*20+20], idx )
      if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ) or entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
        entry.ReadFile( self.sc4, True, True )
      else:
        entry.ReadFile( self.sc4)
      
      self.entries.append( entry )
      if entry.IsItThisTGI( (0xA9c05c85,0x299b2d1b,0x00000000) ):
        print 'Trees in the city --------'
        self.haveTree = True 
        self.protected = True
      if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ):
        print 'This was the terrain'
        self.heightMapEntry = entry
      if entry.IsItThisTGI( (0xCA027EDB, 0xCA027EE1, 0x00000000) ):
        print 'This was the city info', entry.compressed
        print 'version ',hex(entry.GetDWORD( 0x00 ))
        version = entry.GetDWORD( 0x00 )
        self.cityXPos = entry.GetDWORD( 0x04 )
        self.cityYPos = entry.GetDWORD( 0x08 )
        self.cityXSize = entry.GetDWORD( 0x0C )
        self.cityYSize = entry.GetDWORD( 0x10 )
        
        print 'city tile X = ', self.cityXPos 
        print 'city tile Y = ', self.cityYPos 
        print 'city size X = ', self.cityXSize
        print 'city size Y = ', self.cityYSize
        offsetLen = 64
        if version == 0xD0001:
          offsetLen = 64
        if version == 0xA0001:
          offsetLen = 63
        if version == 0x90001:
          offsetLen = 59
      
        self.mayorMod = struct.unpack( "B", entry.content[ offsetLen-1 ] )[0]
        if self.mayorMod :
          self.protected = True
        sizeName = entry.GetDWORD( offsetLen )
        print 'name city length', sizeName
        if( sizeName < 100 ):
          self.cityName = entry.GetString( offsetLen + 4, sizeName )
          print self.cityName
        else:
          print 'xxxxxxxxxxxxxxxxxxxxoldv', version
          self.cityName = "weird name"
        
    print 'finished reading the sc4' 
    print '--'*20       
    self.ySize = self.cityYSize * 64 +1                
    self.xSize = self.cityXSize * 64 +1
    self.xPos = self.cityXPos * 64
    self.yPos = self.cityYPos * 64
    self.heightMap = Numeric.zeros( (self.ySize, self.xSize), Numeric.Float32 )
    for y in xrange( self.ySize ):
      for x in xrange( self.xSize ):
        self.heightMap[ y,x ] = self.heightMapEntry.GetFloat( 2 + (x + y * self.xSize)*4 )
    #print self.heightMap        
    self.im = Image.fromstring( "F", ( self.xSize,self.ySize ), self.heightMap.tostring() )
    #self.im.show()
    header = None
    self.sc4.close()
    
  def Save( self, folder, color,waterLevel ):
    global generic_saveValue
    time.sleep(.1)
    if self.IsProtected():
      return True
    #self.haveTree = False
    #self.mayorMod = False
    togod = False
    removeTree = False
    if self.mayorMod:
      dlg = wx.MessageDialog( None, "City %s is in mayor mode\nRevert to god mode, removing trees and buildings ?(Yes)\nSave the changes anyway,leaving buildings and trees ?(No)\nDon't save ?(Cancel)"%(self.cityName),"Warning",wx.CANCEL|wx.YES_NO|wx.ICON_QUESTION)
      result = dlg.ShowModal()
      dlg.Destroy()
      if result == wx.ID_CANCEL:
        return
      if result == wx.ID_YES:
        togod = True
        removeTree = True
    elif self.haveTree:
      dlg = wx.MessageDialog( None, "City %s has trees in it\nRevert to blank, removing trees ? (Yes)\nSave the changes anyway,leaving trees ?(No)\nDon't save (Cancel)"%(self.cityName),"Warning",wx.CANCEL|wx.YES_NO|wx.ICON_QUESTION)
      result = dlg.ShowModal()
      dlg.Destroy()
      if result == wx.ID_CANCEL:
        return
      if result == wx.ID_YES:
        removeTree = True

    if togod or removeTree:
      mainPath = sys.path[0]
      os.chdir(mainPath)    
      if self.cityXSize == 1:
        name = 'datas/City - Small.sc4'
      if self.cityXSize == 2:
        name = 'datas/City - Medium.sc4'
      if self.cityXSize == 4:
        name = 'datas/City - Large.sc4'
        
      self.BuildThumbnail( color,waterLevel )              
      saved = SaveFile( name )
      fileName = self.fileName
      print 'will replace',self.fileName,'with a new blank city'
      
      ret = saved.Save( self.cityXPos, self.cityYPos, self.heightMap, fileName )
      if ret:
        self.mayorMod = False
        self.haveTree = False
        self.entries = saved.entries
        for entry in self.entries:
          if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ):          
            self.heightMapEntry = entry
      return ret
    self.BuildThumbnail( color,waterLevel )      

#8a2482b9 4a2482bb 0
#8a2482b9 4a2482bb 2

    if self.heightMapEntry.compressed:
        print 'Height map will be stored compressed'
        newData = QFS.encode( struct.pack( 'H', 0x2 ) + convheightmap( self.xSize, self.ySize, self.heightMap ) )
        newData = struct.pack( "I", len( newData ) ) + newData 
    else:
        print 'Height map will be stored uncompressed'
        newData = struct.pack( 'H', 0x2 ) + convheightmap( self.xSize, self.ySize, self.heightMap )
    self.indexRecordPosition = 96
    self.dateUpdated = int( time.time() )+generic_saveValue*65535    
    generic_saveValue += 1
    
    self.header = self.header[0:0x1C]+struct.pack( "I", self.dateUpdated )+self.header[0x1C+4:0x28]+struct.pack( "I", self.indexRecordPosition )+self.header[0x28+4:96]
    #self.header = self.header[0:0x28]+struct.pack( "l", self.indexRecordPosition )+self.header[0x28+4:96]
    self.sc4 = open( self.fileName,"rb" )
    for entry in self.entries:
      if entry.rawContent == None:
        entry.ReadFile( self.sc4, True )     
    self.sc4.close()       
    while 1:
        try:
            self.sc4 = open( self.fileName,"wb" )
            break
        except IOError:        
          dlg = wx.MessageDialog( None, "file %s seems to be ReadOnly\nDo you want to skip?(Yes)\nOr retry ?(No)"%(self.cityName),"Warning",wx.YES_NO|wx.ICON_QUESTION)
          result = dlg.ShowModal()
          dlg.Destroy()
          if result == wx.ID_YES:
            return False
                        
                    
    self.sc4.write( self.header )
    self.sc4.truncate( self.indexRecordPosition )
    self.sc4.seek( self.indexRecordPosition )

    
    pos = self.indexRecordPosition + self.indexRecordLength
    for entry in self.entries:
      entry.fileLocation = pos
      newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + entry.buffer[ 0x0C+4: ]
      
      if entry.IsItThisTGI( (0xA9DD6FF4,0xE98F9525,0x00000001) ):
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( newData ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = newData
        entry.compressed = self.heightMapEntry.compressed
        entry.filesize = len( newData )

      if entry.IsItThisTGI( (0x8a2482b9,0x4a2482bb,0x00000000) ):
        n = os.path.splitext( self.fileName )[0]
        print 'updating region view '+n+'.PNG for savegame ',self.fileName
        png = open( n+".PNG","rb" )
        pngData = png.read()
        png.close()
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( pngData ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = pngData
        entry.compressed = 0
        entry.filesize = len( pngData )

      if entry.IsItThisTGI( (0x8a2482b9,0x4a2482bb,0x00000002) ):
        n = os.path.splitext( self.fileName )[0]
        print 'updating region view overlay '+n+'_alpha.PNG for savegame ',self.fileName
        png = open( n+"_alpha.PNG","rb" )
        
        pngData = png.read()
        png.close()
        newbuffer = entry.buffer[ 0 : 0x0C ] + struct.pack( "I", entry.fileLocation ) + struct.pack( "I", len( pngData ) )+ entry.buffer[ 0x10+4: ]
        entry.rawContent = pngData
        entry.compressed = 0
        entry.filesize = len( pngData )
        
      self.sc4.write( newbuffer)
      pos += entry.filesize
                    
    for entry in self.entries:
      self.sc4.write( entry.rawContent )
    self.sc4.close()
    return True
    #self.sc4 = open( self.fileName,"rb" )
    
  def BuildThumbnail(self,colors,waterLevel):
    n = os.path.splitext( self.fileName )[0]
    minx,miny,maxx,maxy,r = tools3D.generateImage( waterLevel,self.heightMap.shape, self.heightMap.tostring(), colors.tostring() )
    maxx += 2
    offset = len(r)/2
    im = Image.fromstring( "RGB", ( 514,428 ), r[:offset]) 
    print minx,miny,maxx,maxy
    im = im.crop( [minx,miny,maxx,maxy] )
    
    im.save( n+".PNG" )
    im = Image.fromstring( "RGB", ( 514,428 ), r[offset:]) 
    im = im.crop( [minx,miny,maxx,maxy] )
    im.save( n+"_alpha.PNG" )
    return

class CityProxy( object ):
  def __init__( self, waterLevel, xPos, yPos, xSize, ySize ):
    self.cityXPos = xPos
    self.cityYPos = yPos
    self.cityXSize = xSize
    self.cityYSize = ySize
    self.haveTree = False
    self.mayorMod = False
    self.protected = False
    self.cityName = 'Not created yet'

    self.ySize = self.cityYSize * 64 +1                
    self.xSize = self.cityXSize * 64 +1
    self.xPos = self.cityXPos * 64
    self.yPos = self.cityYPos * 64
    self.heightMap = Numeric.zeros( (self.ySize, self.xSize), Numeric.Float32 )
    self.heightMap += Numeric.array(waterLevel+30).astype(Numeric.Float32)
    self.im = Image.fromstring( "F", ( self.xSize,self.ySize ), self.heightMap.tostring() )
    self.fileName = None

  def AtPos( self, x,y ):
    return x == self.cityXPos and y == self.cityYPos
    
  def Protected( self, b ):
    pass

  def IsProtected( self ):
    return False
    
  def HaveTrees( self ):
    return False

  def InMayorMod( self ):
    return False
    
  def Save( self, folder,color,waterLevel ):
    mainPath = sys.path[0]
    os.chdir(mainPath)    
    if self.cityXSize == 1:
      name = 'datas/City - Small.sc4'
    if self.cityXSize == 2:
      name = 'datas/City - Medium.sc4'
    if self.cityXSize == 4:
      name = 'datas/City - Large.sc4'
      
    saved = SaveFile( name )
    self.fileName = folder+"/"+"City - New city(%03d-%03d).sc4"%( self.cityXPos, self.cityYPos )
    self.BuildThumbnail( color ,waterLevel)      
    return saved.Save( self.cityXPos, self.cityYPos, self.heightMap, self.fileName )

  def BuildThumbnail(self,colors,waterLevel):
    n = os.path.splitext( self.fileName )[0]
    minx,miny,maxx,maxy,r = tools3D.generateImage( waterLevel,self.heightMap.shape, self.heightMap.tostring(), colors.tostring() )
    maxx += 2
    offset = len(r)/2
    im = Image.fromstring( "RGB", ( 514,428 ), r[:offset]) 
    print minx,miny,maxx,maxy
    im = im.crop( [minx,miny,maxx,maxy] )
    
    im.save( n+".PNG" )
    im = Image.fromstring( "RGB", ( 514,428 ), r[offset:]) 
    im = im.crop( [minx,miny,maxx,maxy] )
    im.save( n+"_alpha.PNG" )
    im.save( n+"_alpha.PNG" )
    return
    
def WorkTheconfig( config, waterLevel ):
    verified = Numeric.zeros( config.size, Numeric.Int8 )
    
    def Redish( value ):
        (r,g,b) = value
        if r > g and r > b and r > 250 :
            return True
        return False
    def Greenish( value ):
        (r,g,b) = value
        if g > r and g > b and g > 250:
            return True
        return False
    def Blueish( value ):
        (r,g,b) = value
        if b > r and b > g  and b > 250:
            return True
        return False
    def VerifyMedium( x,y ):
        rgbs = (config.getpixel( (x+1, y) ), config.getpixel( (x, y+1)), config.getpixel( (x+1, y+1) ) )
        for rgb in rgbs:
          if not Greenish( rgb ):
            assert 0
        verified[ x,y ]=1
        verified[ x+1,y ]=1
        verified[ x,y+1 ]=1
        verified[ x+1,y+1 ]=1
    def VerifyLarge( x,y ):
        rgbs = (
         config.getpixel( (x+1, y) ),config.getpixel( (x+2, y) ),config.getpixel( (x+3, y) ),
         config.getpixel( (x, y+1) ),config.getpixel( (x+1, y+1) ),config.getpixel( (x+2, y+1) ),config.getpixel( (x+3, y+1) ),
         config.getpixel( (x, y+2) ),config.getpixel( (x+1, y+2) ),config.getpixel( (x+2, y+2) ),config.getpixel( (x+3, y+2) ),
         config.getpixel( (x, y+3) ),config.getpixel( (x+1, y+3) ),config.getpixel( (x+2, y+3) ),config.getpixel( (x+3, y+3) )
         )
        for rgb in rgbs:
          if not Blueish( rgb ):
            assert 0
        for j in xrange(4):
            for i in xrange(4):
                verified[ x+i,y+j ]=1
    big = 0
    bigs = []
    small = 0
    medium = 0
    smalls = []
    mediums = []
    
    for y in xrange( config.size[1] ):
        for x in xrange( config.size[0] ):
            if verified[ x,y ] == 0:
                rgb = config.getpixel( (x,y) )
                if Blueish( rgb ):    
                  try:                
                    VerifyLarge( x,y )
                    bigs.append( (x,y) )                    
                    big += 1
                  except IndexError:
                    print x,y, "not blue"
                    raise
                  except AssertionError:
                    print x,y, "not blue"
                    raise
                    
                if Redish( rgb ):
                    smalls.append( (x,y ) )
                    small += 1
                if Greenish( rgb ):
                  try:                
                    VerifyMedium( x,y )
                    mediums.append( (x,y) )
                    medium += 1
                  except IndexError:
                    print x,y, "not green"
                    raise
                  except AssertionError:
                    print x,y, "not green"
                    raise
    print "big cities = ", big
    print "medium cities = ", medium
    print "small cities = ", small

        
    out = Image.new( config.mode, config.size )
    draw = ImageDraw.Draw(out)
    for c in smalls:
        reds = ( "#FF7777", "#FF0000" )
        color = c[0]+c[1]      
        draw.rectangle( [ c, (c[0],c[1])], fill=reds[color%2] )
    for c in mediums:
        colors = ( "#00FF00","#99FF00","#00FF99","#55FF55" )
        color = c[0]+c[1]      
        draw.rectangle( [ c, (c[0]+1,c[1]+1)], fill=colors[color%4] )
    for c in bigs:
        colors = ( "#0000FF","#0099FF","#0011FF","#0088FF","#0022FF","#0077FF","#0033FF","#0066FF",
        "#9900FF","#1100FF","#8800FF","#2200FF","#7700FF","#3300FF","#6600FF","#4400FF", )
        color = c[0]+c[1]      
        draw.rectangle( [ c, (c[0]+3,c[1]+3)], fill=colors[color%16] )
#    out.show()
#    config.show()
    cities = [ CityProxy( waterLevel, c[0],c[1], 1,1 ) for c in smalls ] + [ CityProxy( waterLevel, c[0],c[1], 2,2 ) for c in mediums ] + [ CityProxy( waterLevel, c[0],c[1], 4,4 ) for c in bigs ]
    return cities, out

class SC4Region( object ):
  def __init__( self, folder, waterLevel, dlg ):
    self.folder = folder
    GradientReader.Init('datas/basicColors.ini')
    self.waterLevel = waterLevel
    allfiles = dircache.listdir( folder )
    allCityFileNames = [ x for x in allfiles if os.path.splitext( x )[1] == ".sc4" ]    
    self.allCities = [] 
    try:
      self.config = Image.open( folder+"/config.bmp" )
    except:      
      self.config = None
    
    if self.config:
      self.config = self.config.convert( 'RGB' )
      #try:
      self.allCities,self.config = WorkTheconfig( self.config, waterLevel )
      #except:
      #  self.config = None
      #  dlg1 = wx.MessageDialog( None, 'It seems that your config.bmp is not valid or malformed\nIf it works in SC4 please send a PM to wouanagaine including th offending config.bmp','error', wx.OK | wx.ICON_ERROR )
      #  dlg1.ShowModal()
      #  dlg1.Destroy()
      #  self.allCities = None
      #  return
      #self.configColor = self.config.resize( (self.config.size[0]*64+1,self.config.size[1]*64+1 ) )
      #self.configColor = Numeric.fromstring( self.configColor, Numeric.Int8 )
      #self.configColor = Numeric.reshape( self.configColor , (self.config.size[1]*64+1,self.config.size[0]*64+1,3 ) )
      print 'CONFIG size', self.config.size
    
    for save in allCityFileNames:
      if dlg is not None: dlg.Update( 1, "Please wait while loading the region"+"\nReading "+save )
      sc4 = SC4File( os.path.join( folder, save ) )
      sc4.ReadHeader()
      sc4.ReadEntries()      
      for i,city in enumerate( self.allCities ):
        if city.AtPos( sc4.cityXPos, sc4.cityYPos ):
          if city.__class__ == CityProxy and city.cityXPos == sc4.cityXPos and city.cityYPos == sc4.cityYPos and city.cityXSize == sc4.cityXSize and city.cityYSize == sc4.cityYSize:
              self.allCities = self.allCities[:i]+self.allCities[i+1:]
          else:            
            dlg1 = wx.MessageDialog( None, 'It seems that the config.bmp does not match the savegames present in the region folder','error', wx.OK | wx.ICON_ERROR )
            dlg1.ShowModal()
            dlg1.Destroy()
            self.allCities = None
            return
          
      self.allCities.append( sc4 )
    if self.config == None:
      sizeX = 0
      sizeY = 0
      bigs = []
      smalls = []
      mediums = []
      for city in ( self.allCities ):
        if city.cityXSize == 4:
          bigs.append( (city.cityXPos,city.cityYPos ) )
        if city.cityXSize == 2:
          mediums.append( (city.cityXPos,city.cityYPos ) )
        if city.cityXSize == 1:
          smalls.append( (city.cityXPos,city.cityYPos ) )
        if city.cityXPos + city.cityXSize > sizeX:
          sizeX = city.cityXPos + city.cityXSize
        if city.cityYPos + city.cityYSize > sizeY:
          sizeY = city.cityYPos + city.cityYSize
        
      config = Image.new( "RGB", (sizeX,sizeY) )
      draw = ImageDraw.Draw(config)
      for c in smalls:
          reds = ( "#FF7777", "#FF0000" )
          color = c[0]+c[1]      
          draw.rectangle( [ c, (c[0],c[1])], fill=reds[color%2] )
      for c in mediums:
          colors = ( "#00FF00","#99FF00","#00FF99","#55FF55" )
          color = c[0]+c[1]      
          draw.rectangle( [ c, (c[0]+1,c[1]+1)], fill=colors[color%4] )
      for c in bigs:
          colors = ( "#0000FF","#0099FF","#0011FF","#0088FF","#0022FF","#0077FF","#0033FF","#0066FF",
          "#9900FF","#1100FF","#8800FF","#2200FF","#7700FF","#3300FF","#6600FF","#4400FF", )
          color = c[0]+c[1]      
          draw.rectangle( [ c, (c[0]+3,c[1]+3)], fill=colors[color%16] )
          
      self.config = config
      
    if dlg is not None: dlg.Update( 1, "Please wait while loading the region" )
    
    
  def IsValid( self ):
    return len( self.allCities ) > 0 or self.config != None
    
  def Save( self, dlg ):
    print "saving"
    im = Image.fromstring( "F", (self.height.shape[1],self.height.shape[0]), self.height.tostring() )
    saved = True
    for i,city in enumerate( self.allCities ):      
      dlg.Update( i, "Please wait while saving the region"+"\nsaving "+city.cityName )
      if city.IsProtected():
        continue  
      city.im = im.crop( ( city.cityXPos*64,city.cityYPos*64, city.cityXPos*64+city.xSize, city.cityYPos*64+city.ySize))
      hbuilt = city.im.tostring()
      if hbuilt != city.heightMap.tostring():
          print 'not skipping city',city.cityName
          backup = city.heightMap.tostring()
          city.heightMap = Numeric.fromstring( city.im.tostring(), Numeric.Float32 )
          city.heightMap = Numeric.reshape( city.heightMap, (city.xSize,city.ySize) )
          city.im = None
          x1=city.xPos
          y1=city.yPos
          x2 = x1 + city.xSize
          y2 = y1 + city.ySize
          
          #print self.colors
          print x1,y1,x2,y2
          print self.colors.shape
          c = self.colors[ y1:y2,x1:x2,:]
          if not city.Save( self.folder,c,self.waterLevel ):
            city.heightMap = Numeric.fromstring( backup, Numeric.Float32 )
            city.heightMap = Numeric.reshape( city.heightMap, (city.xSize,city.ySize) )
            saved = False
          else:
            backup = None
      else:
        print 'skipping city',city.cityName
    mini = min( self.height.flat )      
    return saved
      
  def show( self, dlg ):
    
    imgSize = [0,0]
    if self.config:
      imgSize[0] = self.config.size[0]
      imgSize[1] = self.config.size[1]
    for city in self.allCities:
      x = city.cityXPos + city.cityXSize
      y = city.cityYPos + city.cityYSize
      if imgSize[0] < x :
        imgSize[0] = x
      if imgSize[1] < y :
        imgSize[1] = y
              
    self.imgSize = [ a * 64 + 1 for a in imgSize ]              
    im = Image.new( "F", self.imgSize )
    for city in self.allCities:
      im.paste( city.im, ( city.cityXPos*64,city.cityYPos*64 ) )
      city.im = None
    dlg.Update( 2, "Please wait while loading the region\nBuilding textures" )
    #im.show()
    
    rawHeight = im.tostring()
    im =  None
    self.height = Numeric.fromstring( rawHeight, Numeric.Float32 )
    rawHeight = None
    self.height = Numeric.reshape( self.height,( self.imgSize[1],self.imgSize[0]) )
    
    #norms = ComputeNormal( self.height )    
    if dlg is not None : dlg.Update( 3,"Please wait while loading the region\nBuilding shadows" )
    #self.shadow = Numeric.ones( self.height.shape, Numeric.Int8 ) * Numeric.asarray( 255, Numeric.Int8 )#ComputeShadowMap( self.height, norms  )
    #shadow = ComputeShadowMap( False, self.height, None  )
    if dlg is not None : dlg.Update( 4,"Please wait while loading the region\nBuilding colors" )
    #self.colors = ComputeRGB( self.height, None, shadow, self.waterLevel )
    self.colors = ComputeOneRGB( False, self.height, self.waterLevel );
    if dlg is not None : dlg.Update( 5,"Please wait while loading the region\nok" )
    norms = None
    shadow = None
    print 'region read'
    
    return
    

  def RewriteLocked( self ):
    b = False
    for city in self.allCities:
      if city.IsProtected():
        x = city.yPos
        y = city.xPos
        x1 = x + city.xSize
        y1 = y + city.ySize
        print "Rewrite locked city ", city.cityName, "located at ", city.xPos, city.yPos, " size ", city.xSize, city.ySize, "will be rewrite at ", x,y, x1,y1, ' heithmap shape is ', self.height.shape, city.heightMap.shape
        print "code for region ",self.height.typecode()," code for city ",city.heightMap.typecode()
        #a = self.height[ x:x1,y:y1 ]# = city.heightMap
        #print a.shape, a.typecode()
        h = Numeric.zeros( (city.xSize, city.xSize), Numeric.Float32 )
        x = int( city.xPos )
        y = int( city.yPos )
        x1 = int(x) + int(city.xSize)
        y1 = int(y) + int(city.ySize)
        self.height[ y:y1,x:x1 ] = city.heightMap
        b = True
    return b        

if __name__ == '__main__':
    __name__ = 'Main'
    direc = """C:\Documents and Settings\stephane\Mes documents\SimCity 4\Regions\\Coastal"""
    class dlgstub:
        def __init__( self ):
            pass
        def Update( self, x, y ):
            pass
        
    region = SC4Region( direc, 250, dlgstub() )

