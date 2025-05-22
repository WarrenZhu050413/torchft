The `examples` directory contains runnable training loops demonstrating torchft
with different algorithms.

Each subdirectory includes:
- a training script
- a `.torchxconfig` configured to run the script
- a small `README.md` describing how to launch the example

Start the lighthouse server before running any example:

```sh
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

Then change into the desired example directory and run:

```sh
torchx run
```

You may also invoke the script directly using `torchrun` as shown in each example README.
