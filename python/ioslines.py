import os
import os.path
import sys
import struct
import time
import math
import Numeric
import Image
import ImageFilter
import ImageDraw
import tools3D
import PngImagePlugin
import JpegImagePlugin
import BmpImagePlugin
Image._initialized=2

def expand( heights ):
  newheights = Numeric.zeros( heights.shape, Numeric.UnsignedInt8  )
  for y in xrange( heights.shape[0] ):
    for x in range(heights.shape[1]):
      if heights[ y,x ] != 0:
        newheights[y,x] =heights[ y,x ]
        for j in xrange( -1, 2 ):
          ly = y + j
          if ly < 0:
            continue
          if ly >= heights.shape[0]:
            break  
          for i in xrange( -1, 2 ):
            lx = x + i
            if lx < 0:
              continue
            if lx >= heights.shape[1]:
              break  
            if heights[ ly,lx ] == 0:
              newheights[ ly,lx ] = heights[ y,x ]
                          
  return newheights
  
def BuildDistanceMap( heights, value ):
  seeds = []
  done = Numeric.zeros( heights.shape, Numeric.UnsignedInt8  )
  distances = Numeric.ones( heights.shape, Numeric.Float )*Numeric.asarray( 1000000, Numeric.Float )
  for y in xrange( heights.shape[0] ):
    for x in range(heights.shape[1]):
      if heights[ y,x ] == value:
        seeds.append( (y,x,0.) )      
        distances[y,x]=0.
        done[y,x] = 1  

  def Valid( point ):
    if point[0] < 0:return False
    if point[0] >= heights.shape[0] :return False
    if point[1] < 0:return False
    if point[1] >= heights.shape[1] :return False
    if done[ point[0],point[1] ]==1: return False
    if heights[ point[0],point[1] ] != 0: return False
    return True
  
  const2sqr = math.sqrt( 2. )
  for p in seeds:    
    
    added = ( ( p[0],p[1]+1,p[2]+1. ),( p[0],p[1]-1,p[2]+1. ),( p[0]+1,p[1],p[2]+1. ),( p[0]-1,p[1],p[2]+1. ) ,
              ( p[0]+1,p[1]+1,p[2]+const2sqr ),( p[0]+1,p[1]-1,p[2]+const2sqr ),( p[0]+1,p[1]+1,p[2]+const2sqr ),( p[0]-1,p[1]-1,p[2]+const2sqr ) 
            )
    for v in added:
      if Valid( v ):
        done[ v[0],v[1] ] = 1
        distances[v[0],v[1]] = v[2]
        seeds.append( v )          
  return distances                    
  
def UseDistancesMap( distances, shape ):  
  heights = Numeric.zeros( shape, Numeric.Int8  )
  for y in xrange( shape[0] ):
    print 'line %d\r'%(y),
    for x in xrange(shape[1]):
      dists = [ (v,d[y,x]) for v,d in distances.iteritems() if d[y,x] < 100000 ]
      #continue
      #dists.sort( key = lambda x:x[1] )
      h = 0
      if len( dists ) == 0:
        #print dists, "error",x,y, [ (v,d[y,x]) for v,d in distances.iteritems()  ]
        pass
      elif len( dists ) == 1:
       h  = dists[0][0]
      else:        
        distanceTotal = reduce( lambda x,y : x+y, [ b[1] for b in dists ] )
        weights   = [ float(hi)*(max( 0, distanceTotal-d ) ) for hi,d in dists ]
        h = reduce( lambda x,y : x+y, weights )
        h /= distanceTotal
      heights[y,x] = int( h )
  return heights             
        
          
def convheightmap( xS, yS, h ):
  r = ""  
  for y in xrange( yS ):
    for x in xrange( xS ):
      r += struct.pack( "f", h[y,x] )
  return r
          
def main( ):
  im = Image.open( sys.argv[1] )
  im = im.convert( 'L' )
  heights = Numeric.reshape( Numeric.array( im.tostring(), Numeric.UnsignedInt8   ), (im.size[1], im.size[0] ) )
  heights = Numeric.reshape( Numeric.array( tools3D.expand( heights.shape, heights ), Numeric.UnsignedInt8   ), (im.size[1], im.size[0] ) )
  print 'image size :',heights.shape[1],'x',heights.shape[0]
  values = {}
  for x in Numeric.ravel( heights):
    values[int(x)] = 1
  values =values.keys()
  values.sort()
  values = [ v for v in values if v != 0 ]
  print 'isoclines founds : ',values
  distances = {}
  for val in values:
    print 'building distance map for',val
    r = tools3D.buildDistanceMap( heights.shape, heights, val )
    distances[ val ] = r
    #r = Numeric.fromstring( r, Numeric.Float32 )
    #distances[ val ] = Numeric.reshape( r, heights.shape )
    #i = Image.fromstring( "F", (heights.shape[1],heights.shape[0]), distances[val])#convheightmap( heights.shape[1],heights.shape[0], distances[ val ] ) )
    #i.show()
    print 'ok'
  print 'building greyscale'
  r = tools3D.useDistancesMap( distances, heights.shape )
  print 'ok'
  im = Image.fromstring( "L", (heights.shape[1],heights.shape[0]), r )
  im = im.filter(ImageFilter.BLUR)
  im.save( "temp.bmp" )      
  #im.save( "temp.jpg" )      
  im.show()
  
  return
  heights = UseDistancesMap( distances, heights.shape )
  im = Image.fromstring( "L", (heights.shape[1],heights.shape[0]), heights.tostring() )
  im = im.filter(ImageFilter.BLUR)
  im.save( "temp.bmp" )      
  im.save( "temp.jpg" )      
  im.show()
  
  #im.filter(ImageFilter.CONTOUR).show()
  #im.filter(ImageFilter.DETAIL).show()  
  #im.filter(ImageFilter.EMBOSS).show()
  

  return
  while 1:
    heights = Numeric.reshape( Numeric.array( tools3D.expand( heights.shape, heights ), Numeric.UnsignedInt8   ), (im.size[1], im.size[0] ) )
    im = Image.fromstring( "L", (heights.shape[1],heights.shape[0]), heights.tostring() )
    if min( heights.flat ) != 0:
      print min( heights.flat )
      break    
  im.show()
  
main()