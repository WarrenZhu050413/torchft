Before implementing any feature, first create a detailed implementation plan in the plan.md file. Go back and tick off every implemented feature.

Always activate the correct conda environment before executing commands. Do conda init before conda activate.

Always look back on the code that you've written after you finished a feature and check whether it is correct, and whether you could make the code a) more modular, b) have more code reuse.

Do not change the test if you are not passing the tests to make the tests pass.

Don't change the linter settings.

Every change you make should reuse the code from the existing codebase if there is any existing code, and be coded in the same style.

When implementing tests, I want you to create the test without changing the existing code, unless there are bugs in the existing code.

If setting up NVIDIA environments, check nvidia-smi and the currently installed version to make sure that everything is compatible. 

In your pull requests, you should write in extreme detail what you did and why you did it. Don't introduce any unnecessary changes.