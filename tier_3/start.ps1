param(
    [int]$player_num,
    [string]$replay_flag,
    [int]$visibility_radius
)

$workdir = "judge/"
$config_file = "$workdir/sample_config.json"
$bots_dir = "bot/"
$replay_arg = " "

if ($player_num -le 0) {
    Write-Host "No player number given! Example usage: .\start.ps1 <player_number>"
    exit -1
}

Write-Host "starting judge with $player_num players..."

if ($replay_flag -eq "--replay") {
    $replay_arg = "--replay_file ./last_replay1"
}else{
    $replay_flag = ""
}

Start-Process -FilePath "python" -ArgumentList "$($workdir)run.py", $config_file, $player_num, $replay_arg -NoNewWindow

Start-Sleep -Seconds 3
Write-Host "starting players"

Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/winnerBot/bot.py" -NoNewWindow
'''Start-Sleep -Seconds 1
Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/winnerBot/bot.py" -NoNewWindow
Start-Sleep -Seconds 1
Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/winnerBot/bot.py" -NoNewWindow
Start-Sleep -Seconds 1
Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/winnerBot/bot.py" -NoNewWindow
Start-Sleep -Seconds 1'''
#Start-Process -FilePath "python" -ArgumentList "$($bots_dir)client_bridge.py", "bot/lieutenant_crown_him_with_many_crowns_thy_full_gallant_legions_he_found_it_in_him_to_forgive.py" -NoNewWindow


# Wait for judge process to complete
Get-Process python | Wait-Process

if (-not $replay_arg) {
    exit 0
}

Write-Host "Race complete!"
$last_log = "last_replay1"
Write-Host $last_log
python visualisation.py $last_log --visibility_radius $visibility_radius

