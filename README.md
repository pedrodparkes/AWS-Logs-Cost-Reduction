### LogGroupCostReduction
#### Set of scripts necessary for identifying huge log groups, obsolete log-groups, log-groups with never-expires retention and clean up space.

Running:
```shell
export AWS_PROFILE=<profile>
source venv/bin/activate
python log-group-detailed-optimized.py
```

*Configure AWS CLI first.

Report example:

| Region    | Retention Period | Log Group Name | Stored Data Size, GB | Last Ingestion Time |
|-----------|------------------|----------------|----------------------|---------------------|
| us-west-2 | Never Expire     | /aws/batch/job | 32.04                | 2024-07-19          |

