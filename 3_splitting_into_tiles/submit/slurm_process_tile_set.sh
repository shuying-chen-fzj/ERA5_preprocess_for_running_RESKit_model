#!/bin/bash
### s-chen updated on 2025-11-10

#SBATCH --job-name="era5split"
#SBATCH --output=./log/job-out.%j
#SBATCH --error=./log/job-err.%j
#SBATCH --cpus-per-task=1
#SBATCH --array=0-223
#SBATCH --exclude=cn[1-4,8-12,15-19,25-35,38,42,48-54]
#SBATCH --account=s-chen

###################################
## set X and Y tiles (16 x 14 = 224 tiles)
TILES_X=(0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15)
TILES_Y=(0 1 2 3 4 5 6 7 8 9 10 11 12 13)

# declare -a YEARS
declare -a TILES_XX
declare -a TILES_YY

#for yr in $(seq 1980 2019); do

for xi in ${TILES_X[@]}; do
    for yi in ${TILES_Y[@]}; do
        # YEARS+=($yr)
        TILES_XX+=($xi)
        TILES_YY+=($yi)
    done
done

#done

#####################################

NUM_TASKS=${#TILES_XX[@]}
LAST_IDX=$((NUM_TASKS - 1))
echo "Total tile tasks: $NUM_TASKS (indices 0-$LAST_IDX)"

# allow running interactively (default to task 0)
TASK_ID=${SLURM_ARRAY_TASK_ID:-0}
echo "SLURM_ARRAY_TASK_ID = $TASK_ID"

if (( TASK_ID < 0 || TASK_ID > LAST_IDX )); then
    echo "SLURM_ARRAY_TASK_ID ($TASK_ID) out of range (0-$LAST_IDX), exiting."
    exit 1
fi

# fixed year for this run
year=2018
xi=${TILES_XX[$TASK_ID]}
yi=${TILES_YY[$TASK_ID]}
zoom=4

# threading environment: match cpus-per-task or keep conservative
export OMP_NUM_THREADS=1
export USE_SIMPLE_THREADED_LEVEL3=1
export MKL_NUM_THREADS=1

source activate cdo

echo "Running task $TASK_ID -> year=$year xi=$xi yi=$yi zoom=$zoom"
python ../ERA5_processor_split_era5_into_tiles.py $year $xi $yi $zoom
