# path=${1:-'./data/z-machine-games-master/jericho-game-suite'}
if [ $# -eq 0 ]; then
    echo "Usage: ./gen_all.sh -j <jericho_path> -i <input_dir> [-g <game_name>]"
    exit 1
fi

while getopts j:i:g: flag
do
    case "${flag}" in
        j) jericho_path=${OPTARG};;
        i) input_dir=${OPTARG};;
        g) game_name=${OPTARG};;
    esac
done


./scripts/gen_moves/run_gen_move_human_to_final.sh -p $input_dir -j $jericho_path -g $game_name

./scripts/gen_moves/run_gen_move_reversed_all.sh -i $input_dir -j $jericho_path -g $game_name

./scripts/gen_paths/run_gen_all2all.sh -p $input_dir -o $input_dir -g $game_name