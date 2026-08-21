#define MyAppName "BALI SPACE EXPERIENCE"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "BALI"
#define MyAppExeName "BALI_SPACE_EXPERIENCE.exe"

[Setup]
AppId={{B33B13FD-ED5F-4FF0-9BD6-BALI00000001}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\BALI Space Experience
DefaultGroupName=BALI Space Experience
OutputDir=installer_output
OutputBaseFilename=BALI_SPACE_EXPERIENCE_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\BALI Space Experience"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\BALI Space Experience"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch BALI SPACE EXPERIENCE"; Flags: nowait postinstall skipifsilent
