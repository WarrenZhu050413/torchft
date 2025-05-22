This example trains with LocalSGD using torchft for fault tolerance.

Start the lighthouse:
```sh
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

Launch with TorchX:
```sh
torchx run
```

Manual execution on a single machine:
```sh
CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- examples/localsgd/train_localsgd.py
```
Second shell:
```sh
CUDA_VISIBLE_DEVICES=1 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- examples/localsgd/train_localsgd.py
```
