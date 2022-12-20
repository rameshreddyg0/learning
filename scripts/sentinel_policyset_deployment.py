#!/usr/bin/env python3

import argparse
import constant
import json
from jsonschema import validate, ValidationError, SchemaError
import os
import requests
import sys
import utilities

"""
Class Name : PolicySetDeployment
Class Description : This class implements the check and deployment of Sentinel Policy Set in Terraform Cloud for the Given Cloud Provider
"""


class PolicySetDeployment:
    """
    Method Name : __init__
    Method Description : Initializes the PolicySetDeployment object with cloud provider, deployment properties, branch on which the object is invoked
                         and validate if deployment has to proceed
    Method Arguments :   self : Object of the class on which sentinel policies are to be deployed
                         cloud_provider : Cloud Platform on which sentinel policies are to be deployed
                         deployment_properties_json_file : File with deployment properties
                         branch : Branch that will be referred from the policyset in TFE
    """

    def __init__(self, cloud_provider, artifact_dir, deployment_properties_json_file, branch):
        self.content_type = "application/vnd.api+json"
        self.schema_to_validate = 'schema.json'
        self.cloud_provider = cloud_provider
        self.artifact_dir = artifact_dir
        self.deployment_properties_json_file = deployment_properties_json_file
        self.new_policysets_properties = []
        self.update_policysets_properties = []
        self.branch = branch
        deployment_properties = self.get_deployment_properties()

        # In case of deployment flag not set or set to true without any deployment properties
        if not deployment_properties[constant.TRIGGER_DEPLOYMENT]:
            utilities.print_error(
                "Either Sentinel Policy Deployment not targeted or required properties not found for {0} !!".format(self.cloud_provider))
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            error_message = "Either Sentinel Policy Deployment not targeted or required properties not found for {0} !!".format(
                self.cloud_provider)
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            sys.exit(1)

        # Read or fetch policy set properties and tokens only incase of proceeding with policy set deployment
        else:
            utilities.print_notification(deployment_properties.get(
                constant.NEW_POLICY_SET_PROPERTIES))
            if not (deployment_properties.get(constant.NEW_POLICY_SET_PROPERTIES) is None):
                if (deployment_properties.get(constant.NEW_POLICY_SET_PROPERTIES)):
                    self.new_policysets_properties = deployment_properties[
                        constant.NEW_POLICY_SET_PROPERTIES]
                    utilities.print_notification("Policy Sets yo be created {newPolicySets}".format(
                        newPolicySets=self.new_policysets_properties))
                    create_policy_message = "Policy Sets yo be created {newPolicySets}".format(
                        newPolicySets=self.new_policysets_properties)
                    self.sentinel_deploy = open(
                        self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                    self.sentinel_deploy.write(
                        utilities.construct_html_message_success(create_policy_message))
                    self.sentinel_deploy.close()

            if (deployment_properties.get(constant.UPDATE_POLICY_SET_PROPERTIES)):
                self.update_policysets_properties = deployment_properties[
                    constant.UPDATE_POLICY_SET_PROPERTIES]
                utilities.print_notification("Policy Sets to be updated {updatePolicySets}".format(
                    updatePolicySets=self.update_policysets_properties))
                update_policy_message = "Policy Sets to be updated {updatePolicySets}".format(
                    updatePolicySets=self.update_policysets_properties)
                self.sentinel_deploy = open(
                    self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                self.sentinel_deploy.write(
                    utilities.construct_html_message_success(update_policy_message))
                self.sentinel_deploy.close()

            self.tfe_api_token = os.environ['TFE_API_KEY']
            self.dev_tfe_oauth_token = os.environ['DEV_TFE_OAUTH_TOKEN']
            self.prod_tfe_oauth_token = os.environ['PROD_TFE_OAUTH_TOKEN']
            self.tfe_api_url = deployment_properties[constant.TFE_API_URL]
            utilities.print_notification(self.dev_tfe_oauth_token)
            utilities.print_notification("Reading Production Token")
            utilities.print_notification(self.prod_tfe_oauth_token)

    """
    Method Name:        get_schema
    Method Description: Method that loads and returns schema object. Typically this will be used for json validation
    Method Arguments:   self : Object of the class on Which this method is invoked
    Method Returns:     Schema object for the schema file supplied
    """

    def get_schema(self):
        utilities.print_notification(
            "Accessing Schema that JSON to be validated against")
        with open(self.schema_to_validate, encoding='utf-8') as file:
            try:
                schema = json.load(file)
            except OSError as e:
                utilities.print_error(
                    "Failed to load the schema file: schema.json. Suspending the deployment. Please try again")
                error_message = "Failed to load the schema file: schema.json. Suspending the deployment. Please try again"
                self.sentinel_deploy = open(
                    self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                self.sentinel_deploy.write(
                    utilities.construct_html_message_error(error_message))
                self.sentinel_deploy.close()
                sys.exit(1)
            return schema

    """
    Method Name:        validate_json
    Method Description: Method to validate the provided json file and confirms if validation succeeded or failed
    Method Arguments:   self : Object of the class on which the methos is invoked
                        deployment_properties : json object that to be validated against the schema
    Method Returns: 
    """

    def validate_json(self, deployment_properties):
        utilities.print_notification(
            "Validating the JSON against schema provided")
        schema_for_validation = self.get_schema()
        try:
            validate(instance=deployment_properties,
                     schema=schema_for_validation)
        except ValidationError as err:
            utilities.print_error(err)
            utilities.print_error(
                "Deployment Properties seems not to be well formed. Please provide all required deployment properties and try again")
            error_message = "Deployment Properties seems not to be well formed. Please provide all required deployment properties and try again"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            return False
        except SchemaError as err:
            utilities.print_error(err)
            utilities.print_error(
                "Schema seems not to be well formed. Deployment will not proceed without validating the properties json. Please fic the schema and try again")
            error_message = "Schema seems not to be well formed. Deployment will not proceed without validating the properties json. Please fic the schema and try again"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            return False

        return True

    """
    Method Name:        get_deployment_properties
    Method Description: Method to read/retrieve deployment properties for given cloud provider
    Method Arguments:   self : Object of the class on which this method is invoked
    """

    def get_deployment_properties(self):
        deployment_properties_file = "../{deployment_properties_file}".format(
            deployment_properties_file=self.deployment_properties_json_file)
        if (os.path.isfile(deployment_properties_file)):
            utilities.print_notification("Deployment Properties File Found")
            success_message = "Deployment Properties File Found"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_success(success_message))
            self.sentinel_deploy.close()
        else:
            utilities.print_error("Deployment Properties File Not Found")
            error_message = "Deployment Properties File Found"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            sys.exit(1)

        try:
            with open(deployment_properties_file, encoding='utf-8') as fp:
                try:
                    utilities.print_notification(
                        "Reading Deployment Properties")
                    deployment_properties_object = json.load(fp)
                    json_validation_status = self.validate_json(
                        deployment_properties_object)
                    if not json_validation_status:
                        utilities.print_error(
                            "Deployment Properties Validation Failed!! Please provide all required deployment properties and try again")
                        error_message = "Deployment Properties Validation Failed!! Please provide all required deployment properties and try again"
                        self.sentinel_deploy = open(
                            self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                        self.sentinel_deploy.write(
                            utilities.construct_html_message_error(error_message))
                        self.sentinel_deploy.close()
                        sys.exit(1)
                    else:
                        utilities.print_success("JSON Validation Succeeded")
                        success_message = "JSON Validation Succeeded"
                        self.sentinel_deploy = open(
                            self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                        self.sentinel_deploy.write(
                            utilities.construct_html_message_success(success_message))
                        self.sentinel_deploy.close()
                except OSError:
                    utilities.print_error("Invalid Properties in {0}".format(
                        self.deployment_properties_json_file))
                    error_message = "Invalid Properties in {0}".format(
                        self.deployment_properties_json_file)
                    self.sentinel_deploy = open(
                        self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                    self.sentinel_deploy.write(
                        utilities.construct_html_message_error(error_message))
                    self.sentinel_deploy.close()
                    sys.exit(1)
        except (IOError, OSError):
            utilities.print_error("Failed to Open {0}. Please make sure JSON is well formed".format(
                self.deployment_properties_json_file))
            error_message = "Failed to Open {0}. Please make sure JSON is well formed".format(
                self.deployment_properties_json_file)
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            sys.exit(1)

        return deployment_properties_object[cloud_provider][constant.SENTINEL]

    """
    Method Name:        update_policy_set
    Method Description: Updates the policy set in accordance with the provided properties
    Method Arguments:   self : Object of the class on which this methos is invoked
                        policyset_id : ID of the policy set to be updated
                        policyset : Details with which policy set will be updated with 
    """

    def update_policy_set(self, policyset_id, policyset, oauth_token_id):
        uri = "policy-sets/{policy_set_id}".format(policy_set_id=policyset_id)
        session = requests.Session()
        utilities.set_api_token(session, self.tfe_api_token)
        utilities.set_content_type(session, self.content_type)
        utilities.print_notification(
            "Updating Policy Set : {policy_set}".format(policy_set=policyset))

        # Filling in the VCS REPO Information required for API
        vcs_repo = {}
        vcs_repo[constant.INGRESS_MODULES] = False
        vcs_repo[constant.BRANCH] = "{branch}".format(branch=self.branch)
        if not (policyset.get(constant.VCS_REPO_IDENTIFIER) is None):
            vcs_repo[constant.IDENTIFIER] = "{identifier}".format(
                identifier=policyset[constant.VCS_REPO_IDENTIFIER])

        if not (policyset.get(constant.IS_OAUTH_TOKEN_TO_UPDATE) is None) and policyset[constant.IS_OAUTH_TOKEN_TO_UPDATE]:
            vcs_repo[constant.OAUTH_TOKEN_ID] = "{oauth_token_id}".format(
                oauth_token_id=oauth_token_id)

        # Filling in the Attributes required for API
        attributes = {}
        attributes[constant.NAME] = "{policy_set_name}".format(
            policy_set_name=policyset[constant.POLICY_SET_NAME])
        attributes[constant.GLOBAL] = policyset[constant.APPLY_TO_ALL_WORKSPACES]

        if not (policyset.get(constant.POLICY_SET_DESCRIPTION) is None):
            attributes[constant.DESCRIPTION] = "{description}".format(
                description=policyset[constant.POLICY_SET_DESCRIPTION])

        if not (policyset.get(constant.POLICIES_PATH_KEY) is None):
            attributes[constant.POLICIES_PATH] = "{policy_path}".format(
                policy_path=policyset[constant.POLICIES_PATH_KEY])

        if not (policyset.get(constant.VCS_REPO_IDENTIFIER) is None):
            attributes[constant.VCS_REPO] = vcs_repo

        # Filling in the DATA required for API
        data = {}
        data[constant.TYPE] = "{policy_sets}".format(
            policy_sets=constant.POLICY_SETS)
        data[constant.ATTRIBUTES] = attributes

        # Preparing the payload required for API
        payload = {}
        payload[constant.DATA] = data

        utilities.print_notification("Printing Payload JSON")
        payload_json = json.dumps(payload)
        utilities.print_notification(payload_json)
        response = session.patch(self.tfe_api_url+uri, data=payload_json)
        utilities.print_notification(
            "Policy Set Updation Response Text: {responseText}".format(responseText=response.text))
        response_json = json.loads(response.text)
        # Attach Workspace to policy Set
        if(policyset[constant.APPLY_TO_ALL_WORKSPACES] == False and len(policyset[constant.LIST_OF_WORKSPACES])):
            utilities.print_notification("Going to attach Workspace to Policy Set {policy_set_name}".format(
                policy_set_name=policyset[constant.POLICY_SET_NAME]))

            self.attach_workspace_to_policy_set(policyset_id, policyset)

        if response.status_code == constant.POLICY_SET_UPDATE_SUCCESS:
            utilities.print_success("Policy Set Update Successful")
            update_policy_success = "Policy Set update for {policy_set_name} Successful".format(
                policy_set_name=policyset[constant.POLICY_SET_NAME])
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_success(update_policy_success))
            self.sentinel_deploy.close()
        elif response.status_code == constant.POLICY_SET_UPDATE_FAIL_NOT_FOUND_OR_UNAUTHORIZED_ACCESS:
            utilities.print_error(
                "Policy Set Update Failure : Policy set not found or user unauthorized to perform action")
            error_message = "Policy Set Update Failure : Policy set not found or user unauthorized to perform action"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            if not (response_json[constant.ERRORS] is None):
                for error in response[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
                    utilities.print_error(
                        constant.ERROR_DETAIL+error[constant.DETAIL])
                sys.exit(1)
        elif response.status_code == constant.POLICY_SET_FAILURE_MALFORMED_REQUEST:
            utilities.print_error(
                "Policy Set Update Failure : Malformed request body")
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
                    utilities.print_error(
                        constant.ERROR_DETAIL+error[constant.DETAIL])
            sys.exit(1)
        else:
            utilities.print_error("Unknow Error")
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
                    utilities.print_error(
                        constant.ERROR_DETAIL+error[constant.DETAIL])
            sys.exit(1)

        return response.text

    """
    Method Name :        attach_workspace_to_policyset
    Method Description : Method to attach the list of workspace to given policy set id
    Method Arguments :   self : Object of the class on which this method is invoked
                         policyset_id : ID of the policy set to be updated
                         policyset : Details with which policy set will be updated with
    """

    def attach_workspace_to_policy_set(self, policyset_id, policyset):
        uri = "policy-sets/{policy_set_id}/relationships/workspaces".format(
            policy_set_id=policyset_id)
        session = requests.Session()
        utilities.set_api_token(session, self.tfe_api_token)
        utilities.set_content_type(session, self.content_type)

        payload = {}
        payload[constant.DATA] = []
        workspace_details = {}
        for worksapce in policyset[constant.LIST_OF_WORKSPACES]:
            workspace_details = {}
            workspace_details[constant.ID] = worksapce
            workspace_details[constant.TYPE] = constant.WORKSPACES
            payload[constant.DATA].append(workspace_details)

        payload_json = json.dumps(payload)
        utilities.print_notification(
            "Payload JSON = {payload_json}".format(payload_json=payload_json))

        response = session.post(self.tfe_api_url+uri, data=payload_json)
        if response.status_code == constant.POLICY_SET_ATTACH_WORKSPACE_SUCCESS:
            utilities.print_success(
                "Policy Set Update Successful : Attached worksapce to Policy Set")
        else:
            response_json = json.loads(response.text)
            if response.status_code == constant.POLICY_SET_NOT_FOUND_OR_UNAUTHORIZED_ACCESS:
                utilities.print_error(
                    "Policy Set Update : Failed to attach workspace : Organization not found, or user unauthorized to perform action")
                if not (response_json[constant.ERRORS] is None):
                    for error in response_json[constant.ERRORS]:
                        utilities.print_error(
                            constant.ERROR_SUMMARY+error[constant.TITLE])
                        utilities.print_error(
                            constant.ERROR_DETAIL+error[constant.DETAIL])
                sys.exit(1)
            elif response.status_code == constant.POLICY_SET_FAILURE_MALFORMED_REQUEST:
                utilities.print_error(
                    "Policy Set Update : Failed to attach workspace : Malformed request body")
                if not (response_json[constant.ERRORS] is None):
                    for error in response_json[constant.ERRORS]:
                        utilities.print_error(
                            constant.ERROR_SUMMARY+error[constant.TITLE])
                        utilities.print_error(
                            constant.ERROR_DETAIL+error[constant.DETAIL])
                sys.exit(1)
            else:
                utilities.print_error(constant.UNKNOWN_ERROR)
                if not (response_json[constant.ERRORS] is None):
                    for error in response_json[constant.ERRORS]:
                        utilities.print_error(
                            constant.ERROR_SUMMARY+error[constant.TITLE])
                        utilities.print_error(
                            constant.ERROR_DETAIL+error[constant.DETAIL])
                sys.exit(1)

        return response.text

    """
    Method Name :        create_policy_set
    Method Description : Creates the policy set in accordance with provided properties
    Method Arguments :   self : Object of the class on which this method is invoked
                         policy_set_property : Details of the policy set to be created
    """

    def create_policy_set(self, policyset, oauth_token_id):
        uri = 'organizations/{tfe_org_name}/policy-sets'.format(
            tfe_org_name=policyset[constant.TFE_ORG_NAME])
        session = requests.Session()
        utilities.set_api_token(session, self.tfe_api_token)
        utilities.set_content_type(session, self.content_type)

        utilities.print_notification(
            "In Create policyset for - {0}".format(self.cloud_provider))
        utilities.print_notification(
            "Creating Policy Set for - {0}".format(policyset))
        utilities.print_notification(
            "Deployment Branch (policyset)- {0}".format(self.branch))

        # Filling in the VCS REPO Information required for API
        vcs_repo = {}
        vcs_repo[constant.INGRESS_MODULES] = False
        vcs_repo[constant.BRANCH] = "{branch}".format(branch=self.branch)
        vcs_repo[constant.IDENTIFIER] = "{identifier}".format(
            identifier=policyset[constant.VCS_REPO_IDENTIFIER])
        vcs_repo[constant.OAUTH_TOKEN_ID] = "{oauth_token}".format(
            oauth_token=oauth_token_id)

        # Filling in the ATTRIBUTES required for API
        attributes = {}
        attributes[constant.NAME] = "{policy_set_name}".format(
            policy_set_name=policyset[constant.POLICY_SET_NAME])
        attributes[constant.GLOBAL] = policyset[constant.APPLY_TO_ALL_WORKSPACES]
        attributes[constant.DESCRIPTION] = "{description}".format(
            description=policyset[constant.POLICY_SET_DESCRIPTION])
        attributes[constant.POLICIES_PATH] = "{policy_path}".format(
            policy_path=policyset[constant.POLICIES_PATH_KEY])
        attributes[constant.VCS_REPO] = vcs_repo

        # Filling in the DATA required for API
        data = {}
        data[constant.TYPE] = "{policy_sets}".format(
            policy_sets=constant.POLICY_SETS)
        data[constant.ATTRIBUTES] = attributes

        if not (policyset[constant.APPLY_TO_ALL_WORKSPACES]):
            if len(policyset[constant.LIST_OF_WORKSPACES]):
                # Filling in the workspaces that a policy set to be applied to
                workspaces = {}
                workspaces[constant.DATA] = []
                workspace_details = {}
                for workspace_id in policyset[constant.LIST_OF_WORKSPACES]:
                    workspace_details = {}
                    workspace_details[constant.ID] = workspace_id
                    workspace_details[constant.TYPE] = constant.WORKSPACES
                    workspaces[constant.DATA].append(workspace_details)

                relationships = {}
                relationships[constant.WORKSPACES] = workspaces
                data[constant.RELATIONSHIPS] = relationships
            else:
                utilities.print_error(
                    "Create Policy Sets : Required inforamtion of workspaces to which policy set to be updated not provided!")
                error_message = "Create Policy Sets : Required inforamtion of workspaces to which policy set to be updated not provided!"
                self.sentinel_deploy = open(
                    self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                self.sentinel_deploy.write(
                    utilities.construct_html_message_error(error_message))
                self.sentinel_deploy.close()
                sys.exit(1)

        # Preparing the payload required for API
        payload = {}
        payload[constant.DATA] = data

        utilities.print_notification("Printing Payload JSON")
        utilities.print_notification(payload)
        payload_json = json.dumps(payload)
        utilities.print_notification(payload_json)
        utilities.print_notification(self.tfe_api_url+uri)
        response = session.post(self.tfe_api_url+uri, data=payload_json)
        response_json = json.loads(response.text)
        utilities.print_notification(
            "Policy Set Creation Response: {response}".format(response=response))
        utilities.print_notification(
            "Policy Set Creation Response Text: {responseText}".format(responseText=response.text))

        if response.status_code == constant.POLICY_SET_CREATION_SUCCESS:
            utilities.print_success("Policy Set Creation Successful")
            create_policy_success_message = "Policy Set Creation for {policy_set_name} Successful".format(
                policy_set_name=policyset[constant.POLICY_SET_NAME])
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_success(create_policy_success_message))
            self.sentinel_deploy.close()
        elif response.status_code == constant.POLICY_SET_CREATE_FAIL_ORG_NOT_FOUND_OR_UNAUTHORIZED_ACCESS:
            utilities.print_error(
                "Policy Set Creation Failure : Organization not found, or user unauthorized to perform action")
            error_message = "Policy Set Creation Failure for {policy_set_name}: Organization not found, or user unauthorized to perform action".format(
                policy_set_name=policyset[constant.POLICY_SET_NAME])
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')

            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
                    utilities.print_error(
                        constant.ERROR_DETAIL+error[constant.DETAIL])
            sys.exit(1)
        elif response.status_code == constant.POLICY_SET_FAILURE_MALFORMED_REQUEST:
            utilities.print_error(
                "Policy Set Update : Failed to attach workspace : Malformed request body")
            error_message = "Policy Set Creation Failure for {policy_set_name}: Malformed request body".format(
                policy_set_name=policyset[constant.POLICY_SET_NAME])
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
                    utilities.print_error(
                        constant.ERROR_DETAIL+error[constant.DETAIL])
            sys.exit(1)
        else:
            utilities.print_error(constant.UNKNOWN_ERROR)
            error_message = "Policy Set Creation Failure for {policy_set_name}: Unknown Error".format(
                policy_set_name=policyset[constant.POLICY_SET_NAME])
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
            sys.exit(1)

        return response.text

    """
    Method Name :        list_policy_sets
    Method Description : Method to get the list of policy sets for the given organization
    Method Arguments :   self : Object of the class on which this method is invoked
                         tfe_org : Terraform Organization on which the policy sets have to be retieved
    """

    def list_policy_sets(self, tfe_org):
        utilities.print_notification("Listing the policy sets for Org: {tfe_api_url}".format(
            tfe_api_url=self.tfe_api_token))
        uri = "organizations/{tfe_org}/policy-sets".format(tfe_org=tfe_org)
        session = requests.Session()
        utilities.set_api_token(session, self.tfe_api_token)
        response = session.get(self.tfe_api_url+uri)
        response_json = json.loads(response.text)

        if response.status_code == constant.POLICY_SET_LISTING_SUCCESS:
            utilities.print_success("Policy Set Listing Successful")
            list_policy_sucess_message = "Policy Set Listing Successful"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(list_policy_sucess_message))
            self.sentinel_deploy.close()
        elif response.status_code == constant.POLICY_SET_CREATE_FAIL_ORG_NOT_FOUND_OR_UNAUTHORIZED_ACCESS:
            utilities.print_error(
                "Policy Set Listing Failure : Organization not found, or user unauthorized to perform action")
            error_message = "Policy Set Listing Failure : Organization not found, or user unauthorized to perform action"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
                    utilities.print_error(
                        constant.ERROR_DETAIL+error[constant.DETAIL])
            sys.exit(1)
        else:
            utilities.print_error(constant.UNKNOWN_ERROR)
            error_message = "Policy Set Listing Failure : Unknown Error"
            self.sentinel_deploy = open(
                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
            self.sentinel_deploy.write(
                utilities.construct_html_message_error(error_message))
            self.sentinel_deploy.close()
            if not (response_json[constant.ERRORS] is None):
                for error in response_json[constant.ERRORS]:
                    utilities.print_error(
                        constant.ERROR_SUMMARY+error[constant.TITLE])
            sys.exit(1)

        return response.text

    """
    Method Name :        is_policy_set_exists_to_update
    Method Description : Method to get the list of policy sets for the given organization
    Method Arguments :   self : Object of the class on which this method is invoked
                         policySetName : Name of the policy set that is to be checked if present in the list of policies supplied
                         policysets_list : List of policy sets
    Returns :            boolean : Returns True, If the name of the policy set is present in list of policies
    
    """

    def is_policy_set_exists_to_update(self, policySetName, policysets_list):
        for policyset in policysets_list[constant.DATA]:
            if policySetName == policyset[constant.ATTRIBUTES][constant.NAME]:
                utilities.print_notification(
                    "The Policy set with name {policy_set_name} exist in Terraform Enterprise".format(policy_set_name=policySetName))
                return policyset[constant.ID]

        utilities.print_notification(
            "The Policy set with name {policy_set_name} does not exist in Terraform Enterprise".format(policy_set_name=policySetName))
        return ""

    """
    Method Name :        process_policy_sets_deployment
    Method Description : Processes the creation or Updating Sentinel Policy Sets for given Cloud Provider with given properties
    Method Arguments :   self : Object of the class on which this method is invoked
    """

    def process_policy_sets_deployment(self):
        oauth_token_id = self.dev_tfe_oauth_token
        if (len(self.new_policysets_properties)):
            utilities.print_notification("Process creation of new policy sets")
            for policy_set_property in self.new_policysets_properties:
                utilities.print_notification(
                    "Policy Set to be created = {0}".format(policy_set_property))
                if policy_set_property[constant.TFE_ORG_NAME] == constant.PROD_TFE_ORG:
                    oauth_token_id = self.prod_tfe_oauth_token
                    utilities.print_notification(
                        "Took prod oauth token {oauth_token}".format(oauth_token=oauth_token_id))
                    utilities.print_notification("Took prod oauth token {self_oauth_token}".format(
                        self_oauth_token=self.prod_tfe_oauth_token))
                policy_creation_response = self.create_policy_set(
                    policy_set_property, oauth_token_id)
                utilities.print_notification("Policy Creation Status : {policy_creation_status}".format(
                    policy_creation_status=policy_creation_response))

        if (len(self.update_policysets_properties)):
            for policy_set_to_update_in_org in self.update_policysets_properties:
                if policy_set_to_update_in_org[constant.TFE_ORG_NAME] == constant.PROD_TFE_ORG:
                    oauth_token_id = self.prod_tfe_oauth_token

                list_policysets_response = self.list_policy_sets(
                    policy_set_to_update_in_org[constant.TFE_ORG_NAME])
                policysets_list = json.loads(list_policysets_response)

                for policyset_to_update in policy_set_to_update_in_org[constant.UPDATE_POLICY_SET_DETAILS]:
                    policyset_id = policyset_to_update[constant.POLICY_SET_ID]
                    if policyset_id:
                        utilities.print_notification(
                            "Update date carries the ID of Policy Set to be updated")
                        self.update_policy_set(
                            policyset_id, policyset_to_update, oauth_token_id)
                    else:
                        utilities.print_notification(
                            "Update date DOES NOT CARRY the ID of the Policy Set to be updated. Fetching now...")
                        policyset_id = self.is_policy_set_exists_to_update(
                            policyset_to_update[constant.POLICY_SET_NAME], policysets_list)
                        if policyset_id:
                            utilities.print_notification("Found the Policy Set {policy_set_name} to be updated".format(
                                policy_set_name=policyset_to_update[constant.POLICY_SET_NAME]))
                            utilities.print_notification("Policy Set to be updated = {policyset_to_update}".format(
                                policyset_to_update=policyset_to_update))
                            self.update_policy_set(
                                policyset_id, policyset_to_update, oauth_token_id)
                        else:
                            utilities.print_error("Policy Set {policy_set_name} does not exist to update. Terminating the build".format(
                                policy_set_name=policyset_to_update[constant.POLICY_SET_NAME]))
                            error_message = "Policy Set {policy_set_name} does not exist to update. Terminating the build".format(
                                policy_set_name=policyset_to_update[constant.POLICY_SET_NAME])
                            self.sentinel_deploy = open(
                                self.artifact_dir+"/"+self.cloud_provider+constant.SENTINEL_DEPLOY_RESULT_HTML, 'a')
                            self.sentinel_deploy.write(
                                utilities.construct_html_message_error(error_message))
                            self.sentinel_deploy.close()
                            sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create or Update Sentinel Policy Sets")

    parser.add_argument("--cloud", dest="cloud_provider",
                        help="Cloud Provider", required=True)
    parser.add_argument("--deployment_properties_json_file",
                        dest="deployment_properties_json_file", help="Deployment Properties", required=True)
    parser.add_argument("--branch", dest="branch",
                        help="Branch", required=True)
    parser.add_argument('--artifact_dir', dest="artifact_dir",
                        help="Artifact Directory", required=True)
    parsed_args = parser.parse_args()
    cloud_provider = parsed_args.cloud_provider
    artifact_dir = parsed_args.artifact_dir
    deployment_properties_json_file = parsed_args.deployment_properties_json_file
    branch = parsed_args.branch

    # Create Object
    policy_set_deployment = PolicySetDeployment(
        cloud_provider, artifact_dir, deployment_properties_json_file, branch)

    # Create or Update Policy Set for different Cloud Providers
    policy_set_deployment.process_policy_sets_deployment()

    utilities.print_success(
        "Sentinel Policy Sets Deployment Processed for "+cloud_provider)
