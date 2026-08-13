[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('DockerfileExcludesSecrets')]
    [string]$Check
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot

function Assert-DockerignoreContains([string]$pattern) {
    $dockerignore = Get-Content (Join-Path $repositoryRoot '.dockerignore')
    if ($dockerignore -notcontains $pattern) {
        throw ".dockerignore must exclude $pattern"
    }
}

function Test-DockerfileExcludesSecrets {
    $dockerfile = Get-Content (Join-Path $repositoryRoot 'Dockerfile') -Raw
    foreach ($pattern in @('.env', '.env.*', 'secrets/', '*.key', '*.pem', 'credential-vault*', 'data/', 'logs/', 'apps/api/tests/')) {
        Assert-DockerignoreContains $pattern
    }

    foreach ($unsafeCopy in @('COPY . ', 'COPY ./', 'ADD . ')) {
        if ($dockerfile -match [regex]::Escape($unsafeCopy)) {
            throw "Dockerfile must not copy the whole build context: $unsafeCopy"
        }
    }
}

switch ($Check) {
    'DockerfileExcludesSecrets' { Test-DockerfileExcludesSecrets }
}
