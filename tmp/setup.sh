# Set up torchFT environment, 
conda activate /srv/apps/danny/miniconda3/envs/warren/torchtitan
pip install -e .
protoc --python_out=. torchft/marduk/marduk.proto
