# Deployment Thingamajigs

## Setup

Deployment scripts are written using [CDK](https://docs.aws.amazon.com/cdk/latest/guide/home.html), the AWS Cloud Development Kit. The CDK dependencies can be installed alongside DuckBot.

```sh
pip install --editable .[cdk]  # run from repository root
```

You'll then actually need CDK. It's a nodejs package, so you'll need that as well.

```sh
npm install -g aws-cdk
```

## Adding New Secrets

To add new secrets (like tokens), only [cdk.json](cdk.json) needs to be modified. Add a secret to the existing list of secrets there.

- `name`: a unique name for the secret, used within the CDK stack
- `environment_name`: the name of the environment variable in the duckbot code base; also must match the GitHub secret name which houses the actual value
- `parameter_name`: the name of the AWS Systems Manager parameter, must start with `/duckbot`

Make sure you also update the `docker-compose.yml` file! And the readme of the repo to include information on how developers can get their own copy of the secrets.

### How Secrets Work

Secrets are annoyingly coupled so that we can end up only modifying a single place (well, plus `docker-compose.yml`, but for _prod_ at least it's one place).

- `cdk.json` puts all secrets into a CDK context variable
  - the stack uses that variable to inject the secrets into the duckbot container
- the stack also writes new versions of those secrets to AWS, pulling new values from the environment
  - this is disabled by default, but enabled for the `deploy` action (enabled like `cdk synth --context write_secrets=true`)
  - if enabled, the deployment will fail if any secret is missing a value
- the `deploy` actions workflow injects all GitHub secrets into the environment then runs the CDK deployment
  - the environment variable name matches the name of the GitHub secret
  - so this ends up creating new versions of the secrets every deployment

## Using CDK

You'll need AWS credentials to use CDK. The following examples assume you have those credentials saved under a `duckbot` AWS CLI profile. The `cdk` commands need to be run from the `.aws` directory.

You can also technically deploy using CDK, but should avoid that. Let the actions workflows do that.

**Synthesize a Stack**

```sh
cdk synth --profile duckbot
```

Synthesizing products `cdk.out/duckbot.template.json`, the CloudFormation template that you can deploy. It also dumps the YML version out to the console.

**Diff a Stack**

```sh
cdk diff --profile duckbot
```

Produces a diff between the stack already deployed and what you have locally.
