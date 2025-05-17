# Notes

## To Push to Remote

```sh
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/warren/github
# Enter "warren" (without quotes) when prompted
git push
```

## Access Dashboard

To access the shenzhen cluster, we use the following in ~/.ssh/config

```sh
Host shenzhen-node2
    HostName 10.0.0.2
    User root
    ProxyJump shenzhen.cluster

Host shenzhen-nodem
    HostName 10.0.0.3
    User root
    ProxyJump shenzhen.cluster
```

Then, to access the dashboard, we can use the following ssh command:

```sh
ssh -L 8080:localhost:29510 shenzhen-nodem
```

Then, we can access the dashboard at http://localhost:8080 in the local web browser.