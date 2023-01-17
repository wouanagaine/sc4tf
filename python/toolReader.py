""" a quick function for reading the 'universal' tools definition """
import ConfigParser 

def ReadTools( fileName ):
    cp = ConfigParser.ConfigParser()
    cp.read( fileName )
    tools = cp.sections()
    availablesTools = {}
    for tool in tools:
        values = cp.items(tool)
        print values
        splineValues = []
        params = {}
        for v in values:
            if v[0] == 'perturbheight':
                print 'height',v[1]                
                params[ 'pertubHeight' ]= [ float(x) for x in v[1].split(',') ]
            elif v[0] == 'perturbradius':
                print 'radius', v[1]
                params[ 'pertubRadius' ]= [ float(x) for x in v[1].split(',') ]
            elif v[0] == 'scalefactor':
                print 'factor', v[1]
                params['factor'] = 1
            try:
                splineValues.append( (float(v[0]),float(v[1])) )
            except ValueError:
                pass
        splineValues.sort( key = lambda x:x[0] )
        params[ 'spline' ]=splineValues
        availablesTools[ tool ] = params
    return availablesTools
        
print ReadTools( "datas/tools.ini" )