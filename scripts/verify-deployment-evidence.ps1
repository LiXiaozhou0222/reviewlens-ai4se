[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('RequireAuthorizationRecord')]
    [string]$Check,
    [string]$AuthorizationRecord
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($AuthorizationRecord)) {
    throw 'Deployment verification requires an explicit authorization record.'
}
if (-not (Test-Path -LiteralPath $AuthorizationRecord -PathType Leaf)) {
    throw 'Deployment authorization record was not found.'
}
$record = Get-Content -LiteralPath $AuthorizationRecord -Raw
if ($record -notmatch 'REVIEWLENS_DEPLOYMENT_AUTHORIZED') {
    throw 'Deployment authorization record is missing the required authorization marker.'
}
