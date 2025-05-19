<llm.txt>
General Guidelines
 * Plan First: Before coding, create a detailed implementation plan in plan.md, explaining actions and rationale. Update this plan as you complete tasks.
 * Prioritize Simplicity: Favor simple, error-free approaches over complex ones, unless specifically requested.
 * Review and Refactor: After implementing a feature, review your code for correctness, modularity, and potential code reuse.
 * Don't Alter Tests to Pass: If tests fail, fix the code, not the tests (unless the tests themselves are flawed).
 * Explain Design Decisions: Clearly articulate your design choices. If fixing bugs, explain their cause to prevent future occurrences.

Design Guide
 * Simple Tests: Keep tests as simple as possible, akin to unit tests.
 * Code Consistency: Reuse existing code and maintain the established coding style.
 * Test without Changing Code: When writing tests, avoid modifying existing code unless it contains bugs.
Style Guide
 * No Numbered Comments: Do not use numbered lists (e.g., 1., 2., 3...) in comments.

Details
 * NVIDIA Environment: When setting up NVIDIA environments, verify compatibility using nvidia-smi and checking the installed version.
 * Conda Usage: Always initialize (conda init) and activate the correct conda environment before running commands.
 * Linter Settings: Do not modify linter configurations.
Language Specific
 * Rust: Refer to llm.rust.
<EOF>

<llm.rust>

- Rust does not support named parameters
- Whenever you call an object with a mutable method, you have to make sure that that object is declared mutably.
<EOF>