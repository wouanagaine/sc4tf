""" 
  This file is for defining new brush tool
  
  A brush tool is composed of a name and a serie of layers 
  A layer is defined by a grayscale bitmap and some parameters such that SC4Terraformer will know how to apply the bitmap to the terrain
  
  BrushLayer( texture, alignWithMouseMovement, scale, offset, factor, op )
  texture is the file name of the grayscale image - must be enclosed in "
  alignWithMouseMovement is a boolean value ( True or False ) to tell SC4Terrafomer if the layer will be turn to follow the mouse movement
  scale is a real number in the range ( 1 - 0 )  that will affect how the bitmap is used in regard to the radius you use in SC4Terraformer
  offset is a number in the range( 0-255 ). if the graylevel in bitmap is less than this value, the terran will be decreased by the difference, if the graylevel is more than this value, the terran will be raised by the difference
  factor is a real number that will apply to the above difference ( see it as a multiplier to the strength you specify in SC4Terraformer )
  op is a way to apply the bitmap, 3 methods are defined, ADDING, SMOOTH, FLATTEN
    ADDING will add the difference
    SMOOTH will smooth the terran 
    FLATTEN will raise/lower the terran to the cursor level
    
  you can combine any number of layers in a brush, still the more layers you have the more slower it will be. 
  
  if you modify this file, and no brushes tools are available you have made an error ( verify the case of words, verify you put comma in the right place, verify you put " around the texture name
  if you modify this file, and the brush tool you add is not available you have made an error in parameters ( mainly the texture file can't be loaded - not a grayscale image, of does not exist )
  
  Take care!
"""



BrushDefinition( 
    "MoutainTool",
    [
     BrushLayer( texture='brushes/mount.png', alignWithMouseMovement=False, scale=1, offset=0, factor=.02 )
    ,BrushLayer( texture='brushes/submount2.png', alignWithMouseMovement=True, scale=.8, offset=0, factor=.01 )
    ]
)

BrushDefinition(
    "CraterTool", 
    [
        BrushLayer( texture='brushes/crater.png', alignWithMouseMovement=False, scale=1, offset=128, factor=.02 )
    ]
)

BrushDefinition(
    "ValleySteep", 
    [
        BrushLayer( texture='brushes/ValleySteep.png', alignWithMouseMovement=True, scale=1, offset=255, factor=.08 )
    ]
)

BrushDefinition(
    "MountainSteepHill", 
    [
        BrushLayer( texture='brushes/MountainSteepHill1.png', alignWithMouseMovement=True, scale=1, offset=0, factor=.02 )
    ]
)

BrushDefinition( 
    "Volcano",
    [
     BrushLayer( texture='brushes/Volcano1.png', alignWithMouseMovement=False, scale=1, offset=0, factor=.024 )
    ,BrushLayer( texture='brushes/crat.png', alignWithMouseMovement=False, scale=.35, offset=255, factor=.02 )
    ]
)

BrushDefinition(
    "Cliff", 
    [
        BrushLayer( texture='brushes/cliff.png', alignWithMouseMovement=True, scale=1, offset=128, factor=.02 )
    ]
)

BrushDefinition(
    "EarthQuake", 
    [
        BrushLayer( texture='brushes/eqFault.png', alignWithMouseMovement=True, scale=1, offset=128, factor=.02 )
    ]
)

BrushDefinition(
    "Mesa", 
    [
        BrushLayer( texture='brushes/Mesa.png', alignWithMouseMovement=True, scale=1, offset=0, factor=.02 )
        ,BrushLayer( texture='brushes/Mesa.png', alignWithMouseMovement=True, scale=1, offset=0, factor=.08, op=FLATTEN )
    ]
)

BrushDefinition(
    "Flatten", 
    [
        BrushLayer( texture='brushes/leveler.png', alignWithMouseMovement=False, scale=1, offset=0, factor=.2, op=FLATTEN )
    ]
)

BrushDefinition(
    "Canyon", 
    [
        BrushLayer( texture='brushes/canyon.png', alignWithMouseMovement=True, scale=1, offset=128, factor=.02 )
       ,BrushLayer( texture='brushes/valley.png', alignWithMouseMovement=True, scale=1, offset=0, factor=.002, op=SMOOTH )
    ]
)

BrushDefinition(
    "Plains", 
    [
        BrushLayer( texture='brushes/mesa2.png', alignWithMouseMovement=False, scale=1, offset=0, factor=.02, op=SMOOTH )
       ,BrushLayer( texture='brushes/mesa2.png', alignWithMouseMovement=False, scale=.9, offset=0, factor=.02, op=FLATTEN)
    ]
)

BrushDefinition(
    "Hills", 
    [
        BrushLayer( texture='brushes/hills1.png', alignWithMouseMovement=False, scale=1, offset=0, factor=.02  )
       ,BrushLayer( texture='brushes/crat.png', alignWithMouseMovement=False, scale=.9, offset=0, factor=.02, op=SMOOTH)
    ]
)

BrushDefinition(
    "RaiseZone", 
    [
        BrushLayer( texture='brushes/raise.png', alignWithMouseMovement=False, scale=2, offset=0, factor=.00390625  )       
    ]
)

BrushDefinition(
    "LowerZone", 
    [
        BrushLayer( texture='brushes/raise.png', alignWithMouseMovement=False, scale=2, offset=512, factor=.00390625  )       
    ]
)