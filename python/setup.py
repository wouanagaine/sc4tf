from distutils.core import setup
import py2exe

from distutils.core import setup
import py2exe
import sys
import dircache
import os

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-q")

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "0.09"
        self.company_name = "Wouanagaine"
        self.copyright = "Wouanagaine"
        self.name = "SC4Terraformer"

################################################################
# A program using wxPython

# The manifest will be inserted as resource into test_wx.exe.  This
# gives the controls the Windows XP appearance (if run on XP ;-)
#
# Another option would be to store it in a file named
# test_wx.exe.manifest, and copy it with the data_files option into
# the dist-dir.
#
manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24

test_sc4tc = Target(
    # used for the versioninfo resource
    description = "SC4Terraformer a tool for regional hand terraforming",
    # what to build
    script = "SC4Terraformer.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="SC4Terraformer_debug"))],
    icon_resources = [(1, "icon.ico")],
    dest_base = "SC4Terraformer_debug")

test_sc4tw = Target(
    # used for the versioninfo resource
    description = "SC4Terraformer a tool for regional hand terraforming",
    # what to build
    script = "SC4Terraformer.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="SC4Terraformer"))],
    icon_resources = [(1, "icon.ico")],
    dest_base = "SC4Terraformer")
    
test_iso = Target( 
    # used for the versioninfo resource
    description = "iso beta",
    # what to build
    script = "ioslines.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="ConvertIsoLine"))],
    icon_resources = [(1, "icon.ico")],
    dest_base = "ConvertIsoLine")
    
test_isow = Target( 
    # used for the versioninfo resource
    description = "isoclines beta",
    # what to build
    script = "ConvertIsoclines.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog="ConvertIsoclines"))],
    icon_resources = [(1, "icon.ico")],
    dest_base = "ConvertIsoclines")
    


################################################################

excludes = ["d3d8thk.dll","d3d9.dll","d3dx9_30.dll"]
includes = ["encodings",
            "encodings.*",]
            
brushesList = dircache.listdir( "brushes" )
brushesList = [ "brushes/%s"%(x) for x in brushesList if os.path.splitext( x )[1] == ".png" ]    

additionalList = dircache.listdir( "additionalfiles" )
additionalList = [ "additionalfiles/%s"%(x) for x in additionalList if os.path.isfile( "additionalfiles/%s"%(x) ) ]    

datasList= dircache.listdir( "datas" )
datasList = [ "datas/%s"%(x) for x in datasList if os.path.isfile( "datas/%s"%(x) ) ]    

setup(
    options = {"py2exe": {"compressed": 1,
                          "optimize": 2,
                          "dll_excludes":excludes,
                          "includes":includes,
                          "ascii": 1,
                          "bundle_files": 2}},
    #zipfile = None,
    console = [test_sc4tc],
    windows = [test_sc4tw, test_isow],
    
    data_files=[('.',[
                     'brushes.py'
                     ,'icon.ico'
                     ,'about.html'
                     ,'sc4.jpg'
                     ,'splash.jpg'
                     ,'readme.html'] ),
                  ('brushes', brushesList),
                  ('additionalfiles',additionalList ),
                  ('datas',datasList )
                  ]
    )


#setup( 
#  window={script="SC4Terraformer.py",icon_resources = [(1, "icon.ico")]},
  