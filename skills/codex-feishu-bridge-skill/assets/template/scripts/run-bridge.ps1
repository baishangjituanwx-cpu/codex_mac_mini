$ErrorActionPreference = "Stop"
$Root = "__INSTALL_DIR__"
Set-Location $Root

$EnvFile = Join-Path $Root ".bridge.env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ([string]::IsNullOrWhiteSpace($_)) { return }
        if ($_.StartsWith("#")) { return }
        $pair = $_ -split "=", 2
        if ($pair.Count -ne 2) { return }
        $name = $pair[0].Trim()
        $value = $pair[1].Trim()
        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    $fallbacks = @(
        "C:\Program Files\nodejs\node.exe",
        "C:\Program Files (x86)\nodejs\node.exe"
    )
    foreach ($candidate in $fallbacks) {
        if (Test-Path $candidate) {
            $node = @{ Source = $candidate }
            break
        }
    }
}

if (-not $node) {
    throw "node not found on PATH and common install locations are missing"
}

& $node.Source "src/bridge.js"
exit $LASTEXITCODE
