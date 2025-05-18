# Marduk

Marduk is a runtime monitoring and control system for distributed AI training workloads. Named after the Mesopotamian god who governed the universe, Marduk provides comprehensive monitoring and dynamic control capabilities for PyTorch training jobs.

## Overview

Unlike traditional orchestration frameworks that focus on deployment and scheduling, Marduk provides run-time monitoring and control of the training process itself. It enables:

- **Real-time failure detection** and recovery for GPUs and training replicas
- **Dynamic configuration adjustment** without stopping training
- **Resource mapping** between hardware devices and training replicas

## Key Components

- **Controller**: Central service that maintains device-to-replica mappings and coordinates failure responses
- **Manager Integration**: Direct integration with TorchFT Manager for seamless fault-tolerance
- **NATS Messaging**: Lightweight pub/sub communication layer for system events
- **Monitor CLI**: Command-line interface for manual control and testing

## Quick Start

First, open 6 bash terminals, execute `conda deactivate` in each terminal (potentially twice) if you have multiple conda environments locked within each other. 

Then, you can set of the environment. 

0. Set up and clean up

```bash
cd /srv/apps/warren/torchft # or wherever you have cloned the torchft repository
source marduk_docs/preamble.sh # Sets up the environment, compiles protobuf, and kills all the existing servers.
```

1. Start the nats server
```
/srv/apps/warren/torchft/torchft/marduk/nats-server -c /srv/apps/warren/torchft/torchft/marduk/nats.conf
```
2. Start the controller
```sh
python /srv/apps/warren/torchft/torchft/marduk/controller.py
```

3. Start the cli

```sh
python /srv/apps/warren/torchft/torchft/marduk/monitor_cli.py
```

4. Set up torchFT by starting the lighthouse

```bash
RUST_BACKTRACE=1 torchft_lighthouse --min_replicas 1 --quorum_tick_ms 100 --join_timeout_ms 10000
```

5. Run the torchFT training script on one device

Start Device 1:
```sh
export REPLICA_GROUP_ID=0
export NUM_REPLICA_GROUPS=2

CUDA_VISIBLE_DEVICES=0 TORCHFT_LIGHTHOUSE=http://localhost:29510 torchrun --master_port=29600 --nnodes=1 --nproc_per_node=1 -- train_ddp.py
```

6. Optionally, to test multiple device failures, you can run the training script on another device.

Start Device 2:
```sh
export REPLICA_GROUP_ID=1
export NUM_REPLICA_GROUPS=2

CUDA_VISIBLE_DEVICES=1 TORCHFT_LIGHTHOUSE=http://localhost:29510 torchrun --master_port=29601 --nnodes=1 --nproc_per_node=1 -- train_ddp.py
```

7. Now, control C on any of the training processes. See what happens! Also relaunch the training script, and see what happens!

When the training processes run, you should be able to see the devices registering their device_uuid and replica_id.

```sh
Registered device: GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 for replica_id: train_ddp_0:d5aa538f-3268-4f78-ae88-3afff894e629 # For replica 0
Registered device: GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 for replica_id: train_ddp_1:164ecd9c-f806-4eef-8fd3-add20298ea20 # For replica 1
```

Then, you can go to [tutorial.md](tutorial.md) for detailed testing scenarios and instructions to see what Marduk is capable of.

## Documentation

- [Design](design.md): System architecture and concepts
- [Test](tests.md): Testing procedures and example workflows
- [Debugging](debugging.md): Troubleshooting guide for common issues
- [TODO](TODO.md): Upcoming features and development roadmap
- [Shenzhen Cluster FAQ](shenzhen_cluster_FAQ.md): Specific information for development on the Shenzhen cluster
