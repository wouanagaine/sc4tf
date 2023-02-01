""" this is just a funny class to parse the user config file 
    basically map the ini file to a dictionnary 
"""    

import ConfigParser 


class Configurator( object ):
    def __init__( self ):        
        self.cp = ConfigParser.ConfigParser()
        self.cp.read( "config.ini" )
        if self.cp.has_section( "Overview" ):
            values = self.cp.items("Overview")
            self.overview = {}
            for v in values:
                self.overview[ v[0] ] = int(v[1] )
        else:
            self.overview = { "x":22,"y":22,"width":513,"height":513 }

        if self.cp.has_section( "MainWindow" ):
            values = self.cp.items("MainWindow")
            self.mainwindow = {}
            for v in values:
                self.mainwindow[ v[0] ] = int(v[1] )
        else:
            self.mainwindow = { "x":200,"y":0 }

        if self.cp.has_section( "Sliders" ):
            values = self.cp.items("Sliders")
            self.sliders = {}
            for v in values:
                self.sliders[ v[0] ] = int(v[1] )
        else:
            self.sliders = { "x":200,"y":674 }
            
        if self.overview['x'] > 1600 or self.overview['x'] < -500 :            
          self.overview = { "x":22,"y":22,"width":513,"height":513 }
        if self.mainwindow['x'] > 1600 or self.mainwindow['x'] < -500 :            
          self.mainwindow = { "x":200,"y":0 }
        if self.sliders['x'] > 1600 or self.sliders['x'] < -500 :            
          self.sliders = { "x":200,"y":0 }
                            

    def save( self ):
        if not self.cp.has_section( "Overview" ):
            self.cp.add_section( "Overview" )
        if not self.cp.has_section( "MainWindow" ):
            self.cp.add_section( "MainWindow" )
        if not self.cp.has_section( "Sliders" ):
            self.cp.add_section( "Sliders" )
        for k,v in self.overview.iteritems():
            self.cp.set( "Overview", k, str(v) )
        for k,v in self.mainwindow.iteritems():
            self.cp.set( "MainWindow", k, str(v) )
        for k,v in self.sliders.iteritems():
            self.cp.set( "Sliders", k, str(v) )
        f = open( "config.ini","wt" )
        self.cp.write( f )            
        f.close()
        
    def setOverview( self, x,y,w,h ):
        self.overview = { "x":x,"y":y,"width":w,"height":h }
                                
    def setMainwindow( self, x,y ):
        self.mainwindow = { "x":x,"y":y }

    def setSliders( self, x,y ):
        self.sliders = { "x":x,"y":y }
