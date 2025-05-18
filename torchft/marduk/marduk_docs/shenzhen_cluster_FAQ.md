# Shenzhen Cluster Development Guide

This guide provides essential information for developing and testing Marduk on the Shenzhen cluster.

## SSH Access Configuration

To access the Shenzhen cluster, add the following to your `~/.ssh/config` file:

```sh
Host shenzhen.cluster
    HostName 183.240.204.32
    User root

Host shenzhen-node2
    HostName 10.0.0.2
    User root
    ProxyJump shenzhen.cluster

Host shenzhen-nodem
    HostName 10.0.0.3
    User root
    ProxyJump shenzhen.cluster
```

### Connecting to the Cluster

```bash
ssh root@shenzhen-nodem
# Password: Lgtest2024
# You'll need to enter the password twice:
# 1. First to log into shenzhen.cluster
# 2. Then to jump to shenzhen-nodem
```

## Development Environment

The main development directory is:
```
/srv/apps/warren/torchft
```

## Accessing the Lighthouse Dashboard

To access the TorchFT Lighthouse dashboard, set up a local port forwarding:

```sh
ssh -L 8080:localhost:29510 shenzhen-nodem
```

Then access the dashboard at http://localhost:8080 in your local web browser.

## Git Repository Access

To push changes to the GitHub repository:

```sh
# Set up your SSH agent
eval "$(ssh-agent -s)"

# Add your GitHub SSH key
ssh-add ~/.ssh/warren/github

# Enter the passphrase "warren" when prompted
# Then push changes
git push
```

## Troubleshooting Common Issues

### Connection Problems

If you cannot connect to a node:
1. Check that you can reach the gateway node (`shenzhen.cluster`)
2. Verify your SSH config has the correct ProxyJump configuration
3. Ensure your IP is whitelisted on the firewall

### Dashboard Access Issues

If the dashboard doesn't load:
1. Verify that the Lighthouse service is running
2. Check that your port forwarding is active
3. Confirm that no firewall is blocking local port 8080

### Git Push Failures

If git push fails:
1. Ensure your SSH key has been added to the agent
2. Verify that your key has been added to your GitHub account
3. Check that you have the correct permissions on the repository

