import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamo_db,
    aws_events as events,
    aws_events_targets as targets
)

class ServerlessSolar(cdk.Stack):

    def __init__(self, scope: cdk.App, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "ServerlessSolarBucket-",
                           versioned=True,
                           removal_policy=cdk.RemovalPolicy.DESTROY,
                           auto_delete_objects=True)
        table_name = 'api_dump'

        lambda_fn = _lambda.Function(
            self, 'CallApi',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset('src/lambdas'),
            handler='call_api.lambda_handler',
            environment={'TABLE_NAME': table_name},
        )

        rule = events.Rule(self, "Rule",
                           schedule=events.Schedule.rate(cdk.Duration.minutes(5)),
                           )
        rule.add_target(targets.LambdaFunction(lambda_fn))

        dynamodb_table = dynamo_db.Table(
            self,
            table_name,
            table_name=table_name,
            partition_key={'name': 'ID', 'type': dynamo_db.AttributeType.STRING},
            billing_mode=dynamo_db.BillingMode.PAY_PER_REQUEST)
        dynamodb_table.grant_full_access(lambda_fn)
