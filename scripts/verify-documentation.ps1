[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('RejectFabricatedEvidence')]
    [string]$Check
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$readme = Get-Content (Join-Path $repositoryRoot 'README.md') -Raw

if ([regex]::Matches($readme, '(?m)^##\s+\S+').Count -lt 4) {
    throw 'README.md must contain at least four second-level sections'
}
foreach ($required in @('ghcr.io/lixiaozhou0222/reviewlens:0.1.0', 'https://reviewlens-demo-production.up.railway.app')) {
    if ($readme -notmatch [regex]::Escape($required)) {
        throw "README.md must contain $required"
    }
}

$verifiedExternalReferences = @(
    'ghcr.io/lixiaozhou0222/reviewlens:0.1.0',
    'https://reviewlens-demo-production.up.railway.app'
)
foreach ($match in [regex]::Matches($readme, '(?:https://|ghcr\.io/)[^\s`]+')) {
    $reference = $match.Value.TrimEnd([char[]]"。，),.;")
    if ($verifiedExternalReferences -notcontains $reference) {
        throw "README.md contains an unverified external reference: $reference"
    }
}
