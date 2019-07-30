"""This AWS Lambda Function kicks off a code build job."""
import httplib
import urlparse
import json
import boto3


def lambda_handler(event, context):
    """Main Lambda Handling function."""
    try:
        # Log the received event
        print "Received event: " + json.dumps(event, indent=2)
        # Setup base response
        response = get_response_dict(event)

        # CREATE UPDATE (want to avoid rebuilds unless something changed)
        if event['RequestType'] in ("Create", "Update"):
            try:
                print "Kicking off Build"
                execute_build(event)
            except Exception, exce:
                print "ERROR: Build threw exception" + exce.message
                print exce
                # Signal back that we failed
                return send_response(event, get_response_dict(event),
                                     "FAILED", exce.message)
            else:
                # We want codebuild to send the signal
                print "Build Kicked off ok CodeBuild should signal back"
                return
        elif event['RequestType'] == "Delete":
            # TODO: Remove the created images in the Repositories
            # DELETE (Let CFN delete the artifacts etc as per normal)
            # signal success to CFN
            print "Delete event nothing to do just signal back"
            cleanup_images(event)
            response['PhysicalResourceId'] = "1233244324"
            return send_response(event, response)
        else:
            # Invalid RequestType
            print "ERROR: Invalid request type send error signal to cfn"
            return send_response(event, response, "FAILED",
                                 "Invalid RequestType: Create, Update, Delete")
    except Exception, unhandled:
        response = get_response_dict(event)
        return send_response(event, response, "FAILED",
                             "Unhandled exception, failing gracefully")


def cleanup_images(event):
    """
    loop over and delete images in each repo
    """
    properties = event['ResourceProperties']
    for repository in ['ECRRepository']:
       print("Cleaning Up: " + repository)
       print("Trying to cleanup: " + properties[repository])
       cleanup_images_repo(properties[repository])


def cleanup_images_repo(repository):
    """
    Delete Container images
    """
    ecr_client = boto3.client('ecr')
    response = ecr_client.describe_images(
        registryId=globals()['account_id'],
        repositoryName=repository
    )
    imageIds = []
    for imageDetail in response['imageDetails']:
        imageIds.append(
                {
                    'imageDigest': imageDetail['imageDigest'],
                }
        )
        
    if len(imageIds):
        # delete images
        response = ecr_client.batch_delete_image(
            registryId=globals()['account_id'],
            repositoryName=repository,
            imageIds=imageIds
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
        print "Sent CFN Response"

    return response
