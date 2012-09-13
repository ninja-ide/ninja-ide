;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;        Auto-Generated With py2Nsis
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME Ninja
!define PRODUCT_VERSION 2.1
!define PRODUCT_PUBLISHER 
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Ninja.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON ninja.ico
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!define MUI_WELCOMEPAGE_TITLE_3LINES
!insertmacro MUI_PAGE_WELCOME
; License page

; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_TITLE_3LINES

!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "Spanish"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "installer.exe"
InstallDir "$PROGRAMFILES\Ninja"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails hide
ShowUnInstDetails hide

Section "Principal" SEC01
    
  SetOutPath "$INSTDIR"

  File C:\\NINJA\\ninja-ide-2.1\\dist\\Ninja.exe
  File C:\\NINJA\\ninja-ide-2.1\\dist\\w9xpopen.exe
  
  SetOutPath $INSTDIR\\doc
  
  File /r C:\\NINJA\\ninja-ide-2.1\\dist\\doc\\* 
  
  SetOutPath $INSTDIR\\img
  
  File /r C:\\NINJA\\ninja-ide-2.1\\dist\\img\\* 
  
  SetOutPath $INSTDIR\\addins
  
  File /r C:\\NINJA\\ninja-ide-2.1\\dist\\addins\\* 
  
  SetOutPath "$INSTDIR"
  
SectionEnd

Section -AdditionalIcons
  CreateShortCut "$SMPROGRAMS\Ninja.lnk" "$INSTDIR\Ninja.exe"
  CreateShortCut "$DESKTOP\Ninja.lnk" "$INSTDIR\Ninja.exe"
  CreateShortCut "$SMPROGRAMS\Ninja\Desinstalar.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Ninja.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Ninja.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "La desinstalacion de $(^Name) finalizo satisfactoriamente."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Esta completamente seguro que desea desinstalar $(^Name) junto con todos sus componentes?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\*"

  Delete "$SMPROGRAMS\Ninja\Desinstalar.lnk"
  Delete "$DESKTOP\Ninja.lnk"
  Delete "$SMPROGRAMS\Ninja.lnk"
  
  Delete "$INSTDIR\*"
    
  RMDir "$SMPROGRAMS\Ninja"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
