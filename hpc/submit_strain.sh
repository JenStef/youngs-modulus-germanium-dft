#!/bin/bash

#SBATCH -A mtgn473_spring2026_vstevano
#SBATCH -p student
#SBATCH --nodes=1 # number of nodes
#SBATCH --ntasks-per-node=8 # number of tasks per node
####SBATCH --ntasks=12 # redundant; total number of tasks: ntasks = nodes * ntasks-per-node
#SBATCH --time=04:00:00 # time in HH:MM:SS
#SBATCH -o ./jobs/%j/output.%j # standard print output labeled with SLURM job id %j
#SBATCH -e ./jobs/%j/error.%j  # standard print error labeled with SLURM job id %j

# module loads here

# Define the options: f requires an argument, r is optional restart flag
while getopts ":f:r" opt; do
  case $opt in
    f)
      FILE_PATH="$OPTARG"
      echo "File path specified: $FILE_PATH"
      ;;
    r)
      RESTART_MODE="restart"   # NEW: if you submit with -r, QE will restart instead of starting fresh
      ;;
  esac
done

# Stop if no input file was provided
if [ -z "$FILE_PATH" ]; then
  echo "Usage: sbatch sbatch.sh -f inputfile.in [-r]"
  exit 1
fi

# Extract base filename (example: input/Ge_101.in -> Ge_101)
BASE_NAME=$(basename -s .in "$FILE_PATH")   # NEW: used to create unique restart/output names

OUTPUT_FILE_NAME="${BASE_NAME}.out"
echo "$OUTPUT_FILE_NAME"

# Make sure output directories exist
mkdir -p ./output                      # NEW: ensures output folder exists
mkdir -p ./scratch/$BASE_NAME          # NEW: creates unique restart folder for this run
mkdir -p ./jobs/$SLURM_JOB_ID          # NEW: ensures Slurm output/error folder exists for this job

# Create a temporary input file inside this job folder
TEMP_INPUT="./jobs/$SLURM_JOB_ID/${BASE_NAME}.in"   # NEW: per-job patched copy of input
cp "$FILE_PATH" "$TEMP_INPUT"                       # NEW: copy original input so we don’t edit it directly

# Default restart mode if -r was NOT given
if [ -z "$RESTART_MODE" ]; then
  RESTART_MODE="from_scratch"   # NEW: if you don’t use -r, it starts fresh
fi

# Patch the copied input file only (not your original file)
sed -i "s|^[[:space:]]*prefix=.*|    prefix='${BASE_NAME}'|g" "$TEMP_INPUT"  
# NEW: changes prefix so each run has its own .save files

sed -i "s|^[[:space:]]*outdir=.*|    outdir='./scratch/${BASE_NAME}/'|g" "$TEMP_INPUT"  
# NEW: sends QE restart files into a unique folder for this run

sed -i "s|^[[:space:]]*restart_mode=.*|    restart_mode='${RESTART_MODE}'|g" "$TEMP_INPUT"  
# NEW: changes restart_mode automatically depending on whether you used -r

echo "Job has started!"
echo "Running with patched input: $TEMP_INPUT"     # NEW: shows which input is actually being run
echo "Using prefix: $BASE_NAME"                    # NEW: shows unique QE prefix
echo "Using outdir: ./scratch/$BASE_NAME/"         # NEW: shows unique QE restart folder
echo "Using restart_mode: $RESTART_MODE"           # NEW: confirms restart or fresh run

srun -n 8 ./pw.x -in "$TEMP_INPUT" > ./output/$OUTPUT_FILE_NAME  
# CHANGED: uses patched temp input instead of original file, so each run stays separate

echo "Job has ended!"
