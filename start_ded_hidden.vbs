Dim objShell, objWMI, colProcesses, objProcess
Dim isRunning, i

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
    ' Wait for server to be ready (check every second, up to 15 seconds)
    For i = 1 To 15
        WScript.Sleep 1000
        Dim objHTTP
        Set objHTTP = CreateObject("WinHttp.WinHttpRequest.5.1")
        On Error Resume Next
        objHTTP.Option(4) = 13056 ' Ignore SSL errors (self-signed cert)
        objHTTP.Open "GET", "https://localhost:5000", False
        objHTTP.SetTimeouts 500, 500, 1000, 1000
        objHTTP.Send
        If Err.Number = 0 Then
            Set objHTTP = Nothing
            Exit For
        End If
        On Error GoTo 0
        Set objHTTP = Nothing
    Next
Else
    ' Already running, just wait a moment
    WScript.Sleep 500
End If

' Open browser (HTTPS because Flask uses SSL certificates)
objShell.Run "https://localhost:5000", 1, False

Set objShell = Nothing
Set colProcesses = Nothing
Set objWMI = Nothing

