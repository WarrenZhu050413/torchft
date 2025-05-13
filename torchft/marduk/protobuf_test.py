import marduk_pb2

env = marduk_pb2.EventEnvelope()
env.register_device.device_uuid = "123"
env.register_device.replica_id = 1

print(env)
print(env.register_device)
print(env.register_device.device_uuid)
print(env.register_device.replica_id)

print(env.SerializeToString())

print(marduk_pb2.EventEnvelope().ParseFromString(env.SerializeToString()))

print(env.register_device)
print(env.register_device.device_uuid)
print(env.register_device.replica_id)