import argparse
import os
import sys
import subprocess
import utilities

"""
Class Name :        class TerraformValidate
Class Description : This class has implementation to invoke validation on native policies for cloud provider received
Class Methods :     __init__ : Initialized the object with provided cloud platform, mounting workspace and container
                    terraform_validate : Invokes Terraform validation check for the native policies in cloud platform provided
                    and prints the respective details
"""
class TerraformValidate:
  """
  Method Name :        __init__
  Method Description : Creates the object and stores the details like cloud provider and container image to be created
  Method Returns : None
  """
  def __init__(self, cloud_provider, policy_type, artifact_dir):
        self.cloud_provider = cloud_provider
        self.artifact_dir = artifact_dir
        self.policy_type = policy_type

  def terraform_validate(self):
    utilities.print_notification("\n ********** Running The Terraform Validation **********\n")
    os.chdir("../{cloud_provider}/{policy_type}/".format(cloud_provider = self.cloud_provider, policy_type=self.policy_type))
    #Terraform Validate Command For GitHub Acctions
    terraform_validate_command_list = ['terraform', 'validate', '-json']
    p1 = subprocess.run(terraform_validate_command_list, capture_output=True)
    #Terraform Validate Command for Containerized Environment
    #p1 = subprocess.run(utilities.getDockerContainerCmd(self.mountingWorkspace, self.terraformContainer) + 'validate -json', capture_output=True, shell=True)
    # Formating successful
    if(p1.returncode == 0):
      utilities.print_success(p1.stdout.decode())
      os.chdir("../../scripts")
      self.validate_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Terraform_Validate_Results.html", 'w')
      self.validate_check.write(utilities.construct_html_success("Terraform Validate Succeeded", p1.stdout.decode()))
      self.validate_check.close()
    # Formatting faled
    else:
      utilities.print_error("Return code")
      utilities.print_error(p1.returncode)
      utilities.print_error("Diagnostics")
      utilities.print_error(p1.stdout.decode())
      os.chdir("../../scripts")
      self.validate_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Terraform_Validate_Results.html", 'w')
      self.validate_check.write(utilities.construct_html_error("Terraform Plan Failed", p1.stdout.decode(), p1.stderr.decode()))
      self.validate_check.close()
      # Bubble up the failure and hard stop the build
      # sys.exit(1)

    utilities.print_success("\n ********** Completed Terraform Validation **********\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Gather Terraform Container Image, Cloud Platform, to validate the native policies for given cloud provider")

  parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
  parser.add_argument("--policyType", dest="policy_type", help="Policy Type", required=True)
  parser.add_argument("--artifact_dir", dest="artifact_dir", help="Artifact Directory", required=True)

  parsed_args = parser.parse_args()
  cloud_provider = parsed_args.cloud_provider
  artifact_dir = parsed_args.artifact_dir
  policy_type = parsed_args.policy_type

  #Create Object
  policyCheckObj = TerraformValidate(cloud_provider, policy_type, artifact_dir)
  policyCheckObj.terraform_validate()
  
  # utilities.print_notification("Native Policies validation completed for "+cloud_provider)
