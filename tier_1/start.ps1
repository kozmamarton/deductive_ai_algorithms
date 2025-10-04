param(
    [int]$player_num,
    [string]$replay_flag
)

$workdir = "judge/"
$config_file = "$workdir/sample_config.json"
$bots_dir = "bot/"
$replay_arg = ""

if ($player_num -le 0) {
    Write-Host "No player number given! Example usage: .\start.ps1 <player_number>"
    exit -1
}

Write-Host "starting judge with $player_num players..."

if ($replay_flag -eq "--replay") {
    $replay_arg = "--replay_file ./last_replay"
}

Start-Process -FilePath "python" -ArgumentList "$($workdir)run.py", $config_file, $player_num, $replay_arg -NoNewWindow

Start-Sleep -Seconds 3
Write-Host "starting players"

Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/foreign_competitors/bot.py" -NoNewWindow
Start-Sleep -Seconds 1
Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/winnerBot/bot.py" -NoNewWindow
Start-Sleep -Seconds 1
Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/foreign_competitors/my_bot.py" -NoNewWindow
Start-Sleep -Seconds 1
Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/foreign_competitors/mybot2.0.py" -NoNewWindow


# Wait for judge process to complete
Get-Process python | Wait-Process

if (-not $replay_arg) {
    exit 0
}

Write-Host "Race complete!"
$last_log = "last_replay"
Write-Host $last_log
python visualisation.py $last_log

