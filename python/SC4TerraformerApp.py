import wx                  # This module uses the new wx namespace

import tools3D
try:
  version = tools3D.GetVersion()
  if version != "v1.0c":
    raise ValueError
except:
    class ErrApp( wx.App ):
        def OnInit( self ):
            dlg = wx.MessageDialog(None, "It seems that there is a conflicting dll\nPlease make sure to uninstall previous version\nAnd reinstall this one",
                                     'Error',
                                 wx.OK | wx.ICON_ERROR
                                 )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    app = ErrApp( False )
    app.MainLoop()
                
    exit()
    



import gc
gc.enable()
import sys
import os
import webbrowser
mainPath = sys.path[0]
os.chdir(mainPath)
try:
  webbrowser.open_new( "readme.html" )
except:
  print 'No readme.html found, I really hope you have read it !!!!!!!!!!!!!!!!!!!!!!!!!'

try:
    import dxEngine
except ImportError:
    class ErrApp( wx.App ):
        def OnInit( self ):
            dlg = wx.MessageDialog(None, "DirectX can't be loaded\nMaybe there is another application that use DirectX\nIf it is not the case check the readme.html for more informations",
                                     'Error',
                                 wx.OK | wx.ICON_ERROR
                                 )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    app = ErrApp( False )
    app.MainLoop()
                
    exit()
try:
  version = dxEngine.GetVersion()
  if version != "v1.0c":
    raise ValueError
except:
    class ErrApp( wx.App ):
        def OnInit( self ):
            dlg = wx.MessageDialog(None, "It seems that there is a conflicting dll\nPlease make sure to uninstall previous version\nAnd reinstall this one",
                                     'Error',
                                 wx.OK | wx.ICON_ERROR
                                 )
            dlg.ShowModal()
            dlg.Destroy()
            return False

    app = ErrApp( False )
    app.MainLoop()
                
    exit()
    
import datReader
import PIL.JpegImagePlugin
import Image
import ImageFilter
import ImageDraw
import Numeric
import thread
import terraTools
import time
import struct
import wx.lib.scrolledpanel as scrolled
import wx.lib.foldpanelbar as fpb
import DlgCities
import zlib
import os
import os.path
import math
import GradientReader
import toolReader
import brushReader
import QuestionDialog

from config import *
config = None
    
from about import MyAboutBox
from about import AuthorBox

import math

def ReadCLR():
  clrFile = open( "datas/RGB colourscheme.clr","rt" )
  lines = clrFile.readlines()
  clrFile.close()
  lines = lines[2:]
  oldHeight = 0.
  oldR = 0
  oldG = 0
  oldB = 0
  clr = {}
  grad = []
  for line in lines:
    try:
      v = line.split( ' ' )
      v = [ i for i in v if i != '' ]
      height = float( v[0] )+250.
      r = int( v[1] )
      g = int( v[2] )
      b = int( v[3] )
      delta = height-oldHeight
      deltaR = r - oldR
      deltaG = g - oldG
      deltaB = b - oldB
      if delta == .1:
        #grad.append( ( r,g,b ) )
        v =r*256*256 +g*256 + b
        clr[ v ] = height
      else:
        iDelta = int( delta * 10 )
        hCurrent = oldHeight
        rCurrent = oldR
        gCurrent = oldG
        bCurrent = oldB
        rstep = deltaR/iDelta
        gstep = deltaG/iDelta
        bstep = deltaB/iDelta
        for x in xrange( iDelta ):
          #grad.append( (rCurrent,gCurrent,bCurrent) )
          v =rCurrent*256*256 +gCurrent*256 + bCurrent
          clr[ v ] = hCurrent
          hCurrent += .1
          rCurrent += rstep
          gCurrent += gstep
          bCurrent += bstep
    except:
      print line
      raise
  return clr    
  
class RebuildColors:
  def __init__( self, region,frame ):
    self.region = region
    self.frame = frame
    
    
  def start(self):
    self.closed = False
    self.restart = False  
    self.pause = self.keepGoing =  True
    self.running = False
    self.colors = None
    
    thread.start_new_thread(self.run, (self.region,))
    
  def stop(self):
    self.keepGoing = False
    
  def Pause( self ):
    self.pause = True

  def Restart( self ):
    self.pause = False
    self.restart = True
    
  def isRunning(self):
    return self.running
  
  def isClosed( self ):
    return self.closed

  def run(self, region ):
    while self.keepGoing:
        while self.pause:
            time.sleep( .1 )
            if not self.keepGoing:
                break
        if not self.keepGoing:
            break
        h = region.height[:]
        gc.collect()
        #print "starting a color process"            
        self.running = True            
        self.colors = None
        self.restart = False
        if self.frame.bUseConfig:
          print "compute normal"            
          #norms = datReader.ComputeNormal( h )    
          print "compute shadow"            
          #shadow = datReader.ComputeShadowMap(False, h, None )
          print "compute colors"            
          #colors = Numeric.add( self.region.configColor,  )
          #colors = datReader.ComputeRGB( h, None, shadow, self.region.waterLevel )
          colors=datReader.ComputeOneRGB( False, h, self.region.waterLevel );
          #colors = region.colors
          s = (h.shape[0],h.shape[1],3)
          del h
          
          im = Image.fromstring( "RGB", (s[1],s[0]), colors.tostring() )
          draw = ImageDraw.Draw(im)
          #draw.rectangle( [0,0,s[1],s[0]],fill="#000000" )
          for y in xrange( s[0]/64 ):
            for x in xrange( s[1]/64 ):
                draw.rectangle( [x*64,y*64,x*64+64,y*64+64], outline ="#777777" )
          for city in region.allCities:
            x = city.xPos
            y = city.yPos
            x1 = x + city.xSize
            y1 = y + city.ySize
            draw.rectangle( [x,y,x1,y1], outline ="#FFFFFF" )
          #im = Image.blend( self.region.configColor, , .5 )
          rgb = Numeric.fromstring( im.tostring(), Numeric.Int8 )
          rgb = Numeric.reshape( rgb, s  )
          colors = rgb
        else:
          print "compute normal"            
          #norms = datReader.ComputeNormal( h )    
          print "compute shadow"            
          #shadow = datReader.ComputeShadowMap(self.frame.bComputeShadow, h, None )
          print "compute colors"            
          #colors= datReader.ComputeRGB( h, None, shadow, self.region.waterLevel )      
          colors=datReader.ComputeOneRGB(self.frame.bComputeShadow, h, self.region.waterLevel );
          del h
        #del norms         
        #del shadow
        
        print "ending a color process"            
        gc.collect()
        if not self.restart:
            self.restart = False
            self.colors = colors
            self.pause = True
            self.running = False
    print 'Thread stop'            
    self.closed = True

class OverViewCanvas( wx.ScrolledWindow):
    def __init__(self, parent, id = -1, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftButtonEvent)
        self.Bind(wx.EVT_LEFT_UP,   self.OnLeftButtonEvent)
        self.Bind(wx.EVT_MOTION,    self.OnLeftButtonEvent)
        self.bmp = None
        self.drag = False
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.DoPrepareDC(dc)
        if self.bmp is not None:
          dc.BeginDrawing()
          dc.DrawBitmap(self.bmp, 0, 0, True)            
          dc.EndDrawing()
    
    def Redraw( self ):
        dc = wx.ClientDC(self)
        self.DoPrepareDC(dc)
        if self.bmp is not None:
          dc.BeginDrawing()
          dc.DrawBitmap(self.bmp, 0, 0, True)            
          dc.EndDrawing()
      
    def OnLeftButtonEvent(self, event):
      if event.LeftDown():
        self.drag = True
      if event.LeftUp():
        self.drag = False
              
      if self.drag:
        xView, yView = self.GetViewStart()
        xDelta, yDelta = self.GetScrollPixelsPerUnit()
        camAt = (event.GetX() + (xView * xDelta),
                  event.GetY() + (yView * yDelta))
        dxEngine.moveCamera( camAt )                  
        
class OverView( wx.MiniFrame ):
    def __init__(         self, parent, title, virtualSize, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE |wx.MINIMIZE_BOX |wx.MAXIMIZE_BOX
        ):
        self.parent = parent
        global config 
        x=config.overview["x"]
        y=config.overview["y"]
        w=config.overview["width"]
        h=config.overview["height"]
        
        pos = wx.Point( config.overview["x"],config.overview["y"] )
        size = wx.Size( config.overview["width"],config.overview["height"] )
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        self.btnSave = wx.Button(self, -1, "Save Image")
        self.Bind( wx.EVT_BUTTON, self.SaveBmp, self.btnSave  )    
        self.back = OverViewCanvas(self, -1,size=size)
        self.back.SetBackgroundColour("WHITE")
        self.back.SetVirtualSize(virtualSize)
        self.back.SetScrollRate(20,20)
        
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.btnSave, 0 )        
        self.box.Add(wx.StaticLine(self), 0, wx.EXPAND)
        self.box.Add(self.back, 1, wx.EXPAND)
        self.box.Fit(self)
        self.SetSizer(self.box)
        

    def UpdateConfig( self ):
        global config 
        (w,h) = self.GetClientSizeTuple()
        (x,y) = self.GetPositionTuple()
        config.setOverview( x,y,w,h-25 )
        config.save()
                
    def OnCloseWindow(self, event):
        self.UpdateConfig()
        self.parent.overView = None
        self.Destroy()

    def UpdateBmp( self, colors ):
      img = wx.EmptyImage( colors.shape[1],colors.shape[0] )        
      img.SetData( colors.tostring() )
      self.back.bmp = wx.BitmapFromImage( img )
      self.back.Redraw()
      
    def SaveBmp( self,event ):
        self.parent.timer.Stop()
        
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard="PNG file (*.png)|*.png|""Jpeg file (*.jpg)|*.jpg|""Bitmap file (*.bmp)|*.bmp", style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
          path = dlg.GetPath()
          img = wx.ImageFromBitmap( self.back.bmp )          
          im = Image.fromstring( "RGB", ( img.GetWidth(),img.GetHeight()), img.GetData() )
          im.save( path )
        self.parent.timer.Start(33)
      
        
      
  
class ToolBarSliders( wx.MiniFrame ):
    def __init__(         self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE 
        ):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        panel = wx.Panel(self, -1,size=size)

        globalsizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.stRad = wx.StaticText(panel, -1, "Radius : %02d"%(5))
        x = self.stRad
        box.Add( x, 0, wx.ALL, 0 )
        self.sliderR = wx.Slider( panel, -1, 5, 1, 50, style = wx.SL_HORIZONTAL ) #| wx.SL_LABELS
        self.Bind(wx.EVT_SCROLL, parent.OnSlideRadius, self.sliderR )
        box.Add( self.sliderR, 1, wx.GROW|wx.ALL, 0 )
        
        sizer.Add( box, 1, wx.EXPAND|wx.ALL, 0 )
        
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        self.stStr = wx.StaticText(panel, -1, "Strength : %02d"%(10))        
        x = self.stStr
        box.Add( x, 0, wx.ALL, 0 )
        self.sliderS = wx.Slider( panel, -1, 10, 1, 20, style = wx.SL_HORIZONTAL   )#| wx.SL_LABELS
        self.Bind(wx.EVT_SCROLL, parent.OnSlideStrength, self.sliderS )
        box.Add( self.sliderS, 1, wx.EXPAND|wx.ALL, 0 )
        sizer.Add( box, 1, wx.EXPAND|wx.ALL, 0 )

        globalsizer.Add( sizer, 1, wx.EXPAND|wx.ALL, 0 )
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        box = wx.BoxSizer(wx.HORIZONTAL)
        x = wx.StaticText(panel, -1, "Min Height : %04d"%(2))        
        self.stMinH = x
        box.Add( x, 0, wx.ALL, 0 )
        self.sliderMinH = wx.Slider( panel, -1, 2, 2, 6000, style = wx.SL_HORIZONTAL )#| wx.SL_LABELS )
        self.Bind(wx.EVT_SCROLL, parent.OnSlideMinH, self.sliderMinH)
        box.Add( self.sliderMinH, 1, wx.EXPAND|wx.ALL, 0 )
        sizer.Add( box, 1, wx.EXPAND|wx.ALL, 0 )
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        x = wx.StaticText(panel, -1, "Max Height : %04d"%(6000))
        self.stMaxH = x
        box.Add( x, 0, wx.ALL, 0 )
        self.sliderMaxH = wx.Slider( panel, -1, 6000, 2, 6000, style = wx.SL_HORIZONTAL ) #| wx.SL_LABELS)
        self.Bind(wx.EVT_SCROLL, parent.OnSlideMaxH, self.sliderMaxH )
        box.Add( self.sliderMaxH, 1, wx.GROW|wx.ALL, 0 )
        sizer.Add( box, 1, wx.EXPAND|wx.ALL, 0 )
        
        
        globalsizer.Add( sizer, 1, wx.EXPAND|wx.ALL, 0 )
        panel.SetSizer(globalsizer)
        panel.SetAutoLayout(1)
        panel.Fit()
        self.Fit()
        
    def UpdateConfig( self ):
        global config 
        (x,y) = self.GetPositionTuple()
        config.setSliders( x,y )
        config.save()

    def OnCloseWindow(self, event):
        print "OnCloseWindow"
        #self.Destroy()
        
class ToolBar( wx.MiniFrame ):
    def __init__(
        self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
        style=wx.DEFAULT_FRAME_STYLE 
        ):
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        #self.panelA = scrolled.ScrolledPanel(self, -1,size=size)
        
        #box = wx.BoxSizer(wx.VERTICAL)        
        
        self.panel = fpb.FoldPanelBar(self, -1, wx.DefaultPosition, wx.Size(-1,-1), fpb.FPB_DEFAULT_STYLE, fpb.FPB_SINGLE_FOLD)

        item = self.panel.AddFoldPanel("Configuration tools", collapsed=False)
        cb = wx.CheckBox( item, -1, "Edges scrolling" );
        self.Bind( wx.EVT_CHECKBOX, parent.OnEdgeScroll, cb )
        self.panel.AddFoldPanelWindow( item, cb, Spacing=0 )
        cb = wx.CheckBox( item, -1, "Compute shadows" );
        self.Bind( wx.EVT_CHECKBOX, parent.OnDoShadow, cb )
        self.panel.AddFoldPanelWindow( item, cb, Spacing=0 )
        cb = wx.CheckBox( item, -1, "Show cities borders" );
        self.Bind( wx.EVT_CHECKBOX, parent.OnUseConfig, cb )
        self.panel.AddFoldPanelWindow( item, cb, Spacing=0 )
        cb = wx.CheckBox( item, -1, "Render water" );
        cb.SetValue( True )
        self.Bind( wx.EVT_CHECKBOX, parent.OnRenderWater, cb )
        self.panel.AddFoldPanelWindow( item, cb, Spacing=0 )

        b=wx.Button( item, -1, "lock/unlock cities" )
        self.Bind( wx.EVT_BUTTON, parent.OnReportcity, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )

        b=wx.Button( item, -1, "Undo last terraforming" )
        self.Bind( wx.EVT_BUTTON, parent.OnUndo, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )

        b=wx.Button( item, -1, "Change colors" )
        self.Bind( wx.EVT_BUTTON, parent.OnChangeColors, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
            
        item = self.panel.AddFoldPanel("Global tools", collapsed=True)
        
        b=wx.Button( item, -1, "Equalize" )
        self.Bind( wx.EVT_BUTTON, parent.OnEgalise, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
#        b=wx.Button( item, -1, "Water level" )
#        self.Bind( wx.EVT_BUTTON, parent.OnChangeWaterLevel, b )
#        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Raise terran" )
        self.Bind( wx.EVT_BUTTON, parent.OnRaiseTerran, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Lower terran" )
        self.Bind( wx.EVT_BUTTON, parent.OnLowerTerran, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Compressor" )
        self.Bind( wx.EVT_BUTTON, parent.OnCompressor, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Erode terran" )
        self.Bind( wx.EVT_BUTTON, parent.OnErodeTerran, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Erode terran Bis" )
        self.Bind( wx.EVT_BUTTON, parent.OnErodeTerran2, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Import image" )
        self.Bind( wx.EVT_BUTTON, parent.OnImportImage, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Export (SC4M/16bit png)" )
        self.Bind( wx.EVT_BUTTON, parent.OnPrepareExport, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        
        item = self.panel.AddFoldPanel("Zone tools", collapsed=True)

        rb = wx.RadioBox( item, -1, "Tool shape", wx.DefaultPosition, wx.DefaultSize,[ "Rounded", "Square" ], 2, wx.RA_SPECIFY_COLS )
        self.Bind(wx.EVT_RADIOBOX, parent.ChangeToolShape, rb)
        self.panel.AddFoldPanelWindow( item, rb, Spacing=0 )
        
        
        b=wx.Button( item, -1, "Flatten" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetFlatten, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        
        b=wx.Button( item, -1, "Draw" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetDraw, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )

        self.drawHeightText = wx.TextCtrl(item, -1, str(parent.drawHeight), (30, 50), (60, -1), style = wx.TE_PROCESS_ENTER)
        self.Bind( wx.EVT_TEXT_ENTER, parent.OnChangeDrawHeight, self.drawHeightText )
        self.panel.AddFoldPanelWindow( item, self.drawHeightText, Spacing=0 )
        
        
        
        b=wx.Button( item, -1, "Smooth" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetSmooth, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "rough" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetRough, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make hills" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeHill, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make Mountains" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeMountain, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make SteepHill" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeSteepHill, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make Canyon" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeCanyon, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make Valley" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeValley, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make Valley( new)" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeNewValley, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Make Harbor" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetMakeHarbor, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Water erode" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetWeatherErode, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Water erode Enhanced" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetEnhancedErode, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
        b=wx.Button( item, -1, "Talus erosion" )
        self.Bind( wx.EVT_BUTTON, parent.OnSetTalusErode, b )
        self.panel.AddFoldPanelWindow( item, b, Spacing=0 )

        #b=wx.Button( item, -1, "Rain" )
        #self.Bind( wx.EVT_BUTTON, parent.OnSetRain, b )
        #self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
          
        item = self.panel.AddFoldPanel("Universal tools", collapsed=True)
        tools = parent.universalTools
        panelBut = scrolled.ScrolledPanel(item, -1,size=(185,550))
        grid = wx.GridSizer( 0, 2, 2, 2)
        #grid = wx.BoxSizer(wx.VERTICAL)
        for k,v in tools.iteritems():        
            img = wx.EmptyImage( 50,50 )
            img.SetData( tools3D.getShapeUniversal( v ) )
            bmp = wx.BitmapFromImage( img )            
            b=  wx.BitmapButton( panelBut, -1, bmp,size=(55, 55) )
            b.SetLabel( k )
            b.SetToolTipString(k)
            self.Bind( wx.EVT_BUTTON, parent.OnUniversal, b )            
            grid.Add( b, 1, wx.EXPAND|wx.ALL )
        panelBut.SetSizer(grid)
        self.panel.AddFoldPanelWindow( item, panelBut, flags = fpb.FPB_ALIGN_LEFT, Spacing=5 )                    
        #panelBut.Fit()
        panelBut.SetupScrolling()
        
        item = self.panel.AddFoldPanel("Brush tools", collapsed=True)
        brushReader.initBrushesPlugins()
        tools = brushReader.BrushDefinition.allBrushes
        for k,v in tools.iteritems():        
            b=wx.Button( item, -1, k )
            self.Bind( wx.EVT_BUTTON, parent.OnBrush, b )            
            self.panel.AddFoldPanelWindow( item, b, Spacing=0 )
            
      

    def OnCloseWindow(self, event):
        print "OnCloseWindow"
        #self.Destroy()


class SC4Frame(wx.Frame):
    def __init__(
            self, parent, ID, title, pos=wx.DefaultPosition,
            size=(800,600), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
            ):

        self.universalTools = toolReader.ReadTools( "datas/tools.ini" )
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        self.SetIcon(wx.Icon( "icon.ico",wx.BITMAP_TYPE_ICO  ) )
        global config
        x = config.mainwindow["x"]
        y = config.mainwindow["y"]
        self.MoveXY( x, y )        
        self.panel = wx.Panel(self, -1, style=wx.WANTS_CHARS)
        self.unsavedWorks = False

        try:
            self.region = self.LoadARegion()  
        except:
            self.region = None
            dlg = wx.MessageDialog(self, 'A problem has occured while reading the region\nMaybe it is too large for your RAM',
                                 'Error while loading region',
                                 wx.OK | wx.ICON_ERROR
                                 #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                 )
            dlg.ShowModal()
            dlg.Destroy()          
            
        if self.region == None:
          self.Close( True )
          return
        dlg = DlgCities.ReportCitiesDialog( self, -1, "Report" )
        dlg.ShowModal()
        dlg.Destroy()
        
        menuBar = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append( -1,"&Open a region\tCtrl-O",'')
        self.Bind( wx.EVT_MENU, self.OnOpen, item )
        item = menu.Append( -1,"&Create a region\tCtrl-N",'')
        self.Bind( wx.EVT_MENU, self.OnCreate, item )
        item = menu.Append( -1,"&Save\tCtrl-S",'')
        self.Bind( wx.EVT_MENU, self.OnSave, item )
        menu.AppendSeparator()
        item = menu.Append( -1,"Show over&view\tCtrl-V",'')
        self.Bind( wx.EVT_MENU, self.OnOverview, item )
        item = menu.Append( -1,"&Take a picture\tCtrl-Shift-S",'')
        self.Bind( wx.EVT_MENU, self.OnScreenShot, item )
        menu.AppendSeparator()
        item = menu.Append( -1,"&Quit\tAlt-F4",'')
        self.Bind( wx.EVT_MENU, self.OnCloseWindow, item )
        menuBar.Append( menu, "&File" )

        self.Bind( wx.EVT_CLOSE, self.OnCloseWindow  )
        menu = wx.Menu()
        item = menu.Append( -1,"&About\tCtrl-H",'')
        self.Bind( wx.EVT_MENU, self.OnHelpAbout, item )
        menuBar.Append( menu, "&Help" )
        
        self.SetMenuBar( menuBar )

        self.sb = wx.StatusBar( self, -1, style = 0 )
        self.sb.SetFieldsCount( 3 )
        self.sb.SetStatusText( "SC4Terraformer V1.0d", 0 )
        self.sb.SetStatusWidths( [ -1, -2, -2 ] )
        self.sb.SetStatusStyles( [wx.SB_RAISED,wx.SB_RAISED,wx.SB_RAISED] )
        self.SetStatusBar( self.sb )
        
        self.SetClientSize( (800,600) )
        
        if dxEngine.init( self.panel.GetHandle() ) == 0:
          dlg = wx.MessageDialog(self, "DirectX 9.0c is installed but your graphic card can't handle the program",
                                 'Error',
                                 wx.OK | wx.ICON_INFORMATION
                                 #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                 )
          dlg.ShowModal()
          dlg.Destroy()
          self.Close( True )
          
            
        self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_IDLE, self.OnTimer)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        #self.Bind(wx.EVT_IDLE, self.OnTimer)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.panel.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel )
        #self.CaptureMouse()
        dxEngine.initTerran( self.waterLevel, self.region.height.shape, self.region.height,self.region.colors)
        dxEngine.setBgColor( GradientReader.bgColor )
        self.rebuilder = RebuildColors( self.region, self )        
        self.rebuilder.start()
        
        self.move = 0
        self.strafe = 0
        self.up = 0
        self.minHLimit = 2
        self.maxHLimit = 6000
        ms = wx.GetMouseState()
        self.oldMX = ms.x
        self.oldMY = ms.y
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        self.bUpdateTex = False 
        dxEngine.move( 120 )
        self.toolsSlider = ToolBarSliders( self,"",style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)
        self.toolsSlider.Show( True )
        self.tools = ToolBar(self, "SC4Terraformer toolbar",
                  style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION_HORIZ)
        self.tools.Show( True )
        s = self.GetSizeTuple()
        self.tools.SetSize((200, s[1]))                  
        self.toolsSlider.SetSize((s[0], 100))                  
        p = self.GetPositionTuple()
        self.tools.MoveXY( p[0]-200, p[1] )
        x = config.sliders["x"]
        y = config.sliders["y"]
        self.toolsSlider.MoveXY( x, y )
        self.shape = 0
        self.toolRadius = 5
        self.toolStrength = 10
        dxEngine.mouseShape( self.toolRadius,self.shape )
        ms = wx.GetMouseState()
        m = self.panel.ScreenToClient( (ms.x, ms.y) )
        self.umX,self.umY = dxEngine.getCoordUnderMouse( m[0], m[1] )
        self.umFX,self.umFY = self.umX,self.umY
        self.bUseScroll = False
        self.bComputeShadow = False
        self.bRenderWater = True
        self.bUseConfig = False
        self.scaleFactor = 3
        self.minHeight = 0
        self.undoHeight = None
        self.timer.Start(33)
        self.overView = OverView( self, 'Overview', (self.region.height.shape[1],self.region.height.shape[0]),size=(513,513) )
        self.overView.Show( True )
        self.overView.UpdateBmp( self.region.colors )

    
    def OnCreate( self, event ):
        self.timer.Stop()
        if self.unsavedWorks :
          dlg = wx.MessageDialog( self, "Save modifications ?","SC4Terraformer",wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION )
          res = dlg.ShowModal()
          dlg.Destroy()
          if res == wx.ID_CANCEL :
            self.SetFocus()
            self.panel.SetFocus()
            self.timer.Start(33)
            return
          if res == wx.ID_YES :
            self.OnSave( event )

        x = dxEngine.GetDoc()
#        dlg = wx.DirDialog(self, "Create a new region:", x+"\\SimCity 4\\Regions",style=wx.DEFAULT_DIALOG_STYLE|wx.DD_NEW_DIR_BUTTON )
#        if dlg.ShowModal() != wx.ID_OK:
#            dlg.Destroy()
#            self.SetFocus()
#            self.panel.SetFocus()
#            self.timer.Start(33)
#            return
#        path = dlg.GetPath()
#        print path
#        if os.path.isfile( path+"/config.bmp" ):
#          dlg = wx.MessageDialog( self, "This region already exists","SC4Terraformer",wx.OK| wx.ICON_ERROR )
#          dlg.ShowModal()
#          dlg.Destroy()
#          self.SetFocus()
#          self.panel.SetFocus()
#          self.timer.Start(33)
#          return
#        dlg.Destroy()
        dlg = DlgCities.CreateRegionDlg( self, -1, "Region creation" )
        if dlg.ShowModal() == wx.ID_CANCEL:
          dlg.Destroy()
          self.SetFocus()
          self.panel.SetFocus()
          self.timer.Start(33)
          return
          
        name = dlg.regionName.GetValue()
        x = os.path.join( x, "SimCity 4\\Regions" )
        path = os.path.join( x, name )
        width =  float( dlg.width.GetValue() )          
        height =  float( dlg.height.GetValue() )
        sc4mFile = dlg.imagePath.GetValue()
        print sc4mFile
        dlg.Destroy()
        if len( name ) == 0:
          dlg = wx.MessageDialog( self, "This region can't be created( verify the name you have inputed )","SC4Terraformer",wx.OK| wx.ICON_ERROR )
          dlg.ShowModal()
          dlg.Destroy()
          self.SetFocus()
          self.panel.SetFocus()
          self.timer.Start(33)
          return
        
        
        if os.path.isfile( os.path.join( path,"config.bmp" ) ):
          dlg = wx.MessageDialog( self, "This region already exists ( it has a config.bmp )","SC4Terraformer",wx.OK| wx.ICON_ERROR )
          dlg.ShowModal()
          dlg.Destroy()
          self.SetFocus()
          self.panel.SetFocus()
          self.timer.Start(33)
          return
        
        print path
        try:
            os.mkdir( path )
        except OSError:
            pass        
        
        if sc4mFile == "":
            config = Image.new ("RGB", (width,height), "#FF0000" )
            config.save( path+"/config.bmp" )
        
            self.regionPath = path
            class dlgstub:
                def __init__( self ):
                    pass
                def Update( self, x, y ):
                    pass
            
            NewRegion = datReader.SC4Region( self.regionPath,self.waterLevel, dlgstub() )
            NewRegion.show( dlgstub() )
            self.region = NewRegion;
        else:
            try:
                raw = open( sc4mFile,"rb" )            
                buffer1 = raw.read( os.path.getsize( sc4mFile ) )
                raw.close()
                s = zlib.decompress( buffer1 )
                if s[:4] != "SC4M":
                  raise IOError
                version = struct.unpack( "L", s[4:8] )[0]
                if version != 0x0200:
                  raise IOError
                ySize = struct.unpack( "L", s[8:12] )[0]                 
                xSize = struct.unpack( "L", s[12:16] )[0]                
                self.unsavedWorks = True
                mini = struct.unpack( "f", s[16:20] )[0]
                s = s[20:]
                temp = s[:4]
                if temp == "SC4N":
                  s = s[4:]
                  lenHtml = struct.unpack( "L", s[:4] )[0]
                  s = s[4:]
                  htmlText = s[:lenHtml]
                  s = s[lenHtml:]
                  authorNotes = AuthorBox(self,htmlText)
                  authorNotes.ShowModal()
                  authorNotes.Destroy()
                  temp = s[:4]
                  print temp
                if temp == 'SC4C':
                  s = s[4:]                                        
                  configSize = struct.unpack( "LL", s[:8] )
                  s = s[8:]
                  lenstring = struct.unpack( "L", s[:4] )[0]
                  s = s[4:]                      
                  imString = s[:lenstring]
                  config = Image.fromstring( "RGB", configSize, imString )
                  config.save( path+"/config.bmp" )
                  s = s[lenstring:]
                  temp = s[:4]
                  print temp
                if temp != "SC4D":
                  raise IOError
                s = s[4:]
                r = Numeric.fromstring( s[:xSize*ySize], Numeric.UnsignedInt8 )
                rH = Numeric.fromstring( s[xSize*ySize:+xSize*ySize+xSize*ySize], Numeric.UnsignedInt8 )
                r = r.astype( Numeric.Int )
                rH = rH.astype( Numeric.Int )
                rH *= Numeric.array( 256 ).astype( Numeric.Int )
                print rH.shape, rH.typecode(), r.shape, r.typecode()
                r = r + rH
                r = r.astype( Numeric.Float32 )
                r /= Numeric.array( 10 ).astype( Numeric.Float32 )
                r += Numeric.array( mini ).astype( Numeric.Float32 )
                self.regionPath = path
                class dlgstub:
                    def __init__( self ):
                        pass
                    def Update( self, x, y ):
                        pass
                
                NewRegion = datReader.SC4Region( self.regionPath,self.waterLevel, dlgstub() )
                NewRegion.show( dlgstub() )
                self.region = NewRegion;
                self.region.height = Numeric.reshape( r, self.region.height.shape )
                self.region.colors = datReader.ComputeOneRGB( False, self.region.height, self.region.waterLevel );
            except IOError:
                dlg1 = wx.MessageDialog(self, sc4mFile + ' seems not to be a valid image file',
                 'Import error',
                 wx.OK | wx.ICON_ERROR
                 )
                dlg1.ShowModal()
                dlg1.Destroy()
        
        if self.overView is not None:
          self.overView.Destroy()
          self.overView = OverView( self, 'Overview', (self.region.height.shape[1],self.region.height.shape[0]),size=(513,513) )
          self.overView.Show( True )
          self.overView.UpdateBmp( self.region.colors )
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        dxEngine.initTerran( self.waterLevel, self.region.height.shape, self.region.height,self.region.colors)
        self.rebuilder = RebuildColors( self.region, self )        
        self.rebuilder.start()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        
        return
        
                      
    def OnOpen( self, event ):
        self.timer.Stop()
        if self.unsavedWorks :
          dlg = wx.MessageDialog( self, "Save modifications ?","SC4Terraformer",wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION )
          res = dlg.ShowModal()
          dlg.Destroy()
          if res == wx.ID_CANCEL :
            self.SetFocus()
            self.panel.SetFocus()
            self.timer.Start(33)
            return
          if res == wx.ID_YES :
            self.OnSave( event )
        
        try:
            r = self.LoadARegion()
        except:
            r = None
            dlg = wx.MessageDialog(self, 'A problem has occured while reading the region\nMaybe it is too large for your RAM',
                                 'Error while loading region',
                                 wx.OK | wx.ICON_ERROR
                                 #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                 )
            dlg.ShowModal()
            dlg.Destroy()          
            
        if r == None:
            self.SetFocus()
            self.panel.SetFocus()
            self.timer.Start(33)
            return

        
        self.unsavedWorks = False
        self.undoHeight = None
        self.rebuilder.stop()
        running = 1
        while running:
            running = not self.rebuilder.isClosed()
            time.sleep(0.1)

        self.region = r;
        if self.overView is not None:
          self.overView.Destroy()
          self.overView = OverView( self, 'Overview', (self.region.height.shape[1],self.region.height.shape[0]),size=(513,513) )
          self.overView.Show( True )
          self.overView.UpdateBmp( self.region.colors )
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        dlg = DlgCities.ReportCitiesDialog( self, -1, "Report" )
        dlg.ShowModal()
        dlg.Destroy()
        dxEngine.initTerran( self.waterLevel, self.region.height.shape, self.region.height,self.region.colors)
        self.rebuilder = RebuildColors( self.region, self )        
        self.rebuilder.start()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
      

    def LoadARegion( self ):
        x = dxEngine.GetDoc()
        
        # In this case we include a "New directory" button. 
        dlg = wx.DirDialog(self, "Choose a directory:", x+"\\SimCity 4\\Regions",
                          style=wx.DEFAULT_DIALOG_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
          self.regionPath = dlg.GetPath()
        else:
          dlg.Destroy()
          return None                           
          
        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        self.waterLevel = 250.
        self.drawHeight = self.waterLevel+1
        if 0:     
          dlg = wx.TextEntryDialog(
                  self, 'What is your sea level\n250 is default\n',
                  'Some informations', '250')
          if dlg.ShowModal() == wx.ID_OK:
            self.waterLevel = float( dlg.GetValue() )
            self.drawHeight = self.waterLevel+1
          else:          
            dlg.Destroy()          
            return None;
          
          dlg.Destroy()

        dlg = wx.ProgressDialog("Loading region",
                               "Please wait while loading the region",
                               maximum = 6,
                               parent=self,
                               style = 0 )

        dlg.Update( 0 )
        NewRegion = datReader.SC4Region( self.regionPath,self.waterLevel, dlg )
        if NewRegion.allCities == None:
          dlg.Close()
          dlg.Destroy()                  
          return None
        NewRegion.show( dlg )
        dlg.Close()
        dlg.Destroy()        

        if not NewRegion.IsValid():
          dlg = wx.MessageDialog(self, 'This folder seems not to be a valid region',
                                 'Error while loading region',
                                 wx.OK | wx.ICON_ERROR
                                 #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                 )
          dlg.ShowModal()
          dlg.Destroy()          
          return None

        if NewRegion.IsValid() and NewRegion.config == None:
          dlg = wx.MessageDialog(self, "There isn't any config.bmp",
                                 'Warning while loading region',
                                 wx.OK | wx.ICON_INFORMATION
                                 #wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                                 )
          dlg.ShowModal()
          dlg.Destroy()
        return NewRegion          

            
          
    def OnHelpAbout(self, event):
        self.timer.Stop()
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        mainPath = sys.path[0]
        os.chdir(mainPath)
        about = MyAboutBox(self)
        about.ShowModal()
        about.Destroy()
        self.timer.Start(33)

    def OnOverview( self, event ):
        self.timer.Stop()
        if self.overView == None:
          self.overView = OverView( self, 'Overview', (self.region.height.shape[1],self.region.height.shape[0]),size=(513,513) )
          self.overView.Show( True )
          self.overView.UpdateBmp( self.region.colors )
        self.timer.Start(33)
        
    def OnScreenShot( self, event ):
        self.timer.Stop()
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        
        dlg = wx.FileDialog(
            self, message="Save file as ...", defaultDir=os.getcwd(), 
            defaultFile="", wildcard="PNG file (*.png)|*.png|""Jpeg file (*.jpg)|*.jpg|""Bitmap file (*.bmp)|*.bmp", style=wx.SAVE
            )
        if dlg.ShowModal() == wx.ID_OK:
          path = dlg.GetPath()
          dxEngine.saveToFile( unicode( path ) )
        self.timer.Start(33)
      
    def OnSave( self, event ):
        self.timer.Stop()
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        #dlg = wx.MessageDialog(self, "You are about to save your region\nThis is a preliminary version\nMake sure you have made a backup of your region!\nAre you sure you want to save ?",
        dlg = wx.MessageDialog(self, "You are about to save your region\nMake sure you have made a backup of your region!\nAre you sure you want to save ?",        
                               'Warning',                               
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION
                               )
        if dlg.ShowModal() == wx.ID_YES:
          
          dlg1 = wx.ProgressDialog("Saving region",
                               "Please wait while saving the region",
                               maximum = len( self.region.allCities),
                               parent=self,
                               style = 0 )
          if self.region.Save( dlg1 ):
            self.unsavedWorks = False          
          dlg1.Close()
          dlg1.Destroy()        
          
        dlg.Destroy()
        self.timer.Start(33)
          
        
    def VerifyTerran( self, checkHeights = False ):
      if checkHeights:
        if min( self.region.height.flat ) < 2 or max( self.region.height.flat ) > 6000:
          self.unsavedWorks = True
          self.region.height = Numeric.clip( self.region.height, 2, 6000 )        
      return self.region.RewriteLocked()
      
    def UpdateTerran( self, rect, bOnlyHeight=False, bOnlyTex=False ):
      if not bOnlyTex:
        
        dxEngine.updateTerran( self.region.height, self.waterLevel, rect )
        if self.rebuilder.isRunning():
            #print 'stopping rebuilder'
            self.rebuilder.Pause()
            
      if not bOnlyHeight :                
        if self.rebuilder.isRunning():
          #print 'stopping rebuilder'
          self.rebuilder.Pause()
        #print 'launching rebuilder',
        self.rebuilder.Restart()
        #print 'ok'

    def OnChangeColors( self, event ):
      self.timer.Stop()            
      dlg = wx.FileDialog(
          self, message="Choose a new color scheme", defaultDir=os.getcwd(), 
          defaultFile="", wildcard= "colors scheme file |*.ini"
          , style=wx.OPEN  
          )
      if dlg.ShowModal() == wx.ID_OK:
          paths = dlg.GetPaths()[0]
          GradientReader.Init(paths)
          self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) , False, True )
      dlg.Destroy()
      
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
      
      
    def OnUndo( self, event ):
      self.timer.Stop()            
      if self.undoHeight is not None:
        print 'undoing'
        self.region.height = Numeric.reshape( Numeric.fromstring( self.undoHeight, Numeric.Float32), self.region.height.shape )
        self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )              
        self.undoHeight = None
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
      
    def OnReportcity( self, event ):
        self.timer.Stop()
        dlg = DlgCities.ReportCitiesDialog( self, -1, "Report" )
        dlg.ShowModal()
        dlg.Destroy()
        self.VerifyTerran( True)
        self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        
    def OnEdgeScroll( self, event ):
        self.timer.Stop()
        self.bUseScroll = event.IsChecked()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)

    def OnUseConfig( self, event ):
        self.timer.Stop()
        self.bUseConfig = event.IsChecked()
        self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ), False, True  )
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)

    def OnDoShadow( self, event ):
        self.timer.Stop()
        self.bComputeShadow = event.IsChecked()
        self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ), False, True  )
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)

    def OnRenderWater( self, event ):
        self.timer.Stop()
        self.bRenderWater = event.IsChecked()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
            
    def OnChangeWaterLevel( self, event ):
      self.timer.Stop()
      self.actualTool = None
      self.sb.SetStatusText( "No tool selected", 1 )
      dlg = wx.TextEntryDialog(
              self, 'What the new water level',
              'Water Level', str( self.waterLevel ))
      if dlg.ShowModal() == wx.ID_OK:
        self.region.waterLevel = self.waterLevel = float( dlg.GetValue() )
      else:          
        dlg.Destroy()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)

        return;          
      dlg.Destroy()
      self.unsavedWorks = True
      #self.VerifyTerran( False )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ), False, True )
      dxEngine.updateWater( self.region.waterLevel )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
        
    def OnRaiseTerran( self, event ):
      self.timer.Stop()
      
      self.actualTool = None
      self.sb.SetStatusText( "No tool selected", 1 )
      try:
        v = str( self.raiseAmount )
      except:
        v= '10'
      dlg = wx.TextEntryDialog(
              self, 'Raise by which amount',
              'Raising terran', v)
      if dlg.ShowModal() == wx.ID_OK:
        self.raiseAmount = float( dlg.GetValue() )
      else:          
        dlg.Destroy()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        return;          
      dlg.Destroy()
      self.unsavedWorks = True
      self.undoHeight = self.region.height.tostring()
      print 'saving height'
      self.region.height += Numeric.array(self.raiseAmount).astype(Numeric.Float32)
      self.VerifyTerran( True )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSlideMaxH( self, event ):
        self.timer.Stop()
        x = self.toolsSlider.sliderMaxH.GetValue()
        if x < self.minHLimit:
            self.toolsSlider.sliderMaxH.SetValue( self.minHLimit+1 )
            self.maxHLimit = self.minHLimit+1
        else:
            self.maxHLimit = x
        self.toolsSlider.stMaxH.SetLabel( "Max Height : %04d"%(self.maxHLimit) )
        #self.SetFocus()
        #self.panel.SetFocus()
        self.timer.Start(33)

    def OnSlideMinH( self, event ):
        self.timer.Stop()
        x = self.toolsSlider.sliderMinH.GetValue()
        if x > self.maxHLimit:
            self.toolsSlider.sliderMinH.SetValue( self.maxHLimit-1 )
            self.minHLimit = self.maxHLimit-1
        else:
            self.minHLimit = x
        self.toolsSlider.stMinH.SetLabel( "Min Height : %04d"%(self.minHLimit) )
        #self.SetFocus()
        #self.panel.SetFocus()
        self.timer.Start(33)
    
    def OnSlideStrength( self, event ):
        self.timer.Stop()
        self.toolStrength = self.toolsSlider.sliderS.GetValue()        
        self.toolsSlider.stStr.SetLabel( "Strength : %02d"%(self.toolStrength) )
        if self.actualTool:
          self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
        #self.SetFocus()
        #self.panel.SetFocus()
        self.timer.Start(33)
        
        #print "strength = ", self.toolStrength
    def OnSlideRadius( self, event ):
        self.timer.Stop()
        self.toolRadius = self.toolsSlider.sliderR.GetValue()
        self.toolsSlider.stRad.SetLabel( "Radius : %02d"%(self.toolRadius) )
        if self.actualTool:
          self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
        #self.SetFocus()
        #self.panel.SetFocus()
        
        dxEngine.mouseShape( self.toolRadius,self.shape )
        self.timer.Start(33)
        #print "radius = ", self.toolRadius
        
    def ChangeToolShape( self, event ):
        self.timer.Stop()
        self.shape = event.GetInt()
        self.SetFocus()
        self.panel.SetFocus()
        
        dxEngine.mouseShape( self.toolRadius,self.shape )
        self.timer.Start(33)
        #print self.shape
        
    def OnChangeDrawHeight( self, event ):
      self.timer.Stop()
      self.drawHeight = float( event.GetString() )
      if self.actualTool:
        if self.actualTool.__class__ == terraTools.DrawTool or self.actualTool.__class__ == terraTools.TalusErode:
          self.actualTool.ChangeLevel( self.drawHeight )
          self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
          
    def OnBrush( self, event ):
      self.timer.Stop()
      toolName = event.GetEventObject().GetLabel()
      self.actualTool = terraTools.BrushTool( toolName )
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
        
    def OnUniversal( self, event ):
      self.timer.Stop()
      toolName = event.GetEventObject().GetLabel()
#      img = wx.EmptyImage( 100,100 )
#      img.SetData( tools3D.getShapeUniversal( self.universalTools[ toolName ] ) )
#      bmp = wx.BitmapFromImage( img )
#      self.tools.bitmap.SetBitmap( bmp )
      print self.universalTools
      self.actualTool = terraTools.UniversalTool( toolName, self.universalTools[ toolName ] )
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
    
    def OnSetDraw( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.DrawTool( self.drawHeight )
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
      
    def OnSetFlatten( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.Flatten()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetBrush( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.BrushTool()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetSmooth( self, event ):      
      self.timer.Stop()
      self.actualTool = terraTools.Smooth()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetRough( self, event ):      
      self.timer.Stop()
      self.actualTool = terraTools.Roughen()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
     
    def OnSetMakeHill( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.MakeHill()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetMakeCanyon( self, event ):      
      self.timer.Stop()
      self.actualTool = terraTools.MakeCanyon()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
      
    def OnSetMakeSteepHill( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.MakeSteepHill()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
      
    def OnSetMakeMountain( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.MakeMountainJason()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetMakeValley( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.MakeValley()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetMakeNewValley( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.MakeNewValley()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetMakeHarbor( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.MakeHarbor( self.waterLevel + .5 )
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
 
    def OnSetEnhancedErode( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.WeatherErodeNew()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetTalusErode( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.TalusErode( self.drawHeight )
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnSetRain( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.RainErode()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

      
    def OnSetWeatherErode( self, event ):
      self.timer.Stop()
      self.actualTool = terraTools.WeatherErode()
      self.sb.SetStatusText( self.actualTool.name+" radius : %d / strength : %d"%(self.toolRadius,self.toolStrength), 1 )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
    
      
    def OnPrepareExport( self, event ):
      self.timer.Stop()
      mini = 0
      r = self.region.height - Numeric.array( mini ).astype(Numeric.Float32)
      r *= Numeric.array( 10 ).astype( Numeric.Float32 )
      res = r.astype( Numeric.Int )
      
      
      dlg = wx.FileDialog(
          self, message="Export region as ...", defaultDir=os.getcwd(), 
          defaultFile="", wildcard="SC4 Terrain files (*.SC4M)|*.SC4M""|16bit png files (*.png)|*.png|RGB files (*.bmp)|*.bmp", style=wx.OPEN
          )
      if dlg.ShowModal() == wx.ID_OK:
        im =Image.fromstring( "RGBA",( self.region.height.shape[1],self.region.height.shape[0]), res.tostring() )
        path = dlg.GetPath()
      
        ext = os.path.splitext( path )[1].upper()
        if  ext == ".BMP":
            h = self.region.height * Numeric.array( 10 ).astype(Numeric.Float32)
            h = Numeric.floor( h ).astype( Numeric.Int )
            red = ( (h / Numeric.array(4096) ) % Numeric.array(16) )*Numeric.array(16)
            green = ( (h / Numeric.array(256) ) % Numeric.array(16) )*Numeric.array(16)
            blue = h % Numeric.array(256)
            red = red.astype( Numeric.UnsignedInt8 )
            green = green.astype( Numeric.UnsignedInt8 )
            blue = blue.astype( Numeric.UnsignedInt8 )
            imRed = Image.fromstring( "L", ( self.region.height.shape[1],self.region.height.shape[0]), red.tostring() )
            imGreen = Image.fromstring( "L", ( self.region.height.shape[1],self.region.height.shape[0]), green.tostring() )
            imBlue = Image.fromstring( "L", ( self.region.height.shape[1],self.region.height.shape[0]), blue.tostring() )
            im = Image.merge( "RGB", ( imRed, imGreen, imBlue ) )
                        
            if 0:
                h = self.region.height.flat
                res = ""
                for height in h:
                  cur = height * 10.
                  cur = int( cur )
                  red = (math.floor( cur/4096 )%16)*16
                  green = (math.floor( cur/256 )%16)*16
                  blue = cur%256
                  res += struct.pack( "BBB", red,green,blue ) 
                im =Image.fromstring( "RGB",( self.region.height.shape[1],self.region.height.shape[0]), res )
            im.save( path )
            dlg1 = wx.MessageDialog(self, path + ' as been exported',
             'Export done',
             wx.OK | wx.ICON_INFORMATION
             )
            dlg1.ShowModal()
            dlg1.Destroy()
            
        if  ext == ".SC4M":
            dlg1 = wx.FileDialog( self, message="Enter a hml file that will be displayed on import", defaultDir=os.getcwd(), defaultFile="", wildcard="HTML files (*.HTML)|*.html", style=wx.OPEN )
            if dlg1.ShowModal() == wx.ID_OK:
              htmlFileName = dlg1.GetPaths()[0]           
            else:
              htmlFileName = None
            s = "SC4M"        
            s += struct.pack( "L",0x0200 )
            s += struct.pack( "L",self.region.height.shape[0] )        
            s += struct.pack( "L",self.region.height.shape[1] ) 
            s += struct.pack( "f",mini )
            if htmlFileName is not None:
              s += "SC4N" # author notes
              filehtml = open( htmlFileName )
              lines = filehtml.readlines()
              line = "\n".join( lines )
              filehtml.close()
              s += struct.pack( "L", len( line ) )
              s += line
            s += "SC4C" # config.bmp included
            s += struct.pack( "L", self.region.config.size[0] )
            s += struct.pack( "L", self.region.config.size[1] )
            configStr = self.region.config.tostring()
            s += struct.pack( "L", len( configStr ) )
            s += configStr
            s += "SC4D" # elevation data
            for b in im.split()[:2]:
              s += b.tostring()
            raw = open( path,"wb" )            
            raw.write( zlib.compress( s, 9) )
            raw.close()
            dlg1 = wx.MessageDialog(self, path + ' as been exported',
             'Export done',
             wx.OK | wx.ICON_INFORMATION
             )
            dlg1.ShowModal()
            dlg1.Destroy()
        if ext == ".PNG":
            im =Image.fromstring( "I",( self.region.height.shape[1],self.region.height.shape[0]), res.tostring() )
            im.save( path )
            dlg1 = wx.MessageDialog(self, path + ' as been exported',
             'Export done',
             wx.OK | wx.ICON_INFORMATION
             )
            dlg1.ShowModal()
            dlg1.Destroy()
                
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        self.VerifyTerran( True )
        self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      else:
        dlg.Destroy()
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnErodeTerran( self, event ):
      self.timer.Stop()
      self.undoHeight = self.region.height.tostring()
      print 'saving height'
      self.actualTool = None
      self.unsavedWorks = True
      self.sb.SetStatusText( "No tool selected", 1 )
      h = self.region.height.tostring()
      z = tools3D.waterErode( 8.0, .01, .04, 1., 20, 5, self.region.height.shape, h )
      x = tools3D.weatherErode( 10, 0.05, 4, self.region.height.shape, z )
      rawHeight = tools3D.egalize( self.region.height.shape, x )
      ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
      self.region.height = Numeric.reshape( ret, self.region.height.shape )
      self.VerifyTerran( True )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnErodeTerran2( self, event ):
      self.timer.Stop()
      self.undoHeight = self.region.height.tostring()
      print 'saving height'
      self.unsavedWorks = True
      self.actualTool = None
      self.sb.SetStatusText( "No tool selected", 1 )
      h = self.region.height.tostring()
      x = tools3D.weatherErode( 10, 0.05, 4, self.region.height.shape, h )
      z = tools3D.waterErode( 8.0, .01, .04, 1., 20, 5, self.region.height.shape, x )
      rawHeight = tools3D.egalize( self.region.height.shape, z )
      ret = Numeric.fromstring( rawHeight, Numeric.Float32 )
      self.region.height = Numeric.reshape( ret, self.region.height.shape )
      self.VerifyTerran( True )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
    
    def OnImportImage( self, event ):
        self.timer.Stop()
        self.actualTool = None
        self.sb.SetStatusText( "No tool selected", 1 )
        dlg = DlgCities.ImportImgDlg( self, -1,"Import image",self.scaleFactor, self.minHeight )
        #dlg = wx.FileDialog(
        #    self, message="Choose an image", defaultDir=os.getcwd(), 
        #    defaultFile="", wildcard= "Jpeg file (*.jpeg;*.jpg)|*.jpeg;*.jpg|""Bitmap file (*.bmp)|*.bmp|""All files (*.*)|*.*"
        #    , style=wx.OPEN  | wx.CHANGE_DIR
        #    )
        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetImageName().upper()
            print os.path.splitext( paths )[1]
            if os.path.splitext( paths )[1] == ".TER":
                  print 'terrangen file'
                  xSize = 0
                  ySize = 0
                  raw = open( paths,"rb" )
                  s = raw.read( os.path.getsize( paths ) )
                  raw.close()
                  if s[:8] != "TERRAGEN":
                    print 'no terragen'
                    raise IOError
                  s=s[8:]
                  if s[:8] != "TERRAIN ":
                    print 'no terrain'
                    raise IOError
                  s=s[8:]
                  chunkName = s[:4]
                  if chunkName == "SIZE":                    
                    s=s[4:]
                    sizeStr = s[:2]
                    size = struct.unpack("H",sizeStr)[0]
                    xSize = size+1
                    ySize = size+1
                    s=s[4:]
                  else:
                    print 'no size'
                    raise IOError
                  sc = 30
                  while 1:
                      chunkName = s[:4]
                      if chunkName == "XPTS":
                        print 'xpts'
                        s=s[4:]
                        sizeStr = s[:2]
                        xSize = struct.unpack("H",sizeStr)[0]
                        s=s[4:]
                      if chunkName == "YPTS":
                        print 'ypts'
                        s=s[4:]
                        sizeStr = s[:2]
                        ySize = struct.unpack("H",sizeStr)[0]
                        s=s[4:]
                      if chunkName == "SCAL":
                        print 'scal'
                        s = s[4:]
                        sc = struct.unpack("f",s[:4])[0]
                        print sc
                        s = s[12:]
                      if chunkName == "CRAD":
                        print 'crad'
                        s = s[4:]
                        s = s[4:]
                      if chunkName == "CRVM":
                        print 'crvm'
                        s = s[4:]
                        s = s[4:]
                      if chunkName == "ALTW":
                        print 'altw'
                        if xSize == self.region.height.shape[1] and ySize == self.region.height.shape[0]:                                              
                            self.unsavedWorks = True
                            s = s[4:]
                            hs = struct.unpack("h",s[:2])[0]
                            print hs                        
                            bh = struct.unpack("h",s[2:4])[0]
                            print bh
                            s = s[4:]
                            s = s[:xSize*ySize*2]
                            r = Numeric.fromstring( s, Numeric.Int16 )
                            
                            r = r.astype( Numeric.Float32 )
                            r /= Numeric.array( 65536 ).astype( Numeric.Float32 )
                            #mini = min( r )
                            #r -= Numeric.array( mini ).astype( Numeric.Float32 )
                            r *= Numeric.array( hs*sc ).astype( Numeric.Float32 )
                            r += Numeric.array( bh+self.waterLevel ).astype( Numeric.Float32 )
                            self.region.height = Numeric.reshape( r, self.region.height.shape )
                            self.VerifyTerran( True )
                            self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
                        else:
                          dlg1 = wx.MessageDialog(self, paths + ' has not correct dimensions\n'+'It should be (%d by %d) but it is (%d by %d)'%(self.region.height.shape[1],self.region.height.shape[0],xSize,ySize),
                           'Import error',
                           wx.OK | wx.ICON_ERROR
                           )
                          dlg1.ShowModal()
                          dlg1.Destroy()
                        break
                                                    
                                                
            elif os.path.splitext( paths )[1] == ".SC4M":
              try:
                raw = open( paths,"rb" )            
                buffer1 = raw.read( os.path.getsize( paths ) )
                raw.close()
                s = zlib.decompress( buffer1 )
                if s[:4] != "SC4M":
                  raise IOError
                version = struct.unpack( "L", s[4:8] )[0]
                if version != 0x0100:
                  if version != 0x0200:
                    raise IOError
                ySize = struct.unpack( "L", s[8:12] )[0]                 
                xSize = struct.unpack( "L", s[12:16] )[0]                
                if xSize == self.region.height.shape[1] and ySize == self.region.height.shape[0]:                                              
                    self.unsavedWorks = True
                    mini = struct.unpack( "f", s[16:20] )[0]
                    s = s[20:]
                    temp = s[:4]
                    if temp == "SC4N":
                      
                      s = s[4:]
                      lenHtml = struct.unpack( "L", s[:4] )[0]
                      s = s[4:]
                      htmlText = s[:lenHtml]
                      s = s[lenHtml:]
                      authorNotes = AuthorBox(self,htmlText)
                      authorNotes.ShowModal()
                      authorNotes.Destroy()
                      temp = s[:4]
                      print temp
                    if temp == 'SC4C':
                      s = s[4:]                                        
                      configSize = struct.unpack( "LL", s[:8] )
                      s = s[8:]
                      lenstring = struct.unpack( "L", s[:4] )[0]
                      s = s[4:]                      
                      imString = s[:lenstring]
                      #Image.fromstring( "RGB", configSize, imString ).show()
                      s = s[lenstring:]
                      temp = s[:4]
                      print temp
                    if temp != "SC4D":
                      raise IOError
                    s = s[4:]
                    r = Numeric.fromstring( s[:xSize*ySize], Numeric.UnsignedInt8 )
                    rH = Numeric.fromstring( s[xSize*ySize:+xSize*ySize+xSize*ySize], Numeric.UnsignedInt8 )
                    r = r.astype( Numeric.Int )
                    rH = rH.astype( Numeric.Int )
                    rH *= Numeric.array( 256 ).astype( Numeric.Int )
                    print rH.shape, rH.typecode(), r.shape, r.typecode()
                    r = r + rH
                    r = r.astype( Numeric.Float32 )
                    r /= Numeric.array( 10 ).astype( Numeric.Float32 )
                    r += Numeric.array( mini ).astype( Numeric.Float32 )
                    self.region.height = Numeric.reshape( r, self.region.height.shape )
                    self.VerifyTerran( True )
                    self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
                else:
                  dlg1 = wx.MessageDialog(self, paths + ' has not correct dimensions\n'+'It should be (%d by %d) but it is (%d by %d)'%(self.region.height.shape[1],self.region.height.shape[0],xSize,ySize),
                   'Import error',
                   wx.OK | wx.ICON_ERROR
                   )
                  dlg1.ShowModal()
                  dlg1.Destroy()
                                  
              except IOError:
                dlg1 = wx.MessageDialog(self, paths + ' seems not to be a valid image file',
                 'Import error',
                 wx.OK | wx.ICON_ERROR
                 )
                dlg1.ShowModal()
                dlg1.Destroy()
              
            else:
              try:
                im = Image.open( paths )
              except IOError:
                dlg1 = wx.MessageDialog(self, paths + ' seems not to be a valid image file',
                 'Import error',
                 wx.OK | wx.ICON_ERROR
                 )
                dlg1.ShowModal()
                dlg1.Destroy()
              else:
                ok = False
                if not( im.size[0] == self.region.height.shape[1] and im.size[1] == self.region.height.shape[0]) : 
                  dlg1 = wx.MessageDialog(self, paths + ' has not correct dimensions\n'+'It should be (%d by %d) but it is (%d by %d)\nDo you want to resize the image to fit region dimensions?'%(self.region.height.shape[1],self.region.height.shape[0],im.size[0],im.size[1]),
                   'Import warning',
                   wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION
                   )
                  res = dlg1.ShowModal()
                  if res == wx.ID_YES:
                    ok = True
                    im = im.resize( (self.region.height.shape[1], self.region.height.shape[0]),Image.BICUBIC )
                  dlg1.Destroy()
                  
                else:
                    ok = True
                if ok:                              
                  self.unsavedWorks = True
                  self.scaleFactor = dlg.GetImageFactor()
                  self.minHeight = dlg.GetMinHeight()
                  if im.mode == "I":
                    r = Numeric.fromstring( im.tostring(), Numeric.Int )
                    r = r.astype( Numeric.Float32 )
                    r /= Numeric.array( 10 ).astype( Numeric.Float32 )
                    self.region.height = Numeric.reshape( r, self.region.height.shape )
                  else:
                      result = QuestionDialog.questionDialog( 'You have selected a 8bit image\nDo you want to import it as greyscale or as RGB scheme?', buttons =["Greyscale","RGB"] )  
                      if result == 'RGB':
                          im = im.convert( "RGB" )
                          r = Numeric.fromstring( im.tostring(), Numeric.UnsignedInt8 )
                          print self.region.height.shape[0],self.region.height.shape[1], self.region.height.shape[1]*self.region.height.shape[0]
                          print r.shape
                          r = Numeric.reshape( r, ( self.region.height.shape[0],self.region.height.shape[1],3) )                          
                          r = r.astype(Numeric.Float32)
                          print r.shape
                          red = Numeric.floor(r[:,:,0]/Numeric.array( 16 ).astype( Numeric.Float32 ))
                          green = Numeric.floor(r[:,:,1]//Numeric.array( 16 ).astype( Numeric.Float32 ))
                          blue = r[:,:,2]
                          
                          res = red*Numeric.array( 4096 ).astype( Numeric.Float32 )
                          res += green*Numeric.array( 256 ).astype( Numeric.Float32 )
                          res += blue                          
                          self.region.height = res / Numeric.array( 10 ).astype( Numeric.Float32 )
                          #self.region.height = (red*4096+green*256+blue)/10
                          if 0:
                              for i in xrange( self.region.height.shape[0]*self.region.height.shape[1] ):
                                y = i/self.region.height.shape[1]
                                x = i%self.region.height.shape[1]
                                v = tuple( r[i] )
                                
                                red = math.floor(v[0]/16)
                                green= math.floor(v[1]/16)
                                blue = v[2]
                                h = red*4096+green*256+blue  
                                self.region.height[ y,x ] = h/10
                      else:
                        im = im.convert( "L" )
                        r = Numeric.fromstring( im.tostring(), Numeric.UnsignedInt8 )
                        r = Numeric.asarray( r, Numeric.Float32 )
                        r += Numeric.array(self.minHeight).astype(Numeric.Float32)
                        r *= Numeric.array(self.scaleFactor).astype(Numeric.Float32)
                        self.region.height = Numeric.reshape( r, self.region.height.shape )
                      

                  self.VerifyTerran( True )
                  self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
                
        self.SetFocus()
        self.panel.SetFocus()              
        dlg.Destroy()
        
        self.timer.Start(33)

      
    def OnCompressor( self, event ):
      self.timer.Stop()
      self.actualTool = None
      self.sb.SetStatusText( "No tool selected", 1 )
      
      minVal = min( self.region.height.flat )
      maxVal = max( self.region.height.flat )

      dlg = DlgCities.CompressorDlg( self, minVal, maxVal )
      if dlg.ShowModal() == wx.ID_CANCEL:
        dlg.Destroy()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        return;    
      
      try:
        piv = float(dlg.pivot.GetValue())
        print piv
      except:
        piv = 0

      try:
        minMap = float(dlg.minMap.GetValue())
        print minMap
      except:
        minMap = minVal

      try:
      
        maxMap = float(dlg.maxMap.GetValue())
        print maxMap
      except:
        maxMap = maxVal
      
      maxMap = float(dlg.maxMap.GetValue())
      dlg.Destroy()
      print piv, minMap, maxMap
        
      if minMap >= maxMap :
        dlg = wx.MessageDialog(self, "Min value should be less than max value" ,'Error',
                 wx.OK | wx.ICON_ERROR
                 )
        dlg.ShowModal()
        dlg.Destroy()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        return;    
        
      if piv > 0 and ( piv <minMap or piv > maxMap ):
        dlg = wx.MessageDialog(self, "unchanged value should be between min and max value" ,'Error',
                 wx.OK | wx.ICON_ERROR
                 )
        dlg.ShowModal()
        dlg.Destroy()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        return;    
        
      
      
      self.undoHeight = self.region.height.tostring()
      print 'saving height'
      self.unsavedWorks = True

      if piv <= 0:        
        self.region.height -= Numeric.array(minVal).astype(Numeric.Float32)
        self.region.height /= Numeric.array(maxVal-minVal).astype(Numeric.Float32)
        self.region.height *= Numeric.array(maxMap-minMap).astype(Numeric.Float32)
        self.region.height += Numeric.array(minMap).astype(Numeric.Float32)
      else:
        maskAbove = Numeric.greater_equal( self.region.height, piv ).astype(Numeric.Float32)
        maskUnder = Numeric.less( self.region.height, piv ).astype(Numeric.Float32)
        above = maskAbove*self.region.height
        under = maskUnder*self.region.height
        
        under -= Numeric.array(minVal).astype(Numeric.Float32)
        under /= Numeric.array(piv-minVal).astype(Numeric.Float32)
        under *= Numeric.array(piv-minMap).astype(Numeric.Float32)
        under += Numeric.array(minMap).astype(Numeric.Float32)
        
        above -= Numeric.array(piv).astype(Numeric.Float32)
        above /= Numeric.array(maxVal-piv).astype(Numeric.Float32)
        above *= Numeric.array(maxMap-piv).astype(Numeric.Float32)
        above += Numeric.array(piv).astype(Numeric.Float32)
        
        self.region.height = under*maskUnder + above*maskAbove

      self.VerifyTerran( True )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
        
    def OnLowerTerran( self, event ):
      self.timer.Stop()
      
      self.actualTool = None
      self.sb.SetStatusText( "No tool selected", 1 )
  
      try:
        v = str( self.lowerAmount )
      except:
        v= '10'
      dlg = wx.TextEntryDialog(
              self, 'Lower by which amount',
              'Lowering terran', v)
      if dlg.ShowModal() == wx.ID_OK:
        self.lowerAmount = float( dlg.GetValue() )
      else:          
        dlg.Destroy()
        self.SetFocus()
        self.panel.SetFocus()
        self.timer.Start(33)
        return;          
      dlg.Destroy()
      self.undoHeight = self.region.height.tostring()
      print 'saving height'
      self.unsavedWorks = True
      self.region.height -= Numeric.array(self.lowerAmount).astype(Numeric.Float32)
      self.VerifyTerran( True )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)
        
    def OnEgalise(self, event):        
      self.timer.Stop()
      self.actualTool = None
      self.sb.SetStatusText( "No tool selected", 1 )
      self.unsavedWorks = True
      self.undoHeight = self.region.height.tostring()
      print 'saving height'
      rawHeight = tools3D.egalize( self.region.height.shape, self.region.height.tostring() )
      self.region.height = Numeric.fromstring( rawHeight, Numeric.Float32 )
      self.region.height = Numeric.reshape( self.region.height, (self.region.imgSize[1],self.region.imgSize[0]) )
      self.VerifyTerran( True )
      self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
      self.SetFocus()
      self.panel.SetFocus()
      self.timer.Start(33)

    def OnMouseWheel( self,evt ):
      speedUp = 10
      if evt.ShiftDown():
        speedUp = 1
      #print evt.GetWheelDelta(), evt.GetWheelRotation()
      if evt.GetWheelRotation() < 0:
          dxEngine.moveUp( 12*speedUp )            
      if evt.GetWheelRotation() > 0:
          dxEngine.moveUp( -12*speedUp )            
      
    def OnKeyUp(self, evt):
      keycode = evt.GetKeyCode()
      print "up",keycode
      if keycode==71:
        dxEngine.turnGrid()
      if keycode == wx.WXK_NUMPAD_ADD or keycode == wx.WXK_NUMPAD_SUBTRACT:
        self.up = 0
      if keycode == wx.WXK_UP or keycode == wx.WXK_DOWN:
        self.move = 0
      if keycode == wx.WXK_LEFT or keycode == wx.WXK_RIGHT:
        self.strafe = 0
        
    def OnKeyDown(self, evt):
        keycode = evt.GetKeyCode()
        print "down",keycode
          
        if keycode == wx.WXK_NUMPAD_ADD:
          self.up = -1
        if keycode == wx.WXK_NUMPAD_SUBTRACT:
          self.up = 1

        if keycode == wx.WXK_UP:
          self.move = 1
        if keycode == wx.WXK_DOWN:
          self.move = -1
        if keycode == wx.WXK_LEFT:
          self.strafe = -1
        if keycode == wx.WXK_RIGHT:
          self.strafe = 1



    def OnCloseWindow(self, event):
        self.timer.Stop()
        global config 
        if self.overView is not None:
            self.overView.UpdateConfig()

        self.toolsSlider.UpdateConfig()
        (x,y) = self.GetPositionTuple()
        config.setMainwindow( x,y )
        config.save()
        if self.unsavedWorks :
          dlg = wx.MessageDialog( self, "Save modifications ?","SC4Terraformer",wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION )
          res = dlg.ShowModal()
          dlg.Destroy()
          if res == wx.ID_CANCEL :
            self.SetFocus()
            self.panel.SetFocus()
            self.timer.Start(33)
            return
          if res == wx.ID_YES :
            self.OnSave( event )
        else:
          dlg = wx.MessageDialog( self, "Are you sure you want to quit ?","SC4Terraformer",wx.YES_NO | wx.YES_DEFAULT | wx.ICON_INFORMATION )
          res = dlg.ShowModal()
          dlg.Destroy()
          if res == wx.ID_NO :
            self.SetFocus()
            self.panel.SetFocus()
            self.timer.Start(33)
            return
        
        
        self.rebuilder.stop()
        running = 1
        while running:
            running = not self.rebuilder.isClosed()
            time.sleep(0.1)
            
        dxEngine.closeTerran()
        dxEngine.close()
        self.Destroy()
      
    
              
    def OnTimer(self, evt):
        self.timer.Stop()
        if not self.rebuilder.isRunning():            
            if self.rebuilder.colors is not None:
                self.region.colors = self.rebuilder.colors
                self.rebuilder.colors = None
                print 'Sending color to dx'
                dxEngine.updateColors( self.region.colors.tostring() )
                if self.overView is not None:
                  self.overView.UpdateBmp(self.region.colors)
                #self.region.colors = None
                print 'ok'
                self.rebuilder.Pause()
        ms = wx.GetMouseState()
        m = self.panel.ScreenToClient( (ms.x, ms.y) )
        
        
        #print umX, umY
            
             
        p = self.GetPositionTuple()
        s = self.GetSizeTuple()
        self.tools.MoveXY( p[0]-200, p[1] )
        #self.toolsSlider.MoveXY( p[0], p[1]+s[1] )
        
        
        
        self.MDX = self.oldMX - ms.x
        self.MDY = self.oldMY - ms.y
        
        umFX,umFY = dxEngine.getFloatCoordUnderMouse( m[0], m[1] )
        umDX = umFX - self.umFX
        umDY = umFY - self.umFY
        self.umFX = umFX
        self.umFY = umFY
        if self.actualTool is not None and ( int(umDX) != 0 or int(umDY) != 0 ):
          self.actualTool.mouseDelta( umDX, umDY )
        
        if self.MDX != 0 or self.MDY != 0:
          umX,umY = dxEngine.getCoordUnderMouse( m[0], m[1] )
          if umX < 0:
            umX = 0
          if umY < 0:
            umY = 0
          if umX >= self.region.height.shape[1]:
            umX = self.region.height.shape[1]-1
          if umY >= self.region.height.shape[0]:
            umY = self.region.height.shape[0]-1
          self.umX = umX
          self.umY = umY
          
        try:
          height = self.region.height[ self.umY, self.umX ]
          self.sb.SetStatusText( "x:%d y:%d height:%.02fm"%( self.umX, self.umY, height ), 2 )          
        except:
          print self.umY, self.umX
        

        rc = self.panel.GetRect()
        outOfWindow = False
        #print m, rc
        if m[0] <= 0 or m[0] >= rc.width or m[1]<=0 or m[1]>=rc.height:
            outOfWindow = True
        
        if not outOfWindow :
            outOfWindow = self.FindFocus()!=self.panel
        if not outOfWindow:              
            if ms.leftDown :
              if self.actualTool is not None :
                if self.actualTool.__class__ is not terraTools.RainErode:
                  def ComputeInd( x,y ):
                    if x < 0 : x = 0
                    if x >= self.region.height.shape[1]: x = self.region.height.shape[1]-1
                    if y < 0 : y = 0
                    if y >= self.region.height.shape[0]: y = self.region.height.shape[0]-1
                    return x + y*self.region.height.shape[1]
                  def ComputeMask( x,y ):
                    if x < 0 : return 0
                    if x >= self.region.height.shape[1]: return 0
                    if y < 0 : return 0
                    if y >= self.region.height.shape[0]: return 0
                    return 1
                  if self.bUpdateTex == False:
                      self.undoHeight = self.region.height.tostring()
                      print 'saving height'
                      self.actualTool.onStart( self.region.height.flat[ self.umX+self.umY*self.region.height.shape[1] ] )
                  indices = [ ComputeInd(x,y) for y in xrange( self.umY-self.toolRadius, self.umY+self.toolRadius+1) for x in xrange( self.umX-self.toolRadius, self.umX+self.toolRadius+1 )  ]
                  #print indices
                  v = Numeric.take( self.region.height.flat, indices )
                  v = Numeric.reshape( v, ((self.toolRadius*2)+1,(self.toolRadius*2)+1) )
                  strength = float(self.toolStrength)/20.;
                  strength = max( 0, math.exp( strength )-1. )
                  v= self.actualTool.apply( self.shape, self.toolRadius, strength , v )
                  if min( v.flat ) < 2 or max( v.flat ) > 6000:
                    v = Numeric.clip( v, 2, 6000 )  
                  if min( v.flat ) < self.minHLimit or max( v.flat ) > self.maxHLimit:
                    print 'outside limits'         
                    if self.shape == 1:
                      v = Numeric.clip( v, self.minHLimit, self.maxHLimit )  
                    else:
                      radius = self.toolRadius
                      mask = Numeric.zeros( v.shape )
                      for y in xrange( -radius, radius+1):
                          for x in xrange( -radius, radius+1):
                              dist = math.sqrt( x*x+y*y )
                              if dist < float(radius):
                                  mask[y+radius,x+radius] = 1
                      Numeric.putmask( v, mask, Numeric.clip( v, self.minHLimit, self.maxHLimit ) )                               
                  
                  #v = Numeric.transpose(v)
                  
                  x = self.umX
                  y = self.umY
                  x1Dest = x-self.toolRadius
                  x2Dest = x+self.toolRadius+1
                  y1Dest = y-self.toolRadius
                  y2Dest = y+self.toolRadius+1
                  x1Src=0
                  y1Src=0
                  x2Src=v.shape[1]
                  y2Src=v.shape[0]
                  if x1Dest < 0:
                    x1Src -= x1Dest
                    x1Dest = 0
                  if y1Dest < 0:
                    y1Src -= y1Dest
                    y1Dest = 0
                  if x2Dest > self.region.height.shape[1]:
                    x2Src -= x2Dest - self.region.height.shape[1]
                    x2Dest = self.region.height.shape[1]
                  if y2Dest > self.region.height.shape[0]:
                    y2Src -= y2Dest - self.region.height.shape[0]
                    y2Dest = self.region.height.shape[0]
                  self.region.height[ y1Dest:y2Dest,x1Dest:x2Dest ] = v[y1Src:y2Src,x1Src:x2Src]
                  self.UpdateTerran( ( self.umX-self.toolRadius,self.umY-self.toolRadius,self.umX+self.toolRadius,self.umY+self.toolRadius ), True )
                  self.bUpdateTex = True
                  self.unsavedWorks = True
                else:
                  if self.bUpdateTex == False:
                      self.undoHeight = self.region.height.tostring()
                  strength = float(self.toolStrength)/20.;
                  strength = max( 0, math.exp( strength )-1. )
                  r = tools3D.rainErode( (self.umX, self.umY), strength, self.region.height.shape, self.region.height.tostring() )    
                  self.region.height = Numeric.reshape( Numeric.fromstring( r, Numeric.Float32 ), self.region.height.shape )
                  self.unsavedWorks = True
                  self.bUpdateTex = True
                  self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
            else:
              if self.bUpdateTex:
                b = self.VerifyTerran()
                self.bUpdateTex = False
                print 'rebuild coloring start'
                if b:
                  self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ) )
                else:
                  self.UpdateTerran( ( 0,0,self.region.imgSize[0],self.region.imgSize[1] ), False, True )
                #self.UpdateTerran( ( self.umX-5,self.umX+5,self.umY-5,self.umY+5 ), False, True )
            
              if ms.shiftDown:
                speedUp = 1.
              else:
                speedUp = 10.
      
              bMRotY = ms.middleDown and self.MDX != 0
              bMRotX = ms.middleDown and self.MDY != 0
              if bMRotY:                       
                dxEngine.rotY( (self.MDX/2000.)*speedUp )
              if bMRotX:                       
                dxEngine.rotX( (self.MDY/2000.)*speedUp )
                
              bMLeft = m[0]>0 and m[0]<40 #and ms.x >= rc.x
              bMRight = m[0]> rc.width-40 #and ms.x <= rc.x + rc.width
              bMTop = m[1]>0 and m[1] < 40# and ms.y >= rc.y + 10
              bMDown = m[1]>rc.height-40 # and ms.y <= rc.y + rc.height
              if self.bUseScroll == False:
                bMLeft = bMRight = bMTop = bMDown = False
              
              recalcMouse = False
              if bMLeft or self.strafe==-1:
                recalcMouse = True
                if ms.controlDown or ms.middleDown:                  
                  dxEngine.rotY( .002*speedUp )
                else:
                  dxEngine.strafe(-12*speedUp)
              if bMRight or self.strafe==1:
                recalcMouse = True
                if ms.controlDown or ms.middleDown:
                  dxEngine.rotY( -.002*speedUp )
                else:
                  dxEngine.strafe(12*speedUp)
              if bMTop or self.move == 1:
                recalcMouse = True
                if ms.controlDown or ms.middleDown:
                  dxEngine.rotX( .002*speedUp )
                else:        
                  dxEngine.move(12*speedUp)
              if bMDown or self.move ==-1:
                recalcMouse = True
                if ms.controlDown or ms.middleDown:
                  dxEngine.rotX( -.002*speedUp )
                else:        
                  dxEngine.move(-12*speedUp)
              if self.up == 1:
                recalcMouse = True
                dxEngine.moveUp( 12*speedUp )            
              if self.up == -1:
                recalcMouse = True
                dxEngine.moveUp( -12*speedUp )            

              if recalcMouse:
                self.umX,self.umY = dxEngine.getCoordUnderMouse( m[0], m[1] )
                if self.umX < 0:
                  self.umX = 0
                if self.umY < 0:
                  self.umY = 0
                if self.umX >= self.region.height.shape[1]:
                  self.umX = self.region.height.shape[1]-1
                if self.umY >= self.region.height.shape[0]:
                  self.umY = self.region.height.shape[0]-1
                
              try:
                height = self.region.height[ self.umY, self.umX ]
                self.sb.SetStatusText( "x:%d y:%d height:%.02fm"%( self.umX, self.umY, height ), 2 )          
              except:
                print self.umY, self.umX
            
                
        #print'udpate engine',                
        dxEngine.update( self.umX, self.umY, self.bRenderWater  )        
        #print 'ok'
        self.oldMX = ms.x
        self.oldMY = ms.y
        print '.',
        self.timer.Start(33)


class SplashScreen(wx.SplashScreen):
    def __init__(self):
        bmp = wx.Image("splash.jpg",wx.BITMAP_TYPE_JPEG).ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                 1000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, evt):
        evt.Skip()
        self.Hide()
        # if the timer is still running then go ahead and show the
        # main frame now
        self.ShowMain()

    def ShowMain(self):
        frame = SC4Frame(None,-1, "SC4Terraformer")
        frame.Show()
        

class SC4App( wx.App ):
    def OnInit( self ):
        splash = SplashScreen()
        splash.Show()
        return True


def main():
    try:
        mainPath = sys.path[0]
        os.chdir(mainPath)
    except:
        pass
    global config 
    config = Configurator()        
    app = SC4App( False )
    app.MainLoop()

#ReadCLR()
main()



