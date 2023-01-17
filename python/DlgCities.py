"""
   here are defined all dialogs
"""
import wx                  
import sys
import os
from wx.lib.mixins.listctrl import CheckListCtrlMixin
import  wx.lib.imagebrowser    as  ib
import ImageDraw
import Image


class CompressorDlg( wx.Dialog ):
    def __init__( self, parent, minVal, maxVal ):
        pre = wx.PreDialog()
        pre.Create(parent, -1, "Compressor", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE)
        self.PostCreate(pre)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "min height will map to")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.minMap = wx.TextCtrl(self, -1, "%f"%minVal, size=(80,-1))
        box.Add(self.minMap, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "unchanged value")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.pivot = wx.TextCtrl(self, -1, "0", size=(80,-1))
        box.Add(self.pivot, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "max height will map to")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.maxMap = wx.TextCtrl(self, -1, "%f"%maxVal, size=(80,-1))
        box.Add(self.maxMap, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        
        btnsizer = wx.StdDialogButtonSizer()
          
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
      

class CreateRegionDlg( wx.Dialog ):
    """ dialog that show up on region creation """
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
      pre = wx.PreDialog()
      pre.Create(parent, ID, title, pos, size, style)
      self.PostCreate(pre)
      
      sizer = wx.BoxSizer(wx.VERTICAL)
    
      box = wx.BoxSizer(wx.HORIZONTAL)
      label = wx.StaticText(self, -1, "Region name")
      box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      self.regionName = wx.TextCtrl(self, -1, "", size=(80,-1))
      box.Add(self.regionName, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

      sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

      line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
      sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        
      box = wx.BoxSizer(wx.HORIZONTAL)
      label = wx.StaticText(self, -1, "You can either specify a size for the region\nor specify a SC4M file made with v1.0b or greater")
      box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
      
      line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
      sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
    
      box = wx.BoxSizer(wx.HORIZONTAL)
  
      label = wx.StaticText(self, -1, "Width ( how many small cities ):")
      box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      self.width = wx.TextCtrl(self, -1, "16", size=(80,-1))
      box.Add(self.width, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
  
      box = wx.BoxSizer(wx.HORIZONTAL)
  
      label = wx.StaticText(self, -1, "Height ( how many small cities ):")
      box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      self.height = wx.TextCtrl(self, -1, "16", size=(80,-1))
      box.Add(self.height, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

      line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
      sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
      
      box = wx.BoxSizer(wx.HORIZONTAL)
      label = wx.StaticText(self, -1, "SC4M file")
      box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    
      self.imagePath = wx.TextCtrl(self, -1, "", size=(80,-1))
      box.Add(self.imagePath, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
    
      b = wx.Button(self, -1, "...",size=(20,-1))
      box.Add(b, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
      self.Bind(wx.EVT_BUTTON, self.OnButton, b)
      sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)  
  
      line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
      sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
  
      btnsizer = wx.StdDialogButtonSizer()
          
      btn = wx.Button(self, wx.ID_OK)
      btn.SetDefault()
      btnsizer.AddButton(btn)
  
      btn = wx.Button(self, wx.ID_CANCEL)
      btnsizer.AddButton(btn)
      btnsizer.Realize()
  
      sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
  
      self.SetSizer(sizer)
      sizer.Fit(self)
        
    def OnButton( self, event ):
        dlg = wx.FileDialog(
            self, message="Choose a SC4M file", defaultDir=os.getcwd(), 
            defaultFile="", wildcard= "SC4Terraform exported (*.SC4M)|*.SC4M"
            , style=wx.OPEN  
            )
        if dlg.ShowModal() == wx.ID_OK:
          paths = dlg.GetPaths()
          self.imagePath.SetValue( paths[0] )
        dlg.Destroy()
  
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin):
    """ the class that handle the checking in the lock/unlock city dialog """
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT,size=(320,150))
        CheckListCtrlMixin.__init__(self)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.region = parent.region
        self.parent = parent


    def OnItemActivated(self, evt):
        self.ToggleItem(evt.m_itemIndex)


    def OnItemSelected( self, evt ):
      currentItem = evt.m_itemIndex
      if self.parent.bitmap :
        data = self.GetItemData(currentItem)
        #we should rebuild the bitmap to reflect the change
        self.parent.bitmap.SetBitmap(self.parent.RebuildConfig(self.region.allCities[ data ])) 
      
    # this is called by the base class when an item is checked/unchecked
    def OnCheckItem(self, index, flag):
        data = self.GetItemData(index)
        if flag:
            print self.region.allCities[ data ].cityName,  "checked"
            self.region.allCities[ data ].Protected( True )
        else:
            print self.region.allCities[ data ].cityName,  "unchecked"
            self.region.allCities[ data ].Protected( False )
                    
        if self.parent.bitmap :
          #we should rebuild the bitmap to reflect the change
          self.parent.bitmap.SetBitmap(self.parent.RebuildConfig()) 

        
class ReportCitiesDialog(wx.Dialog):
    """ this is the dialog where the user can lock/unlock cities to protect them from terraforming """
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
        self.region = parent.region
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        
        self.bitmap = None
        bmp = self.RebuildConfig()

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        label = wx.StaticText(self, -1, "Check the city you don't want to terraform on")
        sizer.Add(label, 0, wx.ALIGN_CENTRE)
        if 0:
          label = wx.StaticText(self, -1, "WARNING:")
          sizer.Add(label, 0, wx.ALIGN_CENTRE)
          label = wx.StaticText(self, -1, "The information shown about Trees is not 100% right for now")
          sizer.Add(label, 0, wx.ALIGN_CENTRE)
          label = wx.StaticText(self, -1, "Sometimes it report trees but there aren't")
          sizer.Add(label, 0, wx.ALIGN_CENTRE)
          label = wx.StaticText(self, -1, "If it report no trees it seems to be right for now")
          sizer.Add(label, 0, wx.ALIGN_CENTRE)
        
        box = wx.BoxSizer(wx.VERTICAL)
        
        if bmp:
          self.bitmap = wx.StaticBitmap(self, -1, bmp, size=(bmp.GetWidth(), bmp.GetHeight()))
          sizer.Add(self.bitmap, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        
        self.list = CheckListCtrl(self )        
        
        self.list.InsertColumn(0, "City name")
        self.list.InsertColumn(1, "Trees planted")
        self.list.InsertColumn(2, "Mayor mod")
        for i,city in enumerate( self.region.allCities ):
            index = self.list.InsertStringItem(sys.maxint, city.cityName)
            mm = "no"
            ht = "no"
            if city.InMayorMod():
                mm = "yes"
            if city.HaveTrees():
                ht = "yes"
            self.list.SetStringItem(index, 1, ht)
            self.list.SetStringItem(index, 2, mm)
            self.list.SetItemData(index, i)
            if city.IsProtected():
                self.list.CheckItem(index)

        self.list.SetColumnWidth(0, 300-(90+70)-4)
        self.list.SetColumnWidth(1, 90)
        self.list.SetColumnWidth(2, 70)

        #box.Add(self.list, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        box.Add( self.list, 1, wx.EXPAND|wx.ALIGN_CENTRE )
        
        sizer.Add( box, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        box = wx.BoxSizer( wx.HORIZONTAL )
        btn = wx.Button(self, -1, "Unprotect all")
        self.Bind(wx.EVT_BUTTON, self.Unprotect, btn)
        box.Add( btn )
        btn = wx.Button(self, -1, "Protect trees")
        self.Bind(wx.EVT_BUTTON, self.ProtectTrees, btn)
        box.Add( btn )
        btn = wx.Button(self, -1, "Protect mayor")
        self.Bind(wx.EVT_BUTTON, self.ProtectMayor, btn)
        box.Add( btn )
        sizer.Add( box, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        self.SetSizer(sizer)
        self.Fit()
        #self.SetAutoLayout(1)
        
    def Unprotect( self, evt ):
      for i,city in enumerate( self.region.allCities ):
        if self.list.IsChecked( i ):
          self.list.ToggleItem( i )
        city.Protected( False )
      if self.bitmap :
        self.bitmap.SetBitmap(self.RebuildConfig()) 

    def ProtectTrees( self, evt ):
      for i,city in enumerate( self.region.allCities ):
        if city.HaveTrees():
          if not self.list.IsChecked( i ):
            self.list.ToggleItem( i )
          city.Protected( True )
      if self.bitmap :
        self.bitmap.SetBitmap(self.RebuildConfig()) 

    def ProtectMayor( self, evt ):
      for i,city in enumerate( self.region.allCities ):
        if city.InMayorMod():
          if not self.list.IsChecked( i ):
            self.list.ToggleItem( i )
          city.Protected( True )
      if self.bitmap :
        self.bitmap.SetBitmap(self.RebuildConfig()) 
              
    def  RebuildConfig( self, selectedCity = None ):
        bmp = None
        if self.region.config:
          ratio = float(self.region.config.size[0])/float(self.region.config.size[1])
          if ratio >= 1.:
            scaleX = 200
            
            scaleY = scaleX/ratio
          else:
            scaleY = 200
            scaleX = scaleY/ratio
          fX = float(scaleX)/float(self.region.config.size[0])
          fY = float(scaleY)/float(self.region.config.size[1])
          scaleX = int(scaleX)
          scaleY = int(scaleY)
          config = self.region.config.resize( (scaleX, scaleY) )
          draw = ImageDraw.Draw(config)
          for city in self.region.allCities:
            if city == selectedCity:
              x = city.cityXPos
              y = city.cityYPos
              x1 = x + city.cityXSize
              y1 = y + city.cityYSize
              draw.rectangle( [ (x*fX,y*fY),(x1*fX,y1*fY) ], fill = "#FFFF00" )
            if city.IsProtected():
              x = city.cityXPos
              y = city.cityYPos
              x1 = x + city.cityXSize
              y1 = y + city.cityYSize
              draw.line( [ (x*fX,y*fY), (x1*fX,y1*fY)], fill="#FFFFFF" )              
              draw.line( [ (x*fX,y1*fY), (x1*fX,y*fY)], fill="#FFFFFF" )
          img = wx.EmptyImage( config.size[0],config.size[1] )
          img.SetData( config.tostring() )
          bmp = wx.BitmapFromImage( img )
        return bmp      

class ImportImgDlg(wx.Dialog):
  """ Dialog for importing a image or SC4M file """
  def __init__( self, parent, ID, title, scaleFactor, minHeight, size=wx.DefaultSize, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE ):
    pre = wx.PreDialog()
    pre.Create(parent, ID, title, pos, size, style)
    self.PostCreate(pre)
    
    sizer = wx.BoxSizer(wx.VERTICAL)

    box = wx.BoxSizer(wx.HORIZONTAL)

    label = wx.StaticText(self, -1, "Image")
    box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

    self.imagePath = wx.TextCtrl(self, -1, "", size=(80,-1))
    box.Add(self.imagePath, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

    b = wx.Button(self, -1, "...",size=(20,-1))
    box.Add(b, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    self.Bind(wx.EVT_BUTTON, self.OnButton, b)

    sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

    box = wx.BoxSizer(wx.HORIZONTAL)

    label = wx.StaticText(self, -1, "Scale factor:")
    box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

    #self.imageFactor = wx.TextCtrl(self, -1, str(scaleFactor), size=(80,-1))
    self.imageFactor = wx.ComboBox( self, -1, "Default factor", style = wx.CB_DROPDOWN )
    scaleTable = [ "100m","250m","500m","Default factor", "1000m", "1500m", "2000m", "import.dat","2500m","3000m","3500m","4000m","4500m","5000m" ]
    for s in scaleTable:
      self.imageFactor.Append( s )
    
    box.Add(self.imageFactor, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

    sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

    if 0:
      box = wx.BoxSizer(wx.HORIZONTAL)
  
      label = wx.StaticText(self, -1, "Min height:")
      box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      self.imageHeight = wx.TextCtrl(self, -1, str(minHeight), size=(80,-1))
      box.Add(self.imageHeight, 1, wx.ALIGN_CENTRE|wx.ALL, 5)
  
      sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

    line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
    sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

    btnsizer = wx.StdDialogButtonSizer()
        
    btn = wx.Button(self, wx.ID_OK)
    btn.SetDefault()
    btnsizer.AddButton(btn)

    btn = wx.Button(self, wx.ID_CANCEL)
    btnsizer.AddButton(btn)
    btnsizer.Realize()

    sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

    self.SetSizer(sizer)
    sizer.Fit(self)
    
  def OnButton( self, event ):
    dlg = wx.FileDialog(
        self, message="Choose an image", defaultDir=os.getcwd(), 
        defaultFile="", wildcard= "All graphics file |*.SC4M;*.jpeg;*.jpg;*.png;*.bmp;*.ter|""SC4Terraform exported (*.SC4M)|*.SC4M|""Jpeg file (*.jpeg;*.jpg)|*.jpeg;*.jpg|""Bitmap file (*.bmp)|*.bmp|""Terragen file (*.ter)|*.ter|""All files (*.*)|*.*"
        , style=wx.OPEN  
        )
    if dlg.ShowModal() == wx.ID_OK:
      paths = dlg.GetPaths()
      self.imagePath.SetValue( paths[0] )
    dlg.Destroy()
    
  def GetImageName( self ):
    return self.imagePath.GetValue()
    
  def GetImageFactor( self ):
    s = self.imageFactor.GetValue()
    scales = { "100m" : 1.3725 ,"250m":1.9608 ,"500m":2.9412 ,"Default factor":3., "1000m":4.9020, "1500m":6.8627, "2000m":8.8235, "import.dat":9.7832,"2500m":10.7843,"3000m":12.7451,"3500m":14.7059,"4000m":16.6667,"4500m":18.6275,"5000m":20.5882 }
    if s in scales.keys():
      return scales[s]
    try:
      return float( s )
    except:
      return 3.
    
  def GetMinHeight( self ):
    return 0 #float( self.imageHeight.GetValue() )