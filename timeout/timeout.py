import base64
import boto3
import gzip
import json
import os
from datetime import datetime, timezone

securityhub_client = boto3.client('securityhub')

def handler(event, context):

    base64data = base64.b64decode(event['awslogs']['data'])
    gzipdata = gzip.decompress(base64data).decode()

    account = os.environ['AWS_ACCOUNT']
    region = os.environ['REGION']

    now = datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

    securityhub_response = securityhub_client.batch_import_findings(
        Findings = [
            {
                "SchemaVersion": "2018-10-08",
                "Id": region+"/"+account+"/timeout",
                "ProductArn": "arn:aws:securityhub:"+region+":"+account+":product/"+account+"/default", 
                "GeneratorId": "cwl-timeout",
                "AwsAccountId": account,
                "CreatedAt": now,
                "UpdatedAt": now,
                "Title": "Timeout",
                "Description": gzipdata,
                "Resources": [
                    {
                        "Type": "AwsLambda",
                        "Id": "arn:aws:lambda:"+region+":"+account+":function:shipit-timeout"
                    }
                ],
                "FindingProviderFields": {
                    "Confidence": 100,
                    "Severity": {
                        "Label": "HIGH"
                    },
                    "Types": [
                        "security/cwl/timeout"
                    ]
                }
            }
        ]
    )

    print(securityhub_response)

    return {
        'statusCode': 200,
        'body': json.dumps('ShipIt - Timeout')
    }