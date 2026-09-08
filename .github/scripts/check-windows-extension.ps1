# Issue #30: a Windows runtime check, with no authentication or model request.
# This does not uninstall the runner's Node.js. It isolates PATH and records every
# descendant process, including attempts to execute an external node.exe by path.
# Sources checked 2026-09-08:
# https://code.claude.com/docs/en/vs-code
# https://code.visualstudio.com/api/working-with-extensions/testing-extension
# https://update.code.visualstudio.com/api/update/win32-x64-archive/stable/latest
# https://open-vsx.org/api/Anthropic/claude-code/win32-x64/2.1.263
param([Parameter(Mandatory)][string]$WorkDirectory)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $IsWindows) { throw 'Run this check on Windows with PowerShell 7.' }

$workRoot = [IO.Path]::GetFullPath($WorkDirectory)
if (Test-Path $workRoot) { throw "Use a new working directory: $workRoot" }
$evidence = Join-Path $workRoot 'evidence'
$profileRoot = Join-Path $workRoot 'profile'
$userData = Join-Path $workRoot 'user-data'
$workspace = Join-Path $workRoot 'workspace'
$codeRoot = Join-Path $workRoot 'vscode'
$vsixRoot = Join-Path $workRoot 'vsix'
$extensionRoot = Join-Path $vsixRoot 'extension'
$eventSource = 'ClaudeExtensionProcessStarts'
$process = $null
$processEventsRegistered = $false
$summary = [ordered]@{
    success = $false
    scope = 'External node/npm/npx absent from PATH; no external node.exe in the VS Code process tree. The runner still contains Node.js outside PATH.'
    excluded = 'No user login, prompt submission, model response, or paid API request.'
    screenshotReview = 'Review claude-code-panel.png to confirm the sign-in UI rendered.'
}

function Write-JsonFile([string]$Name, $Value) {
    $destination = Join-Path $evidence $Name
    $Value | ConvertTo-Json -Depth 12 | Set-Content "$destination.tmp" -Encoding utf8NoBOM
    Move-Item "$destination.tmp" $destination -Force
}

function Get-VerifiedArchive([string]$Url, [string]$Hash, [string]$Destination) {
    Invoke-WebRequest -Uri $Url -OutFile $Destination
    $actualHash = (Get-FileHash $Destination -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -ne $Hash) { throw "SHA256 mismatch for $Url" }
}

function Save-PanelScreenshot {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $bitmap = [System.Drawing.Bitmap]::new($bounds.Width, $bounds.Height)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
        $bitmap.Save((Join-Path $evidence 'claude-code-panel.png'), [System.Drawing.Imaging.ImageFormat]::Png)
    } finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
}

New-Item -ItemType Directory -Path $evidence, $profileRoot, $workspace, (Join-Path $userData 'User') | Out-Null

try {
    $sources = [ordered]@{
        checkedAt = '2026-09-08'
        vscode = @{
            version = '1.136.1'
            commit = 'a44adf7f53e00964ab890f9f8758a334f1fc15bc'
            url = 'https://vscode.download.prss.microsoft.com/dbazure/download/stable/a44adf7f53e00964ab890f9f8758a334f1fc15bc/VSCode-win32-x64-1.136.1.zip'
            sha256 = 'deca16ea5c4d71ece23e50af57632bba3abd0e3577c3c8bfbcdd90b03f11e402'
        }
        claudeExtension = @{
            version = '2.1.263'
            platform = 'win32-x64'
            url = 'https://open-vsx.org/api/Anthropic/claude-code/win32-x64/2.1.263/file/Anthropic.claude-code-2.1.263@win32-x64.vsix'
            sha256 = '91ff4ceae3483d0d9142c0f29bb25e5b36b07f116e09392c78739fdb74e551ed'
        }
    }
    Write-JsonFile 'sources.json' $sources
    Write-JsonFile 'runner.json' @{
        os = [Environment]::OSVersion.VersionString
        image = $env:ImageOS
        imageVersion = $env:ImageVersion
        powershell = $PSVersionTable.PSVersion.ToString()
    }
    Get-VerifiedArchive $sources.vscode.url $sources.vscode.sha256 (Join-Path $workRoot 'vscode.zip')
    Get-VerifiedArchive $sources.claudeExtension.url $sources.claudeExtension.sha256 (Join-Path $workRoot 'claude.zip')
    Expand-Archive (Join-Path $workRoot 'vscode.zip') $codeRoot
    Expand-Archive (Join-Path $workRoot 'claude.zip') $vsixRoot
    Copy-Item (Join-Path $extensionRoot 'package.json') (Join-Path $evidence 'extension-package.json')
    $manifest = Get-Content (Join-Path $extensionRoot 'package.json') -Raw | ConvertFrom-Json
    if ($manifest.version -ne $sources.claudeExtension.version) { throw 'Unexpected VSIX version.' }

    # Only editor preferences are changed. No Claude process wrapper is configured.
    @{
        'telemetry.telemetryLevel' = 'off'
        'update.mode' = 'none'
        'extensions.autoUpdate' = $false
        'extensions.autoCheckUpdates' = $false
        'security.workspace.trust.enabled' = $false
        'workbench.startupEditor' = 'none'
        'workbench.colorTheme' = 'Default Light Modern'
        'window.newWindowDimensions' = 'maximized'
    } | ConvertTo-Json | Set-Content (Join-Path $userData 'User/settings.json') -Encoding utf8NoBOM

    # Construct the child environment explicitly; no GitHub or user credentials are inherited.
    # ProcessStartInfo avoids Start-Process -Environment appending the machine PATH.
    $startInfo = [Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = Join-Path $codeRoot 'Code.exe'
    $startInfo.WorkingDirectory = $workspace
    $startInfo.UseShellExecute = $false
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.Environment.Clear()
    foreach ($name in @('SystemRoot', 'WINDIR', 'SystemDrive', 'COMSPEC', 'PATHEXT', 'PROCESSOR_ARCHITECTURE', 'NUMBER_OF_PROCESSORS')) {
        $value = [Environment]::GetEnvironmentVariable($name)
        if ($null -ne $value) { $startInfo.Environment[$name] = $value }
    }
    $childPath = @(
        (Join-Path $env:SystemRoot 'System32'),
        $env:SystemRoot,
        (Join-Path $env:SystemRoot 'System32/WindowsPowerShell/v1.0'),
        'C:\Program Files\Git\cmd',
        'C:\Program Files\Git\bin'
    ) -join ';'
    $childVariables = @{
        PATH = $childPath
        USERPROFILE = $profileRoot
        APPDATA = (Join-Path $profileRoot 'AppData/Roaming')
        LOCALAPPDATA = (Join-Path $profileRoot 'AppData/Local')
        TEMP = (Join-Path $workRoot 'temp')
        TMP = (Join-Path $workRoot 'temp')
        CLAUDE_CONFIG_DIR = (Join-Path $profileRoot '.claude')
        CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = '1'
        DISABLE_AUTOUPDATER = '1'
        WINDOWS_EXTENSION_EVIDENCE = $evidence
    }
    foreach ($name in $childVariables.Keys) { $startInfo.Environment[$name] = $childVariables[$name] }
    foreach ($name in @('APPDATA', 'LOCALAPPDATA', 'TEMP', 'CLAUDE_CONFIG_DIR')) {
        New-Item -ItemType Directory -Path $childVariables[$name] -Force | Out-Null
    }
    $launchArguments = @(
        $workspace,
        "--user-data-dir=$userData",
        "--extensions-dir=$(Join-Path $workRoot 'extensions')",
        "--extensionDevelopmentPath=$extensionRoot",
        "--extensionTestsPath=$(Join-Path $PSScriptRoot 'windows-extension-test.cjs')",
        '--disable-extensions',
        '--disable-workspace-trust',
        '--skip-welcome',
        '--skip-release-notes',
        '--disable-gpu',
        '--log=trace'
    )
    foreach ($argument in $launchArguments) { $startInfo.ArgumentList.Add($argument) }
    Write-JsonFile 'launch.json' @{
        executable = $startInfo.FileName
        arguments = $launchArguments
        environment = $childVariables
        note = 'VS Code supplies its own embedded Node runtime. No standalone Node is in the child PATH.'
    }

    # OS-level process-start events catch even short-lived absolute-path Node calls.
    Register-CimIndicationEvent -Namespace root/cimv2 -Query 'SELECT * FROM Win32_ProcessStartTrace' -SourceIdentifier $eventSource | Out-Null
    $processEventsRegistered = $true
    $process = [Diagnostics.Process]::Start($startInfo)
    $stdout = $process.StandardOutput.ReadToEndAsync()
    $stderr = $process.StandardError.ReadToEndAsync()
    $deadline = [DateTime]::UtcNow.AddSeconds(150)
    $captured = $false
    while (-not $process.HasExited -and [DateTime]::UtcNow -lt $deadline) {
        if (-not $captured -and (Test-Path (Join-Path $evidence 'capture-request.json'))) {
            try {
                Save-PanelScreenshot
                Write-JsonFile 'capture-result.json' @{ success = $true; capturedAt = [DateTime]::UtcNow.ToString('o') }
            } catch {
                Write-JsonFile 'capture-result.json' @{ success = $false; error = $_.Exception.Message }
            }
            $captured = $true
        }
        Start-Sleep -Milliseconds 200
    }
    $timedOut = -not $process.HasExited
    if ($timedOut) {
        $process.Kill($true)
        $process.WaitForExit()
    }
    $stdout.GetAwaiter().GetResult() | Set-Content (Join-Path $evidence 'vscode-stdout.log') -Encoding utf8NoBOM
    $stderr.GetAwaiter().GetResult() | Set-Content (Join-Path $evidence 'vscode-stderr.log') -Encoding utf8NoBOM
    # Allow event delivery to catch up before evaluating the process tree.
    Start-Sleep -Seconds 2
    $events = @(Get-Event -SourceIdentifier $eventSource -ErrorAction SilentlyContinue | ForEach-Object {
        $item = $_.SourceEventArgs.NewEvent
        [pscustomobject]@{
            processId = [int]$item.ProcessID
            parentProcessId = [int]$item.ParentProcessID
            name = [string]$item.ProcessName
            createdAt = [DateTime]::FromFileTimeUtc([long]$item.TIME_CREATED).ToString('o')
        }
    })
    $descendantIds = [Collections.Generic.HashSet[int]]::new()
    [void]$descendantIds.Add($process.Id)
    do {
        $added = $false
        foreach ($item in $events) {
            if ($descendantIds.Contains($item.parentProcessId) -and $descendantIds.Add($item.processId)) { $added = $true }
        }
    } while ($added)
    $descendants = @($events | Where-Object { $descendantIds.Contains($_.processId) } | Sort-Object createdAt)
    Write-JsonFile 'process-starts.json' @{ rootProcessId = $process.Id; descendants = $descendants }
    if ($timedOut) { throw 'VS Code extension tests timed out after 150 seconds.' }
    if (-not ($descendants | Where-Object { $_.name -ieq 'claude.exe' })) {
        throw 'Process recording did not observe the bundled CLI; absence of Node cannot be verified.'
    }
    if ($descendants | Where-Object { $_.name -ieq 'node.exe' }) {
        throw 'An external node.exe started in the VS Code process tree.'
    }
    $extensionResult = Get-Content (Join-Path $evidence 'extension-result.json') -Raw | ConvertFrom-Json
    if ($process.ExitCode -ne 0 -or -not $extensionResult.success) {
        throw "Extension startup check failed (VS Code exit $($process.ExitCode)). See extension-result.json and logs."
    }
    $summary.success = $true
    $summary.vscodeExitCode = $process.ExitCode
    $summary.externalNodeProcesses = 0
    $summary.recordedProcesses = $descendants.Count
    Write-Host 'PASS: extension activation, webview creation, native CLI, screenshot, and no external Node process.'
} catch {
    $summary.error = $_.Exception.Message
    throw
} finally {
    if ($null -ne $process -and -not $process.HasExited) { $process.Kill($true) }
    if ($processEventsRegistered) {
        Unregister-Event -SourceIdentifier $eventSource
        Get-Event -SourceIdentifier $eventSource -ErrorAction SilentlyContinue | Remove-Event
    }
    $logs = Join-Path $userData 'logs'
    if (Test-Path $logs) { Copy-Item $logs (Join-Path $evidence 'vscode-logs') -Recurse }
    Write-JsonFile 'summary.json' $summary
}
