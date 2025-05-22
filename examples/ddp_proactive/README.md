This example enables proactive recovery mode to react quickly to failures.

Start the lighthouse server:
```sh
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

Launch with TorchX:
```sh
torchx run
```

Manual run with two replica groups:
```sh
export TORCHFT_PROACTIVE_RECOVERY=1
CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- examples/ddp_proactive/train_ddp_proactive.py
```
Second shell:
```sh
export TORCHFT_PROACTIVE_RECOVERY=1
CUDA_VISIBLE_DEVICES=1 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- examples/ddp_proactive/train_ddp_proactive.py
```
