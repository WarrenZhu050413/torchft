## Plan
1. **Understand Requirements**: The `train_diloco.py` script currently mirrors `train_localsgd.py` using `LocalSGD`. We need a working DiLoCo example similar to `diloco_train_loop` in `torchft/local_sgd_integ_test.py`.
2. **Define Implementation**:
   - Load CIFAR10 dataset and create distributed dataloader as in other train scripts.
   - Build the `Net` model as already defined but remove duplicated instantiation.
   - Set up inner and outer optimizers: inner uses `AdamW`, outer uses `SGD`.
   - Adjust state dict/restore logic to also checkpoint DiLoCo `original_parameters` and both optimizers.
   - Use `DiLoCo` context manager with `backup_device=device` and `sync_every=100`.
   - Training loop should zero/step inner optimizer each iteration; DiLoCo takes care of outer optimizer during sync.
3. **Clean Up**: Remove duplicate model creation and fix stray shell text at end if present.
4. **Testing**: Attempt running pytest focused on DiLoCo tests (may fail due to missing dependencies). Record output.
5. **Commit**: Commit updated script and plan.md.
