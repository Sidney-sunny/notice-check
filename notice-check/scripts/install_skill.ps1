param([string]$ProjectPath = (Get-Location).Path)
$ErrorActionPreference = 'Stop'
$source = Split-Path -Parent $PSScriptRoot
$project = [System.IO.Path]::GetFullPath($ProjectPath)
$target = Join-Path $project '.agents/skills/notice-check'
if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) { throw 'Source SKILL.md missing' }
if (Test-Path -LiteralPath $target) { throw "Existing installation retained: $target. Compare before manual update." }
New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
Copy-Item -LiteralPath $source -Destination $target -Recurse
Write-Output "Installed: $target"
