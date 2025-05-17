1. The replica ID of which job? Currently assumes a single job.
2. Persist the dr_map. Put it in an object store.
3. ManagerMarduk as an extension to the Manager module.
4. When drain, delete the DR mapping entry. Delete it from nats jetstream as well as the controller map.


UI:

I want to be able to see, from the controller, the following:

1. The DR Mapping
2. The training status of each replica
3. Past failures
