'''
This function handles a Slack slash command and echoes the details back to the user.

Follow these steps to configure the slash command in Slack:

  1. Navigate to https://<your-team-domain>.slack.com/services/new

  2. Search for and select "Slash Commands".

  3. Enter a name for your command and click "Add Slash Command Integration".

  4. Copy the token string from the integration settings and use it in the next section.

  5. After you complete this blueprint, enter the provided API endpoint URL in the URL field.


To encrypt your secrets use the following steps:

  1. Create or use an existing KMS Key - http://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html

  2. Expand "Encryption configuration" and click the "Enable helpers for encryption in transit" checkbox

  3. Paste <COMMAND_TOKEN> into the kmsEncryptedToken environment variable and click "Encrypt"

  4. Give your function's role permission for the `kms:Decrypt` action using the provided policy template


Follow these steps to complete the configuration of your command API endpoint

  1. When completing the blueprint configuration select "Open" for security
     on the "Configure triggers" page.

  2. Enter a name for your execution role in the "Role name" field.
     Your function's execution role needs kms:Decrypt permissions.

  3. Update the URL for your Slack slash command with the invocation URL for the
     created API resource in the prod stage.
'''

import boto3
import json
import logging
import os
import warnings
warnings.filterwarnings("ignore")

import aiml
bot = aiml.Kernel()
bot.learn("taina.aiml")

from base64 import b64decode
from urlparse import parse_qs

ENCRYPTED_EXPECTED_TOKEN = os.environ['kmsEncryptedToken']

kms = boto3.client('kms', region_name='us-east-1')
expected_token = kms.decrypt(
    CiphertextBlob=b64decode(ENCRYPTED_EXPECTED_TOKEN),
    EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']}
)['Plaintext']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def lambda_handler(event, context):
    params = parse_qs(event['body'])
    token = params['token'][0]
    if token != expected_token:
        logger.error("Request token (%s) does not match expected", token)
        return respond(Exception('Invalid request token'))

    user = params['user_name'][0]
    command = params['command'][0]
    channel = params['channel_name'][0]
    if 'text' in params:
        command_text = params['text'][0]
    else:
        command_text = ''

    return respond(None, "%s : %s" % (command_text, bot.respond(command_text)))

sentence = "What time is it?"
print sentence
print bot.respond(sentence)
sentence = "WHO IS AVAILABLE AT 9am ON 2021-4-20"
print sentence
print bot.respond(sentence)
sentence = "WHEN IS Beckinsale AVAILABLE ON 2021-4-20"
print sentence
print bot.respond(sentence)
sentence = "WHAT DAY IS Beckinsale AVAILABLE AT 9am"
print sentence
print bot.respond(sentence)
