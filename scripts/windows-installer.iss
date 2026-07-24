#define AppName "Performance Cockpit"
#define AppVersion "1.0.3"
#define AppPublisher "xerbooo-ops"
#define AppExeName "PerformanceCockpit.exe"

[Setup]
AppId={{A9BC73D3-7976-4782-A7DF-3D19F82A9480}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\PerformanceCockpit
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=PerformanceCockpit_v1.0.3_Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesAllowed=x64compatible

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Files]
Source: "..\backend\dist\PerformanceCockpit.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\data\sample_kpi_measurements.csv"; DestDir: "{app}\Beispieldaten"; Flags: ignoreversion
Source: "..\docs\windows-standalone.md"; DestDir: "{app}"; DestName: "HILFE.txt"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknüpfung erstellen"; GroupDescription: "Zusätzliche Verknüpfungen:"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{#AppName} starten"; Flags: nowait postinstall skipifsilent
