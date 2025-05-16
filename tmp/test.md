
# Start a simple test:

1. Start the nats server
```
/srv/apps/warren/torchft/torchft/marduk/nats-server -c /srv/apps/warren/torchft/torchft/marduk/nats.conf
```
2. Start the controller
```sh
python /srv/apps/warren/torchft/torchft/marduk/controller.py
```

3. Run the training

Start the lighthouse first:

```bash
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

Then run the training:

Start Device 1:
```sh
export REPLICA_GROUP_ID=0
export NUM_REPLICA_GROUPS=2

CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- train_ddp.py
```

Start Device 2:
```sh
export REPLICA_GROUP_ID=1
export NUM_REPLICA_GROUPS=2

CUDA_VISIBLE_DEVICES=1 TORCHFT_LIGHTHOUSE=http://localhost:29510 torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- train_ddp.py
```

When the training processes run, you should be able to see the devices registering their device_uuid and replica_id.

```sh
Registered device: GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 for replica_id: train_ddp_0:d5aa538f-3268-4f78-ae88-3afff894e629 # For replica 0
Registered device: GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 for replica_id: train_ddp_1:164ecd9c-f806-4eef-8fd3-add20298ea20 # For replica 1
```

4. Testing

To test, start the monitor cli:
```sh
python /srv/apps/warren/torchft/torchft/marduk/monitor_cli.py
marduk>
```

To fail a replica, run:

```sh
marduk> test 50
Received message
[GPU FAILURE] Device: {device_uuid}
[GPU FAILURE] Device not found in device replica map
```

Here, the device_uuid is printed out by the controller whenever a training process starts on a device.

```sh
marduk> test 50
Received message
[GPU FAILURE] Device: 50
[GPU FAILURE] Device not found in device replica map
```