# pylint: disable=too-many-lines, import-error, line-too-long
"""
TODO: update docstring
This file contains a collection of Prisma helper functions for automating tasks.

Functions:
- aws_initiate_secrets_manager_client()
- aws_secrets_manager_get_secret()

Usage:
- Simply import this file and call the function. For example:

    from prisma_implementation_functions import generate_prisma_token

Notes:
- Before using these functions, be sure to configure the .env appropriately.

"""
import boto3
import logging
import datetime
from typing import Optional
from botocore.exceptions import ClientError

def aws_initiate_session():
    """
    Initiate the AWS Session.

    Returns:
        AWS Session
    """

    session = boto3.session.Session()
    return session

def aws_initiate_secrets_manager_client(
         session, region: Optional[str] = ""
):
    """
    Initiate the AWS Secret Manager client.

    Returns:
        AWS Secret Manager Client
    """
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )
    return client

def aws_initiate_ecs_client(
        session, region: Optional[str] = ""
):
    """
    Initiate the AWS Secret Manager client.

    Returns:
        AWS Secret Manager Client
    """
    client = session.client(
        service_name='ecs',
        region_name=region
    )
    return client

def aws_initiate_lambda_client(
        session, region: Optional[str] = ""
):
    """
    Initiate the AWS Secret Manager client.

    Returns:
        AWS Secret Manager Client
    """
    client = session.client(
        service_name='lambda',
        region_name=region
    )
    return client

def aws_lambda_get_function(function_name: str, client, debug_mode: bool) -> dict:
    """
    Get function from AWS Lambda

    Args:
        client: AWS Lambda client
        function_name (str): Function Name

    Raises:
        ex: Client Error

    Returns:
        object: Lambda Function
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    logging.info("Getting function {}".format(function_name))
    try:
        response = client.get_function(
            FunctionName=function_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("The requested function %s was not found", function_name)
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logging.info("The request was invalid due to: %s", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logging.info("The request had invalid params: %s", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            logging.info(
                "The requested secret can't be decrypted using the provided KMS key: %s", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            logging.info("An error occurred on service side: %s", e)

    return response

def aws_ecs_get_clusters(client, debug_mode: bool) -> list:
    """
    Get all ECS clusters

    Args:
        client: AWS ECS client

    Raises:
        ex: Client Error

    Returns:
        object: List of all ECS clusters
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        clusters = []
        paginator = client.get_paginator('list_clusters')
        for page in paginator.paginate():
            clusters.extend(page['clusterArns'])
        response=clusters
        logging.info("All ECS Clusters retrieved.")

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("No clusters were found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logging.info("The request was invalid due to: %s", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logging.info("The request had invalid params: %s", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            logging.info(
                "The requested secret can't be decrypted using the provided KMS key: %s", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            logging.info("An error occurred on service side: %s", e)

    return response

def aws_ecs_get_services(cluster_name: str, client, debug_mode: bool):
    """
    Retrieve all services within a specified ECS cluster
    Args:
        client: AWS ECS client
        layer_arn: AWS Layer Arn
    Raises:
        ex: Client Error

    Returns:
        object: Lambda twistlock layer
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        services = []
        paginator = client.get_paginator('list_services')
        for page in paginator.paginate(cluster=cluster_name):
            services.extend(page['serviceArns'])
            response=services

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("No services were found")
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logging.info("The request was invalid due to: %s", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logging.info("The request had invalid params: %s", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            logging.info(
                "The requested secret can't be decrypted using the provided KMS key: %s", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            logging.info("An error occurred on service side: %s", e)

    return response

def aws_ecs_get_service_desc(service_arn, cluster_name, client, debug_mode: bool):
    """
    Get service description from AWS
    Args:
        client: AWS ECS client
        service_arn: Service ARN
        cluster_name: Cluster Name
    Raises:
        ex: Client Error

    Returns:
        Object: service
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        response = client.describe_services(cluster=cluster_name, services=[service_arn])
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("The requested function %s was not found", service_arn)
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logging.info("The request was invalid due to: %s", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logging.info("The request had invalid params: %s", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            logging.info(
                "The requested secret can't be decrypted using the provided KMS key: %s", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            logging.info("An error occurred on service side: %s", e)

    return response

def aws_ecs_is_fargate_service(service_desc, debug_mode: bool):
    """
    Check to see if Service is Fargate Service
    Args:
        client: AWS ECS client
        service_arn: Service ARN
        cluster_name: Name of ECS cluster
    Raises:
        ex: Client Error

    Returns:
        bool
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    response = False
    if 'services' in service_desc and len(service_desc['services']) > 0:
        for service in service_desc['services']:
            if 'capacityProviderStrategy' in service:
                for capacityProviderStrategy in service['capacityProviderStrategy']:
                    if capacityProviderStrategy['capacityProvider'] == 'FARGATE' and capacityProviderStrategy['weight'] > 0:
                        response = True
            
            elif 'launchType' in service:
                if service['launchType'] == "FARGATE":
                    response = True

    return service, response
    
def aws_ecs_get_fargate_defender_status(latest_version, task_definition_arn, client, debug_mode: bool):
    """
    Check to see if Fargate Service is defended, outdated, or not
    Args:
        client: AWS ECS client
        task_definition_arn: task_definition ARN
    Raises:
        ex: Client Error

    Returns:
        String - defended/outdated/undefended
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        response = "undefended"
        task_definition_desc = client.describe_task_definition(taskDefinition=task_definition_arn)
        task_definition = task_definition_desc['taskDefinition']

        for container in task_definition['containerDefinitions']:
            if container['name'] == "TwistlockDefender":
                defender_version = container["image"][-9:]               
                if defender_version == latest_version:
                    response = "defended"
                else:
                    response = "outdated"
                    logging.info(f"Current Defender Version is {defender_version}, the newest version is {latest_version}. Initiating update...")                   
                break

    except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logging.info("The requested task_definition %s was not found", task_definition_arn)
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                logging.info("The request was invalid due to: %s", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                logging.info("The request had invalid params: %s", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                logging.info(
                    "The requested secret can't be decrypted using the provided KMS key: %s", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                logging.info("An error occurred on service side: %s", e)
    
    if response == "undefended":
        logging.info("Task definition is not defended, defender deployment starting.")

    return task_definition, response

def aws_ecs_register_task_definition(task_definition: str, client, debug_mode: bool):
    """
    Register a new ECS task definition
    Args:
        client: AWS Client client
        layer_arn: AWS Layer Arn

    Raises:
        ex: Client Error

    Returns:
        object: Lambda twistlock layer
    """
    """Register a new ECS task definition"""
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        response = client.register_task_definition(**task_definition)
        return response['taskDefinition']['taskDefinitionArn']
    
    except Exception as e:
        logging.info(f"Error registering task definition: {e}")
        return None
    
def aws_ecs_update_service(cluster_name: str, service_name :str, new_task_definition: str, client, debug_mode: bool):
    """
    Register a new ECS task definition
    Args:
        client: AWS Client client
        layer_arn: AWS Layer Arn

    Raises:
        ex: Client Error

    Returns:
        object: Lambda twistlock layer
    """
    """Register a new ECS task definition"""
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        response = client.update_service(
            cluster=cluster_name,
            service=service_name,
            taskDefinition=new_task_definition
        )
        return response
    except Exception as e:
        logging.info(f"Error updating service: {e}")
        return None
    
def aws_lambda_update_function(function_name: str, layer_arn, client, debug_mode: bool) -> dict:
    """
    Get twistlock layer from AWS Lambda

    Args:
        client: AWS Lambda client
        layer_arn: AWS Layer Arn

    Raises:
        ex: Client Error

    Returns:
        object: Lambda twistlock layer
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
        
    logging.info("Updating function with new layer")
    response = client.update_function_configuration(
        FunctionName=function_name,
        Layers=[layer_arn]
    )

    return response

def aws_lambda_get_layer(layer_arn, client, debug_mode: bool) -> dict:
    """
    Get twistlock layer from AWS Lambda

    Args:
        client: AWS Lambda client
        layer_arn: AWS Layer Arn

    Raises:
        ex: Client Error

    Returns:
        object: Lambda twistlock layer
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    logging.info("Getting twistlock layer")
    try:
        response = client.get_layer_version_by_arn(
            Arn=layer_arn
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("The requested layer %s was not found", layer_arn)
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            logging.info("The request was invalid due to: %s", e)
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            logging.info("The request had invalid params: %s", e)
        elif e.response['Error']['Code'] == 'DecryptionFailure':
            logging.info(
                "The requested secret can't be decrypted using the provided KMS key: %s", e)
        elif e.response['Error']['Code'] == 'InternalServiceError':
            logging.info("An error occurred on service side: %s", e)

    return response

def aws_lambda_publish_layer(layer_arn, zip_file, runtimes, client, debug_mode: bool) -> dict:
    """
    Publish twistlock layer from AWS Lambda with new Serverless zip

    Args:
        client: AWS Lambda client
        layer_arn: AWS Layer Arn

    Raises:
        ex: Client Error

    Returns:
        object: Lambda twistlock layer
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )

    logging.info("Publishing twistlock layer")
    response = client.publish_layer_version(
        LayerName=layer_arn,
        Description="Twistlock layer updated by Prisma Automation on {}".format(datetime.datetime.now()),
        Content={
            'ZipFile': zip_file
        },
        CompatibleRuntimes=runtimes
    )

    return response

def aws_secrets_manager_get_secret(client, secret_name: str, debug_mode: bool) -> dict:
    """
    Get secret from AWS Secret Manager

    Args:
        client: AWS Secret Manager client
        secret_name (str): Secret Name

    Raises:
        ex: Client Error

    Returns:
        list: Secret metadata
    """
    if debug_mode:
        logging.debug(
            "API READ_REQUEST \u2713: sending the request through."
        )
    try:
        response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as ex:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise ex

    return response

def aws_secrets_manager_update_secret_value(client, secret_name: str, secret_value: str, debug_mode: bool) -> bool:
    """
    Update secret in AWS Secret Manager

    Args:
        client: AWS Secret Manager client
        secret_name (str): Secret Name
        secret_value (str): Secret Value

    Raises:
        ex: Client Error

    Returns:
        list: Secret metadata
    """
    if debug_mode:
        logging.info(
            "API PUT_REQUEST \u2717: not sending the request.")

        return False

    try:
        response = client.put_secret_value(
            SecretId=secret_name,
            SecretString=secret_value,
        )

        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("The requested secret %s was not found", secret_name)

    return False

def aws_secrets_manager_create_secret(client, secret_name: str, secret_value: str, debug_mode: bool) -> bool:
    """
    Create secret in AWS Secret Manager

    Args:
        client: AWS Secret Manager client
        secret_name (str): Secret Name
        secret_value (str): Secret Value

    Raises:
        ex: Client Error

    Returns:
        list: Secret metadata
    """
    if debug_mode:
        logging.info(
            "API CREATE_REQUEST \u2717: not sending the request.")

        return False
    try:
        response = client.create_secret(
            Description="Secret managed by Prisma automation.",
            Name=secret_name,
            SecretString=secret_value,
        )

        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            logging.info("The requested secret %s was not found", secret_name)

    return False
