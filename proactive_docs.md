# Tests

1. In Rust, we have lighthouse.rs::test_subscribe_failures_delivers_notifications and lighthouse.rs::test_lighthouse_subscribe_failures.

To enable GIL release for such an iterator, a common pattern involves a more significant refactoring:
FailureStream could spawn a background Tokio task when it's created.
This task would own the tonic::Streaming and continuously poll stream.next().await.
Results would be sent over an mpsc (multi-producer, single-consumer) channel to the FailureStream.
The __next__ method would then perform a blocking receive on this channel (e.g., channel_receiver.recv_timeout(timeout_duration)). This blocking receive can be wrapped in py.allow_threads because the channel receiver and the receive operation itself don't suffer from the same lifetime issues.



Demonstration:

The demonstration is in the training script: train_ddp_proactive.py.

<Insert Description>

Start Lighthouse:
```sh
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_
ms 10000
```

Then, start the two training processes:

```sh
export REPLICA_GROUP_ID=0
export NUM_REPLICA_GROUPS=2
CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- train_ddp_proactive.py
```

```sh
export REPLICA_GROUP_ID=1
export NUM_REPLICA_GROUPS=2

CUDA_VISIBLE_DEVICES=1 
TORCHFT_LIGHTHOUSE=http://localhost:29510 torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- train_ddp_proactive.py
```

You will observe that after 5 seconds, the training process with REPLICA_GROUP_ID=1 will exit, and REPLICA_GROUP_ID=1 will not exit.

On the other hand, if we do:

```sh
export TORCHFT_PROACTIVE_RECOVERY=1 
```

You will observe the manager shutdown with

```sh
INFO:torchft.manager:[train_ddp_0:81a52ce4-d803-4f22-a0c3-54f3b4a88c89/0 - step 10] Setting error processor thread stop event
INFO:torchft.manager:[train_ddp_0:81a52ce4-d803-4f22-a0c3-54f3b4a88c89/0 - step 10] Waiting for error processor thread to complete
INFO:torchft.manager:[train_ddp_0:81a52ce4-d803-4f22-a0c3-54f3b4a88c89/0 - step 10] Error processor thread shutdown completed.
INFO:torchft.manager:[train_ddp_0:81a52ce4-d803-4f22-a0c3-54f3b4a88c89/0 - step 10] Setting failure listener stop event for process
INFO:torchft.manager:[train_ddp_0:81a52ce4-d803-4f22-a0c3-54f3b4a88c89/0 - step 10] Waiting for failure listener process to complete
INFO:torchft.manager:[train_ddp_0:81a52ce4-d803-4f22-a0c3-54f3b4a88c89/0 - step 10] Failure listener process shutdown completed
```

And in the Lighthouse you will observe:

```sh
2025-05-20T22:29:30.029 [INFO] [torchft::lighthouse] - Replica train_ddp_1:a581dae2-1ebc-4f93-b882-6477832fef6b timed out (last heartbeat: Instant { tv_sec: 5200692, tv_nsec: 955240591 }), sending failure notification.
2025-05-20T22:29:30.029 [INFO] [torchft::lighthouse] - Removed replica train_ddp_1:a581dae2-1ebc-4f93-b882-6477832fef6b from heartbeats and participants due to timeout.
2025-05-20T22:29:30.029 [INFO] [torchft::lighthouse] - New failure detected, resetting all participants for quorum formation.
2025-05-20T22:29:30.029 [INFO] [torchft::lighthouse] - Permanent subscriber received failure notification for train_ddp_1:a581dae2-1ebc-4f93-b882-6477832fef6b
```

The recovery process will be much faster.

Under the hood.



## Implementation

I tried various implementations, and at last settled on using multi-processing.

This may not be the most elegant solution. One solution could be using asyncio.

The main problem is that if we start another thread in the main process to listen to the tokio stream, it will be a blocking wait preventing the main thread to continue.

There are three solutions to this:

1. Release GIL in the Rust code
This gets complicated as we would need to decouple the Python related code with the Rust blocking code.

2. Use pyo3-asyncio to turn the iterator into an async iterator and use asyncio.
I attempted this route but because I am not very familiar with Rust could not get this working.

3. Use multiprocessing
- Downside: Larger overhead, requires implementing a layer of interprocess communication.



## Details

The timeout variable is for the timeout of the blocking call to listen to the stream. This enables the failure_listener_process to be interrupted and shut down.
