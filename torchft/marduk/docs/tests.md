# Testing

To test, start the monitor cli:
```sh
python /srv/apps/warren/torchft/torchft/marduk/monitor_cli.py
marduk>
```

## Test 0: DRMapping Registration upon starting training

Controller output:

```bash
Marduk constants module loaded
Starting Marduk Controller
Controller initialized with NATS address: nats://0.0.0.0:4222
Connected to NATS server at nats://0.0.0.0:4222
Subscribing to marduk.DRentry on stream CONTROLLER-STREAM with consumer controller-consumer
Subscribed to marduk.monitored.failure
Controller initialized and subscribed to all subjects
Started listening on marduk.DRentry
Started listening on marduk.monitored.failure
```

Once the two training scrips start according to the above instructions, then should see the registration on the controller:

```bash
----------------------------------------------------------------------------------------------------
Received register_device event for device GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 and replica train_ddp_1:fe7a317e-6474-4d9d-8c8a-2a74b321af17
New Mapping: Device GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 is now associated with replicas: {'train_ddp_1:fe7a317e-6474-4d9d-8c8a-2a74b321af17'}
New Mapping: Replica train_ddp_1:fe7a317e-6474-4d9d-8c8a-2a74b321af17 is now associated with devices: {'GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28'}

----------------------------------------------------------------------------------------------------
Received register_device event for device GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 and replica train_ddp_0:e0d9df8d-8b61-4f2d-a769-5acc59b9ef9d
New Mapping: Device GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28 is now associated with replicas: {'train_ddp_0:e0d9df8d-8b61-4f2d-a769-5acc59b9ef9d', 'train_ddp_1:fe7a317e-6474-4d9d-8c8a-2a74b321af17'}
New Mapping: Replica train_ddp_0:e0d9df8d-8b61-4f2d-a769-5acc59b9ef9d is now associated with devices: {'GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28'}
```

## Test 1: To fail a replica, run:

```sh
marduk> test 50
Received message
[GPU FAILURE] Device not found in device replica map
```

Here, there are two possible cases. If the device_uuid is not found in the device replica map, then the device is not registered.
Here, the device_uuid is printed out by the controller whenever a training process starts on a device.

## Test 1a: Device not registered

CLI output:

```bash
marduk> test 50
Executing test command with input: 50
Simulating failed GPU with uuid: 50
Published device failure event for device 50
```

Controller output:
```bash
[GPU FAILURE] Device 50 not found in device-to-replicas map
```

## Test 1b: Device registered

CLI output:
```sh
marduk> test GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28
Executing test command with input: GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28
Simulating failed GPU with uuid: GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28
Published device failure event for device GPU-307a982d-bf2b-4cc3-64e3-aae456bf6a28
```

Controller output:

```bash
[GPU FAILURE] Associated Replica IDs: {'train_ddp_1:b584d120-6037-4a33-aeb6-54fcbcbee9bf'}
```

Output from the associated replica:

## Test 2: Test NATS server failure

After the NATS server fails, the controller and the training script should not fail, but retry to connect.