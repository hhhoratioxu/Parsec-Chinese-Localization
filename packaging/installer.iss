#define AppVersion "0.1.0"
[Setup]
AppId={{D9486059-2586-45A3-91C0-680B5E69B6D7}
AppName=Parsec Chinese Localization
AppVersion={#AppVersion}
AppPublisher=hhhoratioxu
AppPublisherURL=https://github.com/hhhoratioxu/Parsec-Chinese-Localization
DefaultDirName={localappdata}\Programs\ParsecChineseLocalization
DefaultGroupName=Parsec Chinese Localization
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\release
OutputBaseFilename=ParsecChineseLocalization-0.1.0-windows-x64-setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\ParsecChineseLocalization.exe
LicenseFile=..\LICENSE
CloseApplications=yes
RestartApplications=no

[Files]
Source: "..\dist\ParsecChineseLocalization\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Parsec Chinese Localization"; Filename: "{app}\ParsecChineseLocalization.exe"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[UninstallDelete]
; Exact files only. Never remove a Parsec directory or another user's files.
Type: files; Name: "{localappdata}\ParsecChineseLocalization\preferences.json"; Check: RemovePreferences
Type: files; Name: "{localappdata}\ParsecChineseLocalization\preferences.backup.json"; Check: RemovePreferences
Type: files; Name: "{localappdata}\ParsecChineseLocalization\events.log"; Check: RemovePreferences

[Code]
function RemovePreferences: Boolean;
var
  I: Integer;
begin
  Result := True;
  for I := 1 to ParamCount do
    if CompareText(ParamStr(I), '/KEEPPREFERENCES') = 0 then
      Result := False;
end;
