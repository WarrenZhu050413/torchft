# Plan
* [x] Add `FailureNotification` message and `SubscribeFailures` RPC to `proto/torchft.proto`.
* [x] Lighthouse server monitors heartbeat expirations and broadcasts `FailureNotification`.
* [x] Expose streaming RPC in Rust bindings and Python `LighthouseClient` via `subscribe_failures()`.
* [x] Manager creates a `LighthouseClient`, starts a listener thread, and logs received failures.
* [x] Write tests that heartbeat timeouts trigger a failure notification.
* [x] Remove `py.allow_threads` usage from the new `subscribe_failures` binding.
* [x] Add integration test measuring process group abort time when a manager dies.
