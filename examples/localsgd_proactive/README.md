This example combines LocalSGD with proactive recovery mode.

Start the lighthouse:
```sh
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

Launch with TorchX:
```sh
torchx run
```

Manual run on a single machine:
```sh
export TORCHFT_PROACTIVE_RECOVERY=1
CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- examples/localsgd_proactive/train_localsgd_proactive.py
```
Second shell:
```sh
export TORCHFT_PROACTIVE_RECOVERY=1
CUDA_VISIBLE_DEVICES=1 TORCHFT_LIGHTHOUSE=http://localhost:29510 \
  torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- examples/localsgd_proactive/train_localsgd_proactive.py
```
