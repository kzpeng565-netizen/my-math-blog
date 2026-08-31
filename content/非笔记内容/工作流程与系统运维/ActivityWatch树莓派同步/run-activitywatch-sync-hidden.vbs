Option Explicit
On Error Resume Next

Dim fileSystem, shell, scriptDirectory, syncScript, pythonw, command

Set fileSystem = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

scriptDirectory = fileSystem.GetParentFolderName(WScript.ScriptFullName)
syncScript = fileSystem.BuildPath(scriptDirectory, "push-activitywatch.pyw")
pythonw = "D:\anaconda\pythonw.exe"
command = """" & pythonw & """ """ & syncScript & """"

shell.Run command, 0, False
