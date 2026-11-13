# AWS EC2 Inventory & Cost Estimation Using Python and Boto3

This project uses Python and the AWS SDK for Python (`boto3`) to discover EC2
instances across AWS regions, estimate their running costs, and generate a
consolidated CSV report.

## Features

- Discovers available AWS regions.
- Retrieves EC2 instance details across regions.
- Reports instance name, ID, state, type, architecture, launch time, and region.
- Estimates hourly, daily, and monthly running costs.
- Generates `ec2_instances.csv`.

## Use Cases

- Maintain a centralized inventory of EC2 instances.
- Estimate compute costs for budgeting and planning.
- Identify running instances and their estimated monthly costs.
- Support cloud cost optimization and unused-resource reviews.
- Provide infrastructure reports for operations, finance, and compliance teams.
- Perform regular multi-region EC2 audits.

## Prerequisites

- An active AWS account.
- Python 3.8 or later.
- AWS CLI.
- An IAM user or role with permission to describe EC2 resources and access pricing.
- Internet access.
- Linux, macOS, or Windows.

## Install the AWS CLI

### Linux

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o awscliv2.zip
unzip awscliv2.zip
sudo ./aws/install
aws --version
```

For ARM64 Linux, use the ARM64 installer from the
[AWS CLI installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html).

### macOS

```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o AWSCLIV2.pkg
sudo installer -pkg AWSCLIV2.pkg -target /
aws --version
```

### Windows

Download and install the AWS CLI from the
[AWS CLI download page](https://aws.amazon.com/cli/). Then verify it in
PowerShell:

```powershell
aws --version
```

## Configure AWS Credentials

Run:

```bash
aws configure
```

Enter your AWS access key, secret key, default region, and output format when
prompted:

```text
AWS Access Key ID: <your-access-key-id>
AWS Secret Access Key: <your-secret-access-key>
Default region name: us-east-1
Default output format: json
```

Never commit AWS credentials to this repository. Prefer IAM roles or named AWS
profiles where possible.

## Required IAM Permissions

The configured AWS identity needs permissions similar to:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeRegions",
        "ec2:DescribeInstances",
        "pricing:GetProducts"
      ],
      "Resource": "*"
    }
  ]
}
```

`pricing:GetProducts` is required by `ec2.py`. The AWS Pricing API is queried
through the `us-east-1` endpoint.

## Python Setup

Create and activate a virtual environment.

### Linux and macOS
Install the dependency:

```bash
python -m pip install --upgrade pip
pip install boto3
```

## Run the Script

Run the pricing-enabled script:

```bash
python ec2.py
```

The script creates or overwrites:

```text
ec2_instances.csv
```

## Cost Calculation

For running instances, the estimates are calculated as:

- Daily cost = hourly price × 24
- Monthly cost = hourly price × 730

Stopped or non-running instances have zero estimated running cost.

The estimates cover EC2 instance compute charges only. They do not include EBS,
Elastic IP, data transfer, load balancer, snapshot, tax, Reserved Instance, or
Savings Plans charges. Actual AWS charges may differ.

## Report Columns

The generated CSV includes:

- Instance Name
- Instance ID
- State
- Instance Type
- Architecture
- Start Time
- Region
- Hourly Price
- Daily Price
- Monthly Price

## Troubleshooting

### Access denied

Check the configured identity:

```bash
aws sts get-caller-identity
```

Then verify that the identity has the required IAM permissions.

### No instances returned

Confirm that the account contains EC2 instances and that the configured
identity can access the required regions.

### Pricing API errors

Confirm that `pricing:GetProducts` is allowed and that the Pricing API is
accessed through `us-east-1`.