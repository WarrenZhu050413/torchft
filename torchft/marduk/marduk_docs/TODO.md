# Marduk TODOs

## UI and Monitoring Enhancements

### Data Visualization
1. Display comprehensive DR Mapping
2. Display all the display information in a single page
2. Show real-time training status for each replica
3. Maintain history of past failures

### Runtime Configuration
1. Enable hyperparameter broadcasting from training runtime to controller
   - Maintain a map: replica_id → hyperparameters

2. Implement direct configuration updates without restarts
   - Allow dynamic tuning of parameters when training becomes unstable
   - Enable real-time configuration changes without training interruption

3. Integrate with checkpointing system
   - Allow controller to specify which checkpoint to load
   - Synchronize across distributed training processes

### Training Optimizations
1. Dynamic dataloader modifications
   - Add/remove transformations on-the-fly
   - Adjust batch sizes
   - Maintain constant global batch size when scaling
   - Automatic learning rate adjustments

## Core System Improvements
1. Make controller and Manager handle NATS connection failures (e.g. when we have a network partition or the server is down) gracefully, e.g. by retrying.
2. Implement persistence for DR mapping in an object store
3. Create ManagerMarduk as a proper extension to the Manager module
4. Handle resource draining by properly deleting DR mapping entries from both NATS JetStream and controller map
5. Improve replica ID handling for multiple jobs

## Advanced Features

### Zero-Downtime Operations
1. Support hot-swapping components for:
   - Security updates
   - Algorithm improvements
   - Hardware maintenance
2. Implement "drain" functionality for GPUs requiring replacement

### Integration with External Systems
1. SuperBench integration for failure prediction
   - Use ML models to predict GPU failure probabilities
   - Automatically manage GPU testing and replacement cycle

### Performance Monitoring
1. Live straggler detection
   - Track allreduce group membership and timing
   - Identify and handle performance bottlenecks
   - Calculate straggler impact and selectively remove from training
   - Implement dynamic timeout adjustments

2. Add configurable maximum iteration support