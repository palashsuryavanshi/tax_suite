; Tax Suite - Inno Setup installer script.
; Build:  ISCC.exe TaxSuite.iss
; Requires a one-dir PyInstaller build of gui_console.py (TaxSuiteGUI.spec)
; with Playwright chromium bundled under _internal\browsers.

#define MyAppName "Tax Suite"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "palashsuryavanshi"
#define MyAppExeName "TaxSuiteGUI.exe"

[Setup]
AppId={{A3F2B9C4-5D6E-4F7A-8B1C-2D3E4F5A6B7C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\TaxSuite
DisableProgramGroupPage=yes
PrivilegesRequired=admin
OutputDir=installer
OutputBaseFilename=TaxSuite-Setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (c) 2026 palashsuryavanshi

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Shortcuts:"
Name: "firewall"; Description: "Allow {#MyAppName} through Windows &Firewall (TCP port 5000)"; GroupDescription: "Permissions:"
Name: "autostart"; Description: "Start the web server automatically at &logon"; GroupDescription: "Startup:"

[Files]
Source: "dist\TaxSuiteGUI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "TaxSuite"; ValueData: """{app}\{#MyAppExeName}"" --serve"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "netsh.exe"; Parameters: "advfirewall firewall add rule name=""Tax Suite Web App"" dir=in action=allow protocol=TCP localport=5000 profile=private"; Flags: runhidden; Tasks: firewall
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName} now"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "netsh.exe"; Parameters: "advfirewall firewall delete rule name=""Tax Suite Web App"""; Flags: runhidden