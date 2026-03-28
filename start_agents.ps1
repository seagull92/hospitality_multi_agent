# start_agents.ps1
# Launches all 4 agent HTTP servers in separate terminal windows.
# Each runs as an independent langgraph dev server on its own port.
# After all 4 are ready, run: python main.py

$root = $PSScriptRoot

$agents = @(
    @{ name = "bi-agent";          dir = "agents\bi";          port = 8001 },
    @{ name = "media-agent";       dir = "agents\media";       port = 8002 },
    @{ name = "pricing-agent";     dir = "agents\pricing";     port = 8003 },
    @{ name = "coordinator-agent"; dir = "agents\coordinator"; port = 8004 }
)

foreach ($agent in $agents) {
    $agentDir = Join-Path $root $agent.dir
    $title    = "$($agent.name) :$($agent.port)"
    $cmd      = "Set-Location '$agentDir'; langgraph dev --port $($agent.port)"

    Write-Host "Starting $($agent.name) on port $($agent.port)..."
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd -WindowStyle Normal
}

Write-Host ""
Write-Host "All 4 agent servers starting. Wait for each to show 'Ready' then run:"
Write-Host "  python main.py"
