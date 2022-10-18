# shipit

### Dependency

```python
    aws_logs_destinations as _destinations,
```

### Requirement

```python
        account = Stack.of(self).account
        region = Stack.of(self).region
```

### Error

```python
        error = _lambda.Function.from_function_arn(
            self, 'error',
            'arn:aws:lambda:'+region+':'+account+':function:shipit-error'
        )

        errorsub = _logs.SubscriptionFilter(
            self, 'errorsub',
            log_group = logs,
            destination = _destinations.LambdaDestination(error),
            filter_pattern = _logs.FilterPattern.all_terms('ERROR')
        )
```

### Timeout

```python
        timeout = _lambda.Function.from_function_arn(
            self, 'timeout',
            'arn:aws:lambda:'+region+':'+account+':function:shipit-timeout'
        )

        timesub = _logs.SubscriptionFilter(
            self, 'timesub',
            log_group = logs,
            destination = _destinations.LambdaDestination(timeout),
            filter_pattern = _logs.FilterPattern.all_terms('Task','timed','out')
        )
```
