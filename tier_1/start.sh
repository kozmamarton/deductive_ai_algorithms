#!/bin/bash

workdir="judge/"
config_file=$workdir"sample_config.json"
player_num=$1
bots_dir="bot/"
replay_flag=$2
replay_arg=""


if  ! [[ $player_num -gt 0 ]]; then
  echo "No player number given! Example usage: ./start.sh <player_number>"
  exit -1
fi

echo "starting judge with $player_num players..."


if [[ "$replay_flag" == "--replay" ]]; then
  replay_arg="--replay_file ./last_replay"
fi
python3 $workdir"run.py" $config_file $player_num $replay_arg &

sleep 2
echo "starting player 1"

python3 $bots_dir"client_bridge.py" "bot/naive_astar_no_speed.py" &


wait
if [[ "$replay_arg" == "" ]]; then
  exit 0
fi

echo "Race complete!"
last_log="last_replay"             #$(ls -t | head -n 1)
echo $last_log
python3 visualisation.py $last_log 




