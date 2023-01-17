import Image


FLATTEN = 5
SMOOTH = 2
ADDING = 0
class BrushLayer( object ):
    """ define a layer to be applied when using brush """    
    def __init__( self, texture, alignWithMouseMovement, scale, offset, factor, op=ADDING ):
        self.textureName = texture
        self.texture = Image.open( texture ).convert("I")
        self.alignWithMouseMovement = alignWithMouseMovement
        self.scale = scale
        self.offset = offset
        self.factor = factor
        self.op = op
        
    def __str__( self ):
        return self.textureName        
    def __repr__( self ):
        return self.textureName
        
class BrushDefinition( object ):
    """ define a brush, a brush is build upon one or multiple layer """
    allBrushes = {}
    def __init__( self, name, layers ):
        self.name = name
        self.layers = layers
        BrushDefinition.allBrushes[self.name] =self
        
    def __repr__( self ):
        return self.name + " ".join( [ str(x) for x in self.layers ] )

def initBrushesPlugins():        
    """ brushes are loaded at run time and defined in the file brushes.py """
    try:
        execfile( 'brushes.py', globals() )
    except:
        pass


                    
