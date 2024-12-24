# pylint: disable=wrong-import-position
"""
TODO: update docstring

This script is triggered on a predefined basis to check and rotate Prisma Access Keys
    in AWS Secrets Manager.
    
It performs the following tasks:
    1. Grab Automation Access Keys for Prisma access from AWS Secrets Manager
    2. Grab existing Access Keys in Prisma Cloud
    Iterate over Access Keys and check the date created.
        If expired,
            Check if 2 keys already exist (keys are in buffer)
                If 2 keys exist,
                    Delete the old key if it has reached the expiration + buffer period.
                If 1 key exists,
                    Create a new key and update the value in Secrets Manager
                    A buffer period will be activated before removal of the old keys.
        If not expired,
            Do nothing.

Prerequisites:
    - Please ensure that you have configured the necessary environment variables 
        and service account credentials/permissions for the automation to work.
    - The Role attached to the Lambda function will need to be provisioned access
        to Secrets Manager for read/write capabilities.

Notes:

"""
import os
import sys
import logging
import datetime as dt
import json
sys.path.append(".")  # nopep8
from configurations.code import Configurations
from configurations.prisma import Prisma
from configurations.aws import AWS


if "AWS_LAMBDA_RUNTIME_API" in os.environ:
    LOCAL = False
else:
    LOCAL = True


def lambda_handler(event="", context=""):
    """
    TODO: docstring

    Args:
        context (LambdaContext, optional): 
            runtime environment and execution context of the Lambda function.
            Defaults to "".
    """
    ################################################################################
    # region init
    ################################################################################
    code_conf = Configurations(
        local_run=LOCAL,
        status_code=0,
        task="Initializing code configurations",
        status_text="",
    )
    prisma_conf = Prisma(
        local_run=LOCAL,
        request_offset=0,
        request_limit=50,
        debug_mode=code_conf.debug_mode
    )
    aws_conf = AWS(local_run=LOCAL, debug_mode=code_conf.debug_mode)
    ################################################################################
    # endregion init
    ################################################################################
    ################################################################################
    # region biz logic
    ################################################################################
    ################################################################################
    # region get prisma secrets
    ################################################################################
    prisma_keys = aws_conf.get_prisma_secrets()
    prisma_conf.prisma_access_key = prisma_keys["prisma_access_key"]
    prisma_conf.prisma_secret_key = prisma_keys["prisma_secret_key"]
    prisma_conf.get_cspm_token()
    prisma_conf.get_cwp_token()
    prisma_conf.get_latest_version()
    prisma_conf.set_updated_fargate_image_and_bundle()
    registry_type = ""
    registry_credentialID = ""
    
    # Loop through each cluster and get services and task definitions
    # Get list of clusters
    clusters = aws_conf.get_ecs_clusters()
    for cluster in clusters:
        logging.info(f"Accessing cluster: {cluster}")
        service_arns = aws_conf.get_cluster_services(cluster)
        for service_arn in service_arns:
            service_desc = aws_conf.get_service_desc(service_arn, cluster)
            service, is_fargate = aws_conf.is_fargate_service(service_desc)
            if is_fargate:
                logging.info(f"Service {service_arn} is Fargate, checking defended status")
                task_definition, defender_status = aws_conf.get_fargate_defender_status(prisma_conf._latest_cwp_version, service["taskDefinition"])
                if defender_status == "undefended":
                    image = task_definition['containerDefinitions'][0]['name']
                    logging.debug(f"Image: {image}")
                    extract_entrypoint = not 'entryPoint' in task_definition['containerDefinitions'][0]
                    if extract_entrypoint:
                        if not prisma_conf.check_image_in_registry(task_definition):
                            if not registry_credentialID and registry_type == "aws":
                                registry_credentialID = image.split('.')[0]
                        prisma_conf._fargate_params["extractEntrypoint"] = extract_entrypoint
                        prisma_conf._fargate_params["registryCredentialID"] = registry_credentialID

                    for attribute in prisma_conf._td_removed_attributes:
                        del task_definition[attribute]

                    protected_task = prisma_conf.generate_protected_task(prisma_conf._fargate_params, json.dumps(task_definition, indent=4, sort_keys=True, default=str))
                    logging.debug(f"protected_task: {protected_task}")
                    for container in protected_task["containerDefinitions"]:
                        if container["name"] == "TwistlockDefender" and container["logConfiguration"] == None:
                            del container["logConfiguration"]
                    new_task_definition_arn = aws_conf.register_task_definition(protected_task)
                    aws_conf.update_service(cluster, service_arn, new_task_definition_arn)
                elif defender_status == "outdated":
                    for object in task_definition["containerDefinitions"][1]["environment"]:
                        if object["name"] == "INSTALL_BUNDLE":
                            object["value"] = prisma_conf._updated_fargate_bundle
                    task_definition["containerDefinitions"][1]["image"] = prisma_conf._updated_fargate_image
                    new_task_definition_arn = aws_conf.register_task_definition(task_definition)
                    aws_conf.update_service(cluster, service_arn, new_task_definition_arn)
                else:
                    logging.info("Task definition is defended and defender is updated.")                    
                break
        break
    ################################################################################
    # endregion get prisma secrets
    ################################################################################
    

    ################################################################################
    # endregion biz logic
    ################################################################################

    return "Script finished running."

