Initial plan:
- Add train_localsgd_proactive.py script to examples based on train_localsgd.py with failure injection like train_ddp_proactive.py.
- Move train_ddp.py and train_ddp_proactive.py into examples directory.
- Update torchft/torchx.py default script path to examples/train_ddp.py.
- Update README and CONTRIBUTING docs to refer to new script paths in examples.
- Add README.md in examples that documents how to run all example scripts, including lighthouse startup, torchx run, and manual torchrun commands.
- Add .torchxconfig files for each example script to allow single 'torchx run' command.
- After implementing, run cargo test and pytest and capture failure due to network restrictions or missing dependencies.
