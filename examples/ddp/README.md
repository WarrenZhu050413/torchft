This example runs a minimal fault tolerant DDP training loop.

Start the lighthouse server:
```sh
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

Launch the job with TorchX from this directory:
```sh
torchx run
```

To run manually with two replica groups on one machine use two shells:
```sh
CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- examples/ddp/train_ddp.py
```
Second shell:
```sh
CUDA_VISIBLE_DEVICES=1 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- examples/ddp/train_ddp.py
```
