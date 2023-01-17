import cdk_nag

from aws_cdk import (
    Aspects,
    Duration,
    Stack,
    RemovalPolicy,
    aws_iam as _iam,
    aws_lambda as _lambda,
    aws_logs as _logs
)

from constructs import Construct

class ShipitStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Aspects.of(self).add(
            cdk_nag.AwsSolutionsChecks(
                log_ignores = True,
                verbose = True
            )
        )

        cdk_nag.NagSuppressions.add_stack_suppressions(
            self, suppressions = [
                {'id': 'AwsSolutions-IAM4','reason': 'GitHub Issue'}
            ]
        )

    ### LAMBDA LAYER ###

        account = Stack.of(self).account
        region = Stack.of(self).region

        layer = _lambda.LayerVersion.from_layer_version_arn(
            self, 'layer',
            layer_version_arn = 'arn:aws:lambda:'+region+':070176467818:layer:getpublicip:3'
        )

    ### IAM ROLE ###

        role = _iam.Role(
            self, 'role', 
            assumed_by = _iam.ServicePrincipal(
                'lambda.amazonaws.com'
            )
        )

        role.add_managed_policy(
            _iam.ManagedPolicy.from_aws_managed_policy_name(
                'service-role/AWSLambdaBasicExecutionRole'
            )
        )

        role.add_to_policy(
            _iam.PolicyStatement(
                actions = [
                    'securityhub:BatchImportFindings'
                ],
                resources = [
                    'arn:aws:securityhub:'+region+':'+account+':product/'+account+'/default'
                ]
            )
        )

    ### ERROR ###

        error = _lambda.Function(
            self, 'error',
            function_name = 'shipit-error',
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('error'),
            handler = 'error.handler',
            role = role,
            environment = dict(
                ACCOUNT = account,
                REGION = region
            ),
            architecture = _lambda.Architecture.ARM_64,
            timeout = Duration.seconds(60),
            memory_size = 256,
            layers = [
                layer
            ]
        )

        errorlogs = _logs.LogGroup(
            self, 'errorlogs',
            log_group_name = '/aws/lambda/'+error.function_name,
            retention = _logs.RetentionDays.ONE_WEEK,
            removal_policy = RemovalPolicy.DESTROY
        )

    ### TIME OUT ###

        timeout = _lambda.Function(
            self, 'timeout',
            function_name = 'shipit-timeout',
            runtime = _lambda.Runtime.PYTHON_3_9,
            code = _lambda.Code.from_asset('timeout'),
            handler = 'timeout.handler',
            role = role,
            environment = dict(
                ACCOUNT = account,
                REGION = region
            ),
            architecture = _lambda.Architecture.ARM_64,
            timeout = Duration.seconds(60),
            memory_size = 256,
            layers = [
                layer
            ]
        )

        timeoutlogs = _logs.LogGroup(
            self, 'timeoutlogs',
            log_group_name = '/aws/lambda/'+timeout.function_name,
            retention = _logs.RetentionDays.ONE_WEEK,
            removal_policy = RemovalPolicy.DESTROY
        )
