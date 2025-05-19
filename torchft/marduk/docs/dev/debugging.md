# Marduk Debugging Guide

This guide provides troubleshooting steps for common issues with Marduk.

## Checking Component Status

### NATS Server
```bash
# Check if NATS server is running
ps aux | grep nats-server

# Verify NATS server is accessible
telnet localhost 4222

# Check NATS streams and consumers
/srv/apps/warren/torchft/torchft/marduk/nats-cli stream list
/srv/apps/warren/torchft/torchft/marduk/nats-cli consumer list CONTROLLER-STREAM
```

### Controller
```bash
# Check if controller is running
ps aux | grep controller.py

# Check controller logs
tail -f /srv/apps/warren/torchft/torchft/marduk/logging/marduk.log
```

### Manager
```bash
# Check manager logs
tail -f /srv/apps/warren/torchft/torchft/marduk/logging/manager.log
```

## Common Issues

### Message Delivery Problems

If messages aren't being delivered between components:

1. Verify that all components are using the same NATS server address
   ```bash
   # Check environment variable
   echo $MARDUK_ADDR
   
   # Check controller and manager code for hardcoded addresses
   grep -r "MARDUK_ADDR" /srv/apps/warren/torchft/torchft/
   ```

2. Check NATS subscription status
   ```bash
   # Connect to NATS with CLI
   /srv/apps/warren/torchft/torchft/marduk/nats-cli sub ">"
   
   # This will show all messages - should see activity when events occur
   ```

3. Verify the event loop is running in the manager
   ```python
   # Debugging code to add to manager.py
   def debug_event_loop():
       print(f"Loop running: {self._loop.is_running()}")
       print(f"Loop closed: {self._loop.is_closed()}")
   ```

### Replica Failure Detection Issues

If replica failure events aren't being properly handled:

1. Check device-to-replica mappings
   ```bash
   # Start the monitor CLI
   python /srv/apps/warren/torchft/torchft/marduk/monitor_cli.py
   
   # Use a custom command to dump the current DR mapping
   # (This is a suggested feature to implement)
   marduk> dump_map
   ```

2. Manually trigger a failure event to test the pipeline
   ```bash
   # Get a valid device UUID 
   python -c "from torchft.marduk.utils import get_device_uuid; print(get_device_uuid())"
   
   # Use the monitor CLI to test with that UUID
   python /srv/apps/warren/torchft/torchft/marduk/monitor_cli.py
   marduk> test <device_uuid>
   ```

3. Verify message flow in logs
   - Controller should log receiving the device failure
   - Controller should log associated replica IDs
   - Controller should log publishing replica fail events
   - Manager should log receiving the replica fail event

## Asyncio Debugging

Issues with asyncio are common in the Manager integration:

1. Check if the event loop is running
   ```python
   # Add debug logging to _run_event_loop_in_background
   debug_manager_logger.info(f"Loop ID: {id(self._loop)}")
   debug_manager_logger.info(f"Thread ID: {threading.get_ident()}")
   ```

2. Test a simple message round-trip
   ```bash
   # In monitor_cli:
   marduk> publish marduk.test "test message"
   
   # Then check logs to see if the message was received
   ```

3. Verify the background thread is active
   ```bash
   # Add thread name to ps output
   ps -eLf | grep python
   
   # Should see a thread with "asyncio_loop" in the name
   ```

## Environment Setup Problems

1. Make sure Python environment is activated
   ```bash
   conda activate /srv/apps/danny/miniconda3/envs/warren/torchtitan
   ```

2. Check protobuf generated files exist
   ```bash
   ls -la /srv/apps/warren/torchft/torchft/marduk/marduk_pb2.py
   ```

3. Verify CUDA visibility
   ```bash
   echo $CUDA_VISIBLE_DEVICES
   nvidia-smi
   ``` 