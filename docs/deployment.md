# Deployment Guide

## Prerequisites

- AWS account with EC2, RDS, CloudFormation, and IAM rights
- AWS CLI configured on `eu-west-3` (for local commands only — deploy is done via console)

## Generate required secrets

**Django SECRET_KEY:**

```bash
uv run python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

**RDS password:** choose a strong password, minimum 8 characters. Alphanumeric recommended — special characters in `DATABASE_URL` require URL encoding.

## CFN deploy via AWS Console

### Step 1 — Upload template to S3

Upload `infra/cloudformation.yaml` to any S3 bucket in `eu-west-3`. Copy the S3 object URL.

### Step 2 — Create stack

CloudFormation → Create stack → Template source: Amazon S3 URL → Paste the S3 URL → Next

### Step 3 — Fill parameters

| Parameter | Value |
|-----------|-------|
| Stack name | `otomais-stack` |
| DBPassword | `<your-rds-password>` |
| DjangoSecretKey | `<generated-secret-key>` |
| AllowedSSHCidr | `<your-ip>/32` |
| LatestAmiId | leave default |

### Step 4 — IAM acknowledgement

Check "I acknowledge that AWS CloudFormation might create IAM resources with custom names" → Submit

### Step 5 — Monitor

CloudFormation → Stacks → `otomais-stack` → Events

Wait for `otomais-stack CREATE_COMPLETE`. `cfn-signal` ensures EC2 UserData completed successfully before the stack is marked done. Total time: ~15–20 minutes.

### Step 6 — Get outputs

CloudFormation → Stacks → `otomais-stack` → Outputs

`AppURL`, `ElasticIPAddress`, `RDSEndpoint`, and `SSMConnectionCommand` are all available here.

### Step 7 — Validate

```
http://<ElasticIP>/api/equipment/
http://<ElasticIP>/api/sets/
http://<ElasticIP>/admin/
```

## Connect to the instance

**Via AWS Console (recommended, no plugin needed):**

EC2 → Instances → `otomais-ec2` → Connect → Session Manager → Connect

Switch to `ec2-user` once connected:

```bash
sudo su --login ec2-user
```

**Useful commands:**

```bash
docker ps                       # container status
docker logs otomais             # app logs
docker logs otomais --tail 50   # last 50 lines
docker exec -it otomais bash    # enter container
```

## Teardown

**Stop infrastructure** (pause billing, keep data):

- EC2 → Instance state → Stop
- RDS → Actions → Stop temporarily

Note: RDS auto-restarts after 7 days — re-stop manually if needed.

**Delete everything** (destroys all resources and data):

CloudFormation → Stacks → `otomais-stack` → Delete

All resources including RDS are deleted. No final snapshot — all data is lost by design (`DeletionPolicy: Delete`).

## Architecture reference

| | |
|-|--|
| Region | eu-west-3 (Paris) |
| VPC | 10.0.0.0/16 |
| Public subnet | 10.0.1.0/24 — EC2 (eu-west-3a) |
| Private subnet A | 10.0.2.0/24 — RDS (eu-west-3a) |
| Private subnet B | 10.0.3.0/24 — RDS (eu-west-3b) |
| Compute | EC2 t3.micro, Amazon Linux 2023 |
| Database | RDS db.t4g.micro PostgreSQL 17, Single-AZ |
| Web | Nginx reverse proxy + Docker + Gunicorn |
| Access | SSM Session Manager only (no SSH, no port 22) |
| IP | Elastic IP (fixed across restarts) |

**Key decisions:**

- No SSH — SSM Session Manager only, port 22 is not open
- `gp2` storage on RDS — `gp3` is not covered by the free tier
- `DeletionPolicy: Delete` — clean teardown with no lingering costs
- `cfn-signal` + `CreationPolicy PT25M` — CloudFormation waits for UserData to complete before `CREATE_COMPLETE`
- One codebase, env-var driven: SQLite locally, RDS PostgreSQL on AWS
