Run 

```sh
cd /srv/apps/warren/torchft
source /srv/apps/warren/torchft/tmp/setup.sh
```

To compile the protobufs, run

```sh
python -m torchft.marduk.compile_protos
```

Start nats server
```
./nats-server -c ./nats.conf
```

New environmental variables:

```python
os.environ["MARDUK_ADDR"]
```




