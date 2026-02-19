Dim objShell, objWMI, colProcesses, objProcess
Dim isRunning

' Check if the application is already running
isRunning = False
Set objWMI = GetObject("winmgmts:\\.\root\cimv2")
Set colProcesses = objWMI.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'pythonw.exe'")

For Each objProcess In colProcesses
    If InStr(objProcess.CommandLine, "run.py") > 0 Then
        isRunning = True
        Exit For
    End If
Next

Set objShell = CreateObject("WScript.Shell")

' Only start if not already running
If Not isRunning Then
    objShell.CurrentDirectory = "C:\Users\DELL\DED"
    objShell.Run "C:\Python314\pythonw.exe run.py", 0, False
    ' Wait for the server to start
    WScript.Sleep 3000
End If

' Open browser
objShell.Run "http://localhost:5000", 1, False

Set objShell = Nothing
Set colProcesses = Nothing
Set objWMI = Nothing

