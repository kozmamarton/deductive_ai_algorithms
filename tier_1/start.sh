#!/bin/bash

workdir="judge/"
config_file=$workdir"sample_config.json"
player_num=$1
bots_dir="bot/"

if  ! [[ $player_num -gt 0 ]]; then
  echo "No player number given! Example usage: ./start.sh <player_number>"
  exit -1
fi

echo "starting judge with $player_num players..."

python3 $workdir"run.py" $config_file $player_num &

echo "starting player 1"

python3 $bots_dir"client_bridge.py" "bot/naive_astar_no_speed.py" &


wait



