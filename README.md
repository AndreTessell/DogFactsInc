# Dog Facts, Inc.

In this workshop you'll learn how Datadog can improve the visiblity into your applications and infrastructure by combining metrics, traces, and logs into a single platform. We'll follow the story of Dog Facts, Inc. as they deploy their application and maximize the observiblity within their organization.

You'll learn:
- The benefits of a single unified platform for Metrics, Traces, and Logs
- How to configure a Datadog agent and integration
- How to send application traces to Datadog and use App Analytics to disect your traces
- How to send any logs to Datadog and automatic coorelation to metrics and traces
- How to visualize all of your data using dashboards
- How to create alerts allowing you to notify your team to issues
- How to create SLOs in Datadog and why they're beneficial to your team


## Prerequisites

Before coming to this workshop you should have:
- A basic understanding of docker - https://docs.docker.com/engine/docker-overview/
- Docker installed on your laptop
  - Mac OSX: https://docs.docker.com/docker-for-mac/install/
  - Windows: https://docs.docker.com/docker-for-windows/install
- Git installed on your laptop (optional) - https://git-scm.com/
- The datadog/agent container pulled down
  `docker pull datadog/agent:latest`
- A code editor on your laptop (e.g. VSCode, Sublime, Atom)

## Slides

**TODO** Add slides

## Steps

1. Clone this repo
   
   ```bash
   $ git clone https://github.com/andrewelizondo/DogFactsInc
   $ cd DogFactsInc
   ```

2. Start the Datadog agent


