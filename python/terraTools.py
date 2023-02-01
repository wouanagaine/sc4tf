import wx                  
import dxEngine
import datReader
import Numeric
import tools3D
import random
import math
import cmath
import Image
import os
import sys
import brushReader

# get the mask image 
os.chdir(sys.path[0])
g_mask = Image.open( "datas/mask.png" ).convert("L")


class TerraToolZone( object ):
  """ base class for zone terraforming tool 
      it stores the delta mouse from last frame and the height when clicking 
  """
  def __init__( self ):
    self.angle = 0
    self.dx = 0
    self.dy = 0
    pass

  def onStart( self, height ):
    self.initialHeight = height

    
  def mouseDelta( self, mx, my ):
    self.dx = mx
    self.dy = my
    if int(mx)==0 and int(my) == 0:
      return
    self.angle = self.angle*.2 + math.degrees( math.atan2( self.dx, self.dy ) )*.8
      
  def apply( self, bSquared, radius, strength, heights ):
    return heights
        
class Flatten (TerraToolZone ):
  """ flatten tool will flatten the area """
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Flatten"

        
  def apply( self, bSquared, radius, strength, heights ):
    strength = min( 1., strength )
    rawHeight = tools3D.flatten( bSquared,radius,strength,self.initialHeight,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret
    
    
class Roughen( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Roughen"
    pass
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.rough( bSquared,radius,strength,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret
    
class Smooth( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Smooth"
    pass
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.smooth( bSquared,radius,strength,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret

class MakeHill( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make hills"
    pass
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight =tools3D.hills( bSquared,radius,strength,heights.shape, heights.tostring() )
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret    
    

class MakeSteepHill( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make Steep hill"
    self.add = random.uniform( 0, math.pi )
    pass
    
  def onStart( self, height ):
    self.add = random.uniform( 0, math.pi )
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.smooth( bSquared, radius, strength, heights.shape, tools3D.mountainsOld( bSquared,radius,strength,self.add,heights.shape, heights.tostring() ) )   
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret    
    
class MakeMountainJason( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make Mountains Jplumbley method"
    self.add = random.uniform( 0, math.pi )
    pass
  def onStart( self, height ):
    self.add = random.uniform( 0, 2.*math.pi )

  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.mountainsNew( bSquared,radius,strength,self.add,heights.shape, heights.tostring() )
    
    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret    
  
class MakeMountainClassic( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make Mountains Classic"
    self.add = random.uniform( 0, math.pi )
    pass
    
  def onStart( self, height ):
    self.add = random.uniform( 0, math.pi )
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.smooth( bSquared, radius, strength, heights.shape, tools3D.mountainsClassic( bSquared,radius,strength,heights.shape, heights.tostring() ) )   
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret    


class MakeCanyon( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make Canyon"
    self.add = random.uniform( 0, math.pi )
    pass
  def onStart( self, height ):
    self.add = random.uniform( 0, 2.*math.pi )

  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.canyonBis( bSquared,radius,strength,heights.shape, heights.tostring() )
    
    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret    

class MakeNewValley( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make Valley ( New )"
    pass
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.newValley( bSquared,radius,strength,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret

class MakeValley( TerraToolZone ):
  def __init__( self ):
    TerraToolZone.__init__( self )
    self.name = "Make Valley"
    pass
    
  def apply( self, bSquared, radius, strength, heights ):
    rawHeight = tools3D.valley( bSquared,radius,strength,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret


    
class MakeHarbor( TerraToolZone ):
  def __init__( self, waterLevel ):
    TerraToolZone.__init__( self )
    self.name = "Make Harbor"
    self.waterLevel = waterLevel
    
  def apply( self, bSquared, radius, strength, heights ):       
    strength = min( 1., strength )
    
    rawHeight = tools3D.flatten( bSquared,radius,strength,self.waterLevel,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret

class DrawTool( TerraToolZone ):
  def __init__( self, level ):
    TerraToolZone.__init__( self )
    self.name = "Draw at height %.02fm"%(level)
    self.level = level
  def ChangeLevel( self, level ):
    self.name = "Draw at height %.02fm"%(level)
    self.level = level
    
  def apply( self, bSquared, radius, strength, heights ):       
    strength = min( 1., strength )
    rawHeight = tools3D.flatten( bSquared,radius,strength,self.level,heights.shape, heights.tostring() )    
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret


class WeatherErodeNew( TerraToolZone ):
  def __init__( self):
    TerraToolZone.__init__( self )
    self.name = "Water erode enhanced"    

  def apply( self, bSquared, radius, strength, heights ):       
    mask = Numeric.zeros( heights.shape, Numeric.Float32 )
    for y in xrange( -radius, radius+1):
      for x in xrange( -radius, radius+1):
        dist = math.sqrt( x*x+y*y )
        if bSquared or dist < float(radius):
          mask[y+radius,x+radius] = 1.

    rawHeight = tools3D.waterErode( 8.0, .01, .04, 20., int(strength*2), int(strength/2), heights.shape, heights.tostring() )    
    rawHeight = tools3D.weatherErode( strength, 0.05*strength, 4, heights.shape, rawHeight )
    ret = Numeric.reshape( Numeric.fromstring( rawHeight, Numeric.Float32 ), heights.shape )
    ret -= heights
    ret *= mask
    rough = heights+ret
    return rough

class WeatherErode( TerraToolZone ):
  def __init__( self):
    TerraToolZone.__init__( self )
    self.name = "Water erode"    

  def apply( self, bSquared, radius, strength, heights ):       
    mask = Numeric.zeros( heights.shape, Numeric.Float32 )
    for y in xrange( -radius, radius+1):
      for x in xrange( -radius, radius+1):
        dist = math.sqrt( x*x+y*y )
        if bSquared or dist < float(radius):
          mask[y+radius,x+radius] = 1.

    rawHeight = tools3D.waterErode( 8.0, .01, .04, 1., int(strength*2), int(strength/2), heights.shape, heights.tostring() )    
    ret = Numeric.reshape( Numeric.fromstring( rawHeight, Numeric.Float32 ), heights.shape )
    ret -= heights
    ret *= mask
    rough = heights+ret
    return rough

class TalusErode( TerraToolZone ):
  def __init__( self):
    TerraToolZone.__init__( self )
    self.name = "Talus Erode"    

  def apply( self, bSquared, radius, strength, heights ):       
    mask = Numeric.zeros( heights.shape, Numeric.Float32 )
    for y in xrange( -radius, radius+1):
      for x in xrange( -radius, radius+1):
        dist = math.sqrt( x*x+y*y )
        if bSquared or dist < float(radius):
          mask[y+radius,x+radius] = 1.

    rawHeight = tools3D.weatherErode( 10, 0.05*strength, 20, heights.shape, heights.tostring() )
    ret = Numeric.reshape( Numeric.fromstring( rawHeight, Numeric.Float32 ), heights.shape )
    ret -= heights
    ret *= mask
    rough = heights+ret
    return rough
    
class RainErode( TerraToolZone ):
  def __init__( self):
    TerraToolZone.__init__( self )
    self.name = "Rain Erode"    
  
class UniversalTool( TerraToolZone ):
  """ a universal tool is based on a spline that rotate """
  def __init__( self, toolName, splineValues  ):
    TerraToolZone.__init__( self )
    self.name = "Universal tool "+toolName
    self.splineValues = splineValues
        
  def apply( self, bSquared, radius, strength, heights ):       
    rawHeight =tools3D.universal( bSquared,radius,strength,heights.shape, heights.tostring(), self.splineValues )
    ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
    ret = Numeric.reshape( ret, heights.shape )
    return ret    

class BrushTool( TerraToolZone ):
  """ brush tool is the best way to mimic SC4 ingame tool """ 
  def __init__( self, toolName ):
    TerraToolZone.__init__( self )
    self.name = toolName
    self.brush = brushReader.BrushDefinition.allBrushes[toolName]

  def apply( self, bSquared, radius, strength, heights ):    
    # the mask is here to get rid of artifact when rotating the brush layer image
    mask = g_mask.rotate( self.angle )
    mask = mask.resize( (radius*2+1,radius*2+1)  )
    mask = Numeric.fromstring( mask.tostring(), Numeric.Int8 )

    # we apply each layer in the defined order
    # we rotate each layer if it should follow mouse movement
    
    for layer in self.brush.layers:
        
        res = Numeric.zeros( heights.shape, Numeric.Float32 )
        if layer.alignWithMouseMovement :
            b = layer.texture.rotate( self.angle, Image.BICUBIC )
        else:            
            b = layer.texture.copy()
        if layer.scale != 1:
            origSize = b.size
            size = (int(b.size[0]*layer.scale), int(b.size[1]*layer.scale) )
            newIm = Image.new( b.mode, b.size, b.getpixel((0,0)) )
            b = b.resize( size, Image.BICUBIC  )
            delta = [ origSize[0] - size[0],origSize[1] - size[1] ]
            box = ( delta[0]/2, delta[1]/2 )
            newIm.paste( b, box )
            b = newIm
            
            if layer.alignWithMouseMovement :
              mask = g_mask.rotate( self.angle )
            else:
              mask = g_mask.copy()
            mask = mask.resize(  size )
            newMask = Image.new( "L", (radius*2+1,radius*2+1) )
            newMask.paste( mask, box )
            mask = newMask
            mask = Numeric.fromstring( mask.tostring(), Numeric.Int8 )
        else:
          if layer.alignWithMouseMovement :
            mask = g_mask.rotate( self.angle )
          else:
            mask = g_mask.copy()
          mask = mask.resize( (radius*2+1,radius*2+1)  )
          mask = Numeric.fromstring( mask.tostring(), Numeric.Int8 )
                    
        b = b.resize( (radius*2+1,radius*2+1) )
        b = Numeric.reshape( Numeric.fromstring( b.tostring(), Numeric.Int32 ), heights.shape )
        b -= Numeric.array( layer.offset ).astype(Numeric.Int32)    
        b = b.astype( Numeric.Float32 )
        b *= Numeric.array( layer.factor*strength).astype(Numeric.Float32)
    
        # based on the operation of the layer we mix the resulting image with the underlying terran    
        if layer.op == brushReader.ADDING:
          Numeric.putmask( res, mask, b )
          heights += res
        if layer.op == brushReader.FLATTEN:
          initialHeight = heights[ radius, radius ]
          b /= Numeric.array( 255 ).astype(Numeric.Float32)
          b = ( heights - Numeric.array( initialHeight ).astype(Numeric.Float32) ) * b
          Numeric.putmask( res, mask, b )
          heights -= res
        if layer.op == brushReader.SMOOTH:
          Numeric.putmask( res, mask, b )
          rawHeight = tools3D.egalize( heights.shape, heights.tostring() )
          smooth = Numeric.fromstring( rawHeight, Numeric.Float32 )
          smooth = Numeric.reshape( smooth, heights.shape )     
          res /= Numeric.array( 255 ).astype(Numeric.Float32)     
          heights += ( smooth - heights ) * res
          
    return heights 
    
    
def main():
  pass

try:
    if __name__ == '__main__':
        __name__ = 'Main'
    main()
except:
    pass
