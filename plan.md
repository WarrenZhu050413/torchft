# Lighthouse Failure Handling Improvement Plan

- [X] **Modify `_failure_tick` Function:**
    - [X] Iterate through `state.heartbeats`.
    - [X] For replicas with expired heartbeats:
        - [X] Check if the `replica_id` is already present in `state.failures`.
        - [X] If not in `state.failures` (i.e., it's a new failure):
            - [X] Send a `FailureNotification` via `state.failure_channel`.
            - [X] Add the `replica_id` and current `Instant` to `state.failures`.
            - [X] Remove the `replica_id` from `state.heartbeats`.
            - [X] Remove the `replica_id` from `state.participants`.
        - [X] If already in `state.failures` (already notified), do nothing further for this replica in this tick regarding notification or removal, as it's already been processed.
    - [X] For replicas with non-expired heartbeats:
        - [X] If the `replica_id` is present in `state.failures`, remove it (signifying recovery).
- [X] **Update Unit Tests:**
    - [X] **Enhance `test_failure_tick_marks_failures` (or create a new test, e.g., `test_failure_tick_single_notification_and_cleanup`):**
        - [X] Setup: Include a replica in `participants`.
        - [X] Action: Call `_failure_tick` once.
        - [X] Assert:
            - [X] `FailureNotification` is sent (how to check this precisely might need a small refactor or a test-specific channel).
            - [X] Replica is added to `state.failures`.
            - [X] Replica is removed from `state.heartbeats`.
            - [X] Replica is removed from `state.participants`.
        - [X] Action: Call `_failure_tick` again.
        - [X] Assert:
            - [X] No new `FailureNotification` is sent for the same replica.
            - [X] Replica remains in `state.failures`.
            - [X] Replica remains absent from `state.heartbeats` and `state.participants`.
    - [X] **Verify Existing Tests:**
        - [X] Ensure `test_failure_channel_broadcast` (if it exists or is relevant) still passes.
        - [X] Ensure `test_subscribe_failures_delivers_notifications` still correctly receives a single notification for a new failure.
        - [X] Ensure `test_lighthouse_subscribe_failures` still passes.
- [X] **Update Documentation:**
    - [X] Add/update comments for the `State` struct, specifically for `heartbeats`, `failures`, and `participants`, to clarify their roles in the new failure handling logic.
    - [X] Add/update comments for the `_failure_tick` method to describe its updated behavior (single notification, cleanup of failed replicas).
- [X] **Review and Refactor:**
    - [X] Check if the logic for re-adding participants (via quorum requests or new heartbeats) is robust and correctly handles previously failed-and-removed replicas.
    - [X] Ensure code style and clarity.

# Implementation Plan: Reset Participants on New Failure

This plan outlines the steps to modify the `_failure_tick` function in `src/lighthouse.rs` to clear `state.participants` whenever a new failure is detected and successfully broadcast.

## 1. Modify `_failure_tick` in `src/lighthouse.rs`

**Objective:** Ensure that any ongoing quorum formation process is reset when a replica failure is newly detected.

**Actions:**

-   [x] **Introduce `failure_detected` flag:**
    -   In `_failure_tick`, initialize a boolean variable `failure_detected = false;` at the beginning of the function.
    -   **Rationale:** This flag will track if a *new* failure has been successfully processed and broadcasted within the current tick.

-   [x] **Update `failure_detected` flag upon new failure:**
    -   Inside the loop iterating over `state.heartbeats`, within the `if !state.failures.contains_key(replica_id)` block (which identifies a new failure):
        -   After successfully sending the notification (`state.failure_channel.send(...)`), set `failure_detected = true;`.
    -   **Rationale:** We only want to clear participants if a new failure notification was actually sent. If `send` fails, we shouldn't disrupt the participants list based on a failure that wasn't communicated.

-   [x] **Clear `state.participants` if a new failure was detected:**
    -   After the loop iterating through `state.heartbeats` and after the loop that removes replicas from `state.heartbeats` (i.e., towards the end of the function, before `Ok(())`).
    -   Add a conditional block:
        ```rust
        if failure_detected {
            info!("New failure detected, resetting all participants for quorum formation.");
            state.participants.clear();
        }
        ```
    -   **Rationale:** This is the core logic. If a new failure was detected and broadcasted in this tick, we clear all current participants. This forces any in-progress quorum formation (which might have included the failed replica or been based on a now-stale view of the cluster) to be abandoned. Healthy replicas will need to re-request to join the quorum.

-   [x] **Review existing tests:**
    -   The test `test_failure_tick_single_notification_and_cleanup` already verifies that a *specific* failed replica is removed from `participants`. With the new change, if that's the *only* participant, `participants` will become empty. If there are other participants, they will now *also* be cleared. This test should still pass as its core assertions about the failed replica (being in `failures`, removed from `heartbeats` and `participants`) remain true. The broader clearing of all participants is an extension of this.
    -   No new tests will be added as per the instructions unless a bug is found in existing code that requires it.

## 2. Review and Refactor

-   [x] After implementation, review the changes in `_failure_tick` for clarity, correctness, and adherence to the existing coding style.
-   [x] Ensure that the logging provides clear information about the reset (changed log message slightly for clarity).

This plan aims for a targeted modification to achieve the desired behavior with minimal side effects, ensuring that the quorum formation process is always based on the most current understanding of healthy and participating replicas, especially after failures.

# Refactoring Plan for `test_failure_clears_participants_for_new_quorum`

This plan outlines the steps to refactor the `test_failure_clears_participants_for_new_quorum` method in `torchft/lighthouse_test.py` to use `Manager` instances instead of direct `LighthouseClient` and `LighthouseServer` interactions for managing replicas and quorums.

## Tasks

- [ ] **1. Initialize Shared Lighthouse Server**:
    - Keep the existing `server_opt` dictionary for `LighthouseServer` configuration.
    - Create a single `LighthouseServer` instance that both `Manager` instances will connect to.

- [ ] **2. Initialize Manager Instances (`manager_A`, `manager_B`)**:
    - For each manager ("repA" and "repB"):
        - Create a `torch.distributed.TCPStore` for its `store_address`.
        - Instantiate `Manager` with the following configurations:
            - `pg=ProcessGroupGloo()`
            - `min_replica_size=server_opt["min_replicas"]`
            - `load_state_dict=lambda x: None`
            - `state_dict=lambda: None`
            - `replica_id` (e.g., "repA", "repB")
            - `store_addr="localhost"`
            - `store_port` (from its respective `TCPStore`)
            - `rank=0` (initial rank)
            - `world_size=1` (initial world size for the manager itself)
            - `use_async_quorum=False` (to ensure `start_quorum` is blocking and returns results, mimicking direct client calls)
            - `lighthouse_addr=lighthouse.address()` (address of the shared `LighthouseServer`)
            - `lighthouse_join_timeout_seconds = server_opt["join_timeout_ms"] / 1000.0 * 3` (align with original test's timeout logic)
            - `lighthouse_heartbeat_interval_seconds = server_opt["heartbeat_timeout_ms"] / 1000.0 / 3` (ensure heartbeats are frequent enough relative to timeout)

- [ ] **3. Stage 1: Initial Quorum Formation (Target 2 Participants)**:
    - Call `manager_A.start_quorum(current_step=0, target_world_size=2, target_min_world_size=server_opt["min_replicas"])`. Store the result if needed, though the primary check comes after both attempt to join.
    - Call `manager_B.start_quorum(current_step=0, target_world_size=2, target_min_world_size=server_opt["min_replicas"])`.
    - Add a short sleep to allow server-side processing: `time.sleep(server_opt["quorum_tick_ms"] / 1000.0 * 2)`.
    - One manager (e.g., `manager_A`) re-queries the quorum to verify both participants are included:
        `q_AB_check = manager_A.start_quorum(current_step=0, target_world_size=2, target_min_world_size=server_opt["min_replicas"])`.
    - Assert that `q_AB_check` is not `None`.
    - Assert that `len(q_AB_check.participants) == 2`.
    - Assert that replica IDs "repA" and "repB" are in `q_AB_check.participants`.

- [ ] **4. Stage 2: Simulate Failure of Manager A**:
    - Call `manager_A.shutdown()` to stop its heartbeats and simulate a node failure.

- [ ] **5. Stage 3: Manager B Forms a New Quorum (Target 1 Participant)**:
    - Wait for the Lighthouse server to detect Manager A's failure:
        `sleep_duration = (server_opt["heartbeat_timeout_ms"] + server_opt["failure_tick_ms"] * 2) / 1000.0`
        `time.sleep(sleep_duration)`
    - `manager_B` attempts to form a new quorum, now expecting to be alone:
        `q_B_final = manager_B.start_quorum(current_step=1, target_world_size=1, target_min_world_size=server_opt["min_replicas"])`.
    - Assert that `q_B_final` is not `None`.
    - Assert that `len(q_B_final.participants) == 1`.
    - Assert that `q_B_final.participants[0].replica_id == "repB"`.

- [ ] **6. Cleanup (in `finally` block)**:
    - `lighthouse.shutdown()`
    - `manager_A.shutdown()` (ensure it's idempotent or check if already shut down)
    - `manager_B.shutdown()`
    - Potentially clean up `TCPStore` instances if they require explicit closing (though typically not necessary). 