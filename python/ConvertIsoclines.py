import sys
import os
import wx                  
import wx.html
import wx.lib.wxpTag
import webbrowser

import Numeric
import Image
import ImageFilter
import ImageDraw
import tools3D
import PngImagePlugin
import JpegImagePlugin
import BmpImagePlugin
Image._initialized=2

htmlTxt = """
<html>
<body bgcolor="#ABCDEF">
<center>
<h4>ConvertIsoclines</H4>
</center>
This tool will convert a contour map to a greyscale image that you can use either in SC4Terraformer or in SimCity4<br><br>
The input image will be displayed stretched to fit the display, but the output will be the same size of the original<br><br>
It is recommended that the input image is stored as a greyscale image<br><br>
It is not recommended to use a jpeg file, because of its lossy compression scheme<br><br>
Contour lines should not have holes in them or the result will be unknown<br><br>
Iso2.bmp Iso3.bmp and Iso4.png are correct examples and can be found in the installation folder<br><br>
Isobad.bmp is a bad sample so you can spot the differences<br><br>
</body>
</html>
"""

class MyHtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)#,style=wx.NO_FULL_REPAINT_ON_RESIZE)

    def OnLinkClicked(self, linkinfo):
      webbrowser.open_new( linkinfo.GetHref() )

class ConvertDlg( wx.Dialog ):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=(10,10), 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
                
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        whole = wx.BoxSizer(wx.HORIZONTAL )
        html = MyHtmlWindow(self, -1, size=(200, 650))
        html.SetPage( htmlTxt )
        whole.Add(html, 0, wx.ALL, 5)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.bitmap = wx.StaticBitmap(self, -1, wx.EmptyBitmap(800,600,24 ), size=(800, 600))
        sizer.Add(self.bitmap, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        btnsizer = wx.BoxSizer(wx.HORIZONTAL)#wx.StdDialogButtonSizer()
            
        btn = wx.Button(self, -1,"Load")          
        btnsizer.Add(btn,0, wx.ALIGN_CENTRE|wx.ALL, 5)  
        self.Bind(wx.EVT_BUTTON, self.OnLoad, btn)

        btn = wx.Button(self, -1,"Generate")
        #btn.SetDefault()
        btnsizer.Add(btn,0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnGenerate, btn)
    
        btn = wx.Button(self, -1,"Save")
        btnsizer.Add(btn,0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.OnSave, btn)

        btn = wx.Button(self, wx.ID_OK,"Quit")
        btnsizer.Add(btn,0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        whole.Add( sizer, 0, wx.ALL, 5)
    
        self.SetSizer(whole)
        self.SetAutoLayout(True )
        whole.SetSizeHints(self)
        whole.Fit( self )
        
        
        self.fileName = None
        self.imageOk = None

    def OnSave( self, event ):
      if self.imageOk == None:
        return
      dlg = wx.FileDialog(
          self, message="Save file as ...", defaultDir=os.getcwd(), 
          defaultFile="", wildcard="PNG file (*.png)|*.png|""Jpeg file (*.jpeg;*.jpg)|*.jpeg;*.jpg|""Bitmap file (*.bmp)|*.bmp", style=wx.SAVE
          )
      if dlg.ShowModal() == wx.ID_OK:
        path = dlg.GetPath()
        self.imageOk.save( path )
                
    def OnGenerate( self, event ):
      if self.fileName == None:
        return
      self.imageOk = None
      im = Image.open( self.fileName )
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

      dlg = wx.ProgressDialog("Generating image",
                               "building distance map for level xxx",
                               maximum = len(values)+1,
                               parent=self,
                               style = 0 )
      
      distances = {}
      for i,val in enumerate( values ):
        print 'building distance map for',val
        dlg.Update( i, 'building distance map for level %d'%(val) )
        r = tools3D.buildDistanceMap( heights.shape, heights, val )
        distances[ val ] = r
        #r = Numeric.fromstring( r, Numeric.Float32 )
        #distances[ val ] = Numeric.reshape( r, heights.shape )
        #i = Image.fromstring( "F", (heights.shape[1],heights.shape[0]), distances[val])#convheightmap( heights.shape[1],heights.shape[0], distances[ val ] ) )
        #i.show()
        print 'ok'
      print 'building greyscale'
      dlg.Update( i+1, 'building greyscale image' )
      r = tools3D.useDistancesMap( distances, heights.shape )
      print 'ok'
      im = Image.fromstring( "L", (heights.shape[1],heights.shape[0]), r )
      im = im.filter(ImageFilter.BLUR)
      self.imageOk = im
      im = im.resize( (800,600 ) )
      im = im.convert( "RGB" )
      img = wx.EmptyImage( 800,600,24 )
      img.SetData( im.tostring() )
      bmp = wx.BitmapFromImage( img )
      self.bitmap.SetBitmap( bmp )
      dlg.Close()
      dlg.Destroy()        
      
        
    def OnLoad( self, event ):
        dlg = wx.FileDialog(
            self, message="Choose an image", defaultDir=os.getcwd(), 
            defaultFile="", wildcard= "Graphic file|*.png;*.jpg;*.jpeg;*bmp|""PNG file (*.png)|*.png|""Jpeg file (*.jpeg;*.jpg)|*.jpeg;*.jpg|""Bitmap file (*.bmp)|*.bmp|""All files (*.*)|*.*"
            , style=wx.OPEN  | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
          paths = dlg.GetPaths()          
          im = wx.Image( paths[0] )
          im.Rescale( 800, 600 )
          self.bitmap.SetBitmap( wx.BitmapFromImage( im ) )
          self.fileName = paths[0]
          self.imageOk = None
          
          #self.imagePath.SetValue( paths[0] )
        dlg.Destroy()
            
        
    
class ConvertApp( wx.App ):
    def OnInit( self ):
        dlg = ConvertDlg( None, -1,"Convert Isoclines Tools" )
        dlg.ShowModal()
        dlg.Destroy()
        return True



def main():
    try:
        mainPath = sys.path[0]
        os.chdir(mainPath)
    except:
        pass
    app = ConvertApp( False )
    app.MainLoop()

main()
