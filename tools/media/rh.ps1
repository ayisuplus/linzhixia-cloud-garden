# Project-local launcher for the unmodified official RunningHub CLI.
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$runtime = Join-Path $projectRoot '.venv-media/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $runtime)) {
    throw 'Missing .venv-media. See tools/media/README.md for setup.'
}
$previousOutput = $env:RH_OUTPUT_DIR
$previousEncoding = $env:PYTHONIOENCODING
try {
    if (-not $env:RH_OUTPUT_DIR) {
        $env:RH_OUTPUT_DIR = Join-Path $projectRoot '视频制作/生成结果/RunningHub'
    }
    $env:PYTHONIOENCODING = 'utf-8'
    & $runtime -m rh_cli @args
    $result = $LASTEXITCODE
} finally {
    $env:RH_OUTPUT_DIR = $previousOutput
    $env:PYTHONIOENCODING = $previousEncoding
}
exit $result
