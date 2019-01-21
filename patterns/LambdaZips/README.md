# Lambda Zips

This pattern enables templates that include Lambda functions to be deployed in any region without needing to manually 
create and populate additional regional buckets containing function zips.

## Example implementation

[Full example template including custom resource source code.](/patterns/LambdaZips/example.yaml)

## Usage:
```yaml
Resources:
  # Create a bucket in the local region
  LambdaZipsBucket:
    Type: AWS::S3::Bucket
  # Copy zip files from source bucket
  CopyZips:
    Type: Custom::CopyZips
    Properties:
      ServiceToken: !GetAtt 'CopyZipsFunction.Arn'
      DestBucket: !Ref 'LambdaZipsBucket'
      SourceBucket: !Ref 'QSS3BucketName'
      Prefix: !Ref 'QSS3KeyPrefix'
      Objects:
        - functions/packages/MyFunction/lambda.zip
  # Your lambda function
  MyFunction:
    # DependsOn is required to ensure copy is complete before creating the function
    DependsOn: CopyZips
    Type: AWS::Lambda::Function
    Properties:
      Code:
        # points to regional bucket
        S3Bucket: !Ref 'LambdaZipsBucket'
        S3Key: !Sub '${QSS3KeyPrefix}functions/packages/MyFunction/lambda.zip'
    ...
```