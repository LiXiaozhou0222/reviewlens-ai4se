[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('RejectFabricatedEvidence')]
    [string]$Check
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$readme = Get-Content (Join-Path $repositoryRoot 'README.md') -Raw

foreach ($required in @('## 安装', '## 运行', '## 安全边界', '## 已知限制', '尚未产生')) {
    if ($readme -notmatch [regex]::Escape($required)) {
        throw "README.md must contain $required"
    }
}
foreach ($forbidden in @('ghcr.io/', 'https://')) {
    if ($readme -match [regex]::Escape($forbidden)) {
        throw "README.md must not claim an unverified external reference: $forbidden"
    }
}
