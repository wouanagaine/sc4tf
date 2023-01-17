; SC4Terraformer.nsi
;
; This script is based on example2.nsi, but it remember the directory, 
; has uninstall support and (optionally) installs start menu shortcuts.
;

;--------------------------------

; The name of the installer
Name "SC4Terraformer v1.0c"

; The file to write
OutFile "SetupSC4Terraformer10c.exe"

; The default installation directory
InstallDir $PROGRAMFILES\SC4Terraformer

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\SC4Terraformer" "Install_Dir"

;--------------------------------

; Pages
PageEx license
   LicenseText "Readme of v1.0c"
   LicenseData readme.txt
PageExEnd
Page components
Page directory
Page instfiles



UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "SC4Terraformer (required)"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File "dist\*.*"
  
  SetOutPath $INSTDIR\datas
  File "dist\datas\*.*"
  
  SetOutPath $INSTDIR\brushes
  File "dist\brushes\*.*"

  SetOutPath $INSTDIR\additionalfiles
  File "dist\additionalfiles\*.*"
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\SC4Terraformer "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SC4Terraformer" "DisplayName" "SC4Terraformer V1.0c"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SC4Terraformer" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SC4Terraformer" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SC4Terraformer" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\SC4Terraformer"
  CreateShortCut "$SMPROGRAMS\SC4Terraformer\Uninstall v1.0c.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$SMPROGRAMS\SC4Terraformer\SC4Terraformer Debug v1.0c.lnk" "$INSTDIR\SC4Terraformer_debug.exe" "" "$INSTDIR\SC4Terraformer_debug.exe" 0
  CreateShortCut "$SMPROGRAMS\SC4Terraformer\SC4Terraformer v1.0c.lnk" "$INSTDIR\SC4Terraformer.exe" "" "$INSTDIR\SC4Terraformer.exe" 0
  CreateShortCut "$SMPROGRAMS\SC4Terraformer\ConvertIsoclines v1.0c.lnk" "$INSTDIR\ConvertIsoclines.exe" "" "$INSTDIR\ConvertIsoclines.exe" 0
  CreateShortCut "$SMPROGRAMS\SC4Terraformer\SC4Terraformer v1.0c readme.lnk" "$INSTDIR\Readme.html" "" "$INSTDIR\Readme.html" 0
  
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SC4Terraformer"
  DeleteRegKey HKLM SOFTWARE\SC4Terraformer

  ; Remove files and uninstaller
  Delete $INSTDIR\*.*

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\SC4Terraformer\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\SC4Terraformer"
  RMDir "$INSTDIR"

SectionEnd
