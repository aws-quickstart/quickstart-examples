"""This AWS Lambda Function kicks off a code build job."""
import httplib
import urlparse
import json
import boto3
import traceback


def lambda_handler(event, context):
    """Main Lambda Handling function."""
    account_id = context.invoked_function_arn.split(":")[4]

    try:
        # Log the received event
        print("Received event: " + json.dumps(event, indent=2))

        # Setup base response
        response = get_response_dict(event)

        # CREATE UPDATE (want to avoid rebuilds unless something changed)
        if event['RequestType'] in ("Create", "Update"):
            try:
                print("Kicking off Build")
                execute_build(event)
            except Exception as build_exce:
                print("ERROR: Build threw exception")
                print(repr(build_exce))
                # Signal back that we failed
                return send_response(event, get_response_dict(event),
                                     "FAILED", repr(build_exce))
            else:
                # CodeBuild will send the signal
                print("Build Kicked off ok CodeBuild should signal back")
                return
        elif event['RequestType'] == "Delete":
            # TODO: Remove the created images in the Repositories
            print("Delete event remove container images")
            response['PhysicalResourceId'] = "1233244324"
            try:
                resources = event['ResourceProperties']
                repository = resources['ECRRepository']
                cleanup_images_repo(repository, account_id)
            except Exception as cleanup_exception:
                # signal failure to CFN
                print(json.dumps(event, indent=2))
                traceback.print_stack()
                print("---------")
                traceback.print_exc()
                print(repr(cleanup_exception))
                return send_response(event, response, "FAILED",
                                     "Cleanup of Container image failed." + repr(cleanup_exception))
            # signal success to CFN
            return send_response(event, response)
        else:
            # Invalid RequestType
            print("ERROR: Invalid request type send error signal to cfn")
            print("ERROR: Expected - Create, Update, Delete")
    except Exception as unhandled:
        response = get_response_dict(event)
        return send_response(event, response, "FAILED",
                             "Unhandled exception, failing gracefully: " + str(unhandled))


def cleanup_images_repo(repository, account_id):
    """
    Delete Container images
    """
    ecr_client = boto3.client('ecr')

    print("Repo:" + repository + " AccountID:" + account_id)
    response = ecr_client.describe_images(
        registryId=account_id,
        repositoryName=repository
    )
    image_ids = []
    for imageDetail in response['imageDetails']:
        image_ids.append(
                {
                    'imageDigest': imageDetail['imageDigest'],
                }
        )

    if len(image_ids):
        # delete images
        response = ecr_client.batch_delete_image(
            registryId=account_id,
            repositoryName=repository,
            imageIds=image_ids
        )


def execute_build(event):
    """Kickoff CodeBuild Project."""
    build = boto3.client('codebuild')
    project_name = event["ResourceProperties"]["BuildProjectName"]
    signal_url = event["ResponseURL"]
    stack_id = event["StackId"]
    request_id = event["RequestId"]
    logical_resource_id = event["LogicalResourceId"]
    url = urlparse.urlparse(event['ResponseURL'])
    response = build.start_build(
        projectName=project_name, environmentVariablesOverride=[
            {'name': 'url_path', 'value': url.path},
            {'name': 'url_query', 'value': url.query},
            {'name': 'cfn_signal_url', 'value': signal_url},
            {'name': 'cfn_stack_id', 'value': stack_id},
            {'name': 'cfn_request_id', 'value': request_id},
            {'name': 'cfn_logical_resource_id', 'value': logical_resource_id}
        ])
    return response


def get_response_dict(event):
    """Setup Response object for CFN Signal."""
    response = {
        'StackId': event['StackId'],
        'RequestId': event['RequestId'],
        'LogicalResourceId': event['LogicalResourceId'],
        'Status': 'SUCCESS'
    }
    return response


def send_response(event, response, status=None, reason=None):
    """Response sender."""
    if status is not None:
        response['Status'] = status

    if reason is not None:
        response['Reason'] = reason

    if 'ResponseURL' in event and event['ResponseURL']:
        url = urlparse.urlparse(event['ResponseURL'])
        body = json.dumps(response)
        https = httplib.HTTPSConnection(url.hostname)
        https.request('PUT', url.path+'?'+url.query, body)
        print("Sent CFN Response")

    return response
