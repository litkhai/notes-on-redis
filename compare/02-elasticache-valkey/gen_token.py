"""Print an IAM auth token for ElastiCache Serverless (run in CloudShell, which has credentials).

usage: python3 gen_token.py <cache-name> [user-id] [region]
The token is the password for AUTH <user-id> <token>; it is valid for 15 minutes, and a
connection authenticated with it stays open after that.
"""
import sys

import botocore.session
from botocore.model import ServiceId
from botocore.signers import RequestSigner

cache = sys.argv[1]
user = sys.argv[2] if len(sys.argv) > 2 else "default.iam-user"
region = sys.argv[3] if len(sys.argv) > 3 else "ap-northeast-2"
s = botocore.session.get_session()
signer = RequestSigner(ServiceId("elasticache"), region, "elasticache", "v4", s.get_credentials(), s.get_component("event_emitter"))
req = {"method": "GET", "url": f"https://{cache}/?Action=connect&User={user}&ResourceType=ServerlessCache",
       "body": {}, "headers": {}, "context": {}}
url = signer.generate_presigned_url(req, operation_name="connect", expires_in=900, region_name=region)
print(url.removeprefix("https://"))
