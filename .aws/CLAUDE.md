# CLAUDE.md — CDK deployment stack

AWS CDK app (Python) that deploys DuckBot to AWS. This directory is developer/ops-only; it
has nothing to do with the bot's runtime behaviour. See the repo-root `README.md` for
one-time human setup (installing the `cdk` extras and the Node `aws-cdk` CLI, AWS creds).

## Layout

- `app.py` — CDK entry point (`cdk.json` runs it). Holds the `SECRETS` list and the
  `write_secrets` logic; instantiates `DuckBotStack`.
- `duckdeploy/stack.py` — the whole `DuckBotStack`.
- `duckdeploy/secret.py` — `Secret` dataclass: `environment_name` (env var the bot reads,
  also the GitHub secret name) + `parameter_name` (AWS SSM path, must start with `/duckbot`).

## What the stack deploys

- ECS on **EC2** (not Fargate): one task definition (`family="duckbot"`, bridge network)
  with two linked containers — `duckbot` and a `postgres:13.2` sidecar — mirroring
  `docker-compose.yml`. Postgres data persists on EFS.
- Runs on a **spot** t3/t2.micro Auto Scaling Group. The ASG scales to 0 nightly (23:55)
  and back to 1 in the morning (05:57), `America/Toronto`, to save cost — so the bot is
  intentionally offline overnight.
- VPC uses public subnets with no NAT gateways (cost).

## Rules & gotchas

- **Don't deploy manually.** GitHub Actions runs the deploy. Locally only ever
  `cdk synth` / `cdk diff` (`--profile duckbot`), and run `cdk` **from this `.aws/`
  directory**. The container image tag comes from `--context duckbot_image=...`.
- **Adding a secret touches four places** (keep them in sync): add a `Secret` to `SECRETS`
  in `app.py`; add the env var to `docker-compose.yml`; add the GitHub Actions secret
  (name must equal `environment_name`); document how devs get it in the root `README.md`.
- **Writing secrets is off by default.** `app.py` only publishes env values to SSM when
  `--context write_secrets=true` (set by the Actions deploy step); it validates all values
  are present in the environment first.
- **Keep `stack.py` and `docker-compose.yml` aligned** — same containers/health checks/env;
  the compose file carries a note to that effect.
- Some resources are created **manually, not by CDK**: the `duckbot` EC2 key pair and the
  custom ECS AMI (see the inline comments in `stack.py`). Don't assume `cdk deploy`
  provisions them.
