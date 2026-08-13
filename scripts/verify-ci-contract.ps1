[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('GitHub', 'GitLab')]
    [string]$Provider
)

$ErrorActionPreference = 'Stop'
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$workflowPath = switch ($Provider) {
    'GitHub' { Join-Path $repositoryRoot '.github/workflows/test.yml' }
    'GitLab' { Join-Path $repositoryRoot '.gitlab-ci.yml' }
}
$workflow = Get-Content $workflowPath -Raw

foreach ($required in @('make test', 'APP_MODE: demo')) {
    if ($workflow -notmatch [regex]::Escape($required)) {
        throw "$Provider CI must contain $required"
    }
}
if ($workflow -match 'OPENAI_API_KEY') {
    throw "$Provider CI must not require a real OpenAI key"
}
if ($Provider -eq 'GitHub' -and $workflow -notmatch 'pull_request:') {
    throw 'GitHub CI must run for pull requests'
}
if ($Provider -eq 'GitLab' -and $workflow -notmatch 'unit-test:') {
    throw 'GitLab CI must contain the unit-test job'
}
