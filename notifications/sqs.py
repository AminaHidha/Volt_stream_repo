import json
import os

import boto3


def send_notification_to_sqs(fcm_token, title, body, url="/"):
    """
    Send notification message to AWS SQS queue
    which triggers Lambda to send Firebase push notification
    """
    try:
        # Read service account file
        service_account_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "firebase-service-account.json",
        )

        with open(service_account_path, "r") as f:
            service_account = json.load(f)

        # Create SQS client
        sqs = boto3.client(
            "sqs",
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=os.environ.get("AWS_REGION", "eu-north-1"),
        )

        # Message payload
        message = {
            "fcm_token": fcm_token,
            "title": title,
            "body": body,
            "url": url,
            "project_id": "voltstream-3ca02",
            "service_account": service_account,
        }

        # Send to SQS
        queue_url = os.environ.get("AWS_SQS_QUEUE_URL")

        response = sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))

        print(f"SQS Message sent: {response['MessageId']}")
        return True

    except Exception as e:
        print(f"SQS Error: {str(e)}")
        return False
