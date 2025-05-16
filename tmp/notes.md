# Set up Marduk

1. Set up all the torchFT environments according to their README.md

2. Set up the torchFT environment
```sh
cd /srv/apps/warren/torchft
source /srv/apps/warren/torchft/tmp/setup.sh
```

3. Compile the protobufs

```sh
protoc --python_out=. torchft/marduk/marduk.proto
```

Start nats server
```
/srv/apps/warren/torchft/torchft/marduk/nats-server -c /srv/apps/warren/torchft/torchft/marduk/nats.conf
```

# Other notes

Marduk has a new environmental variable:

```python
os.environ["MARDUK_ADDR"]
```

the default address is `nats://localhost:4222`

To Push to Remote:

```sh
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/warren/github
# Enter "warren" (without quotes) when prompted
git push
```