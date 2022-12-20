import argparse
import os
import subprocess
import sys
import utilities

"""
Class Name :        class TerraformFormatCheck
Class Description : This class has implementation to invoke terraform format check  on native policies for cloud provider received
Class Methods :     __init__ : Initialized the object with provided cloud platform, mounting workspace and container
                    terraform_format_check : Invokes Terraform format check for the native policies in cloud platform provided
                    and prints the respective details
"""
class TerraformFormatCheck:
  """
  Method Name :        __init__
  Method Description : Creates the object and stores the details like cloud provider and container image to be created
  Method Returns : None
  """
  def __init__(self, cloud_provider, policy_type, artifact_dir):
        self.cloud_provider = cloud_provider
        self.policy_type = policy_type
        self.artifact_dir = artifact_dir

  def terraform_format_check(self):
    utilities.print_notification("\n ********** Running The Terraform Format Check **********\n")
    os.chdir("../{cloud_provider}/{policy_type}/".format(cloud_provider = self.cloud_provider, policy_type=self.policy_type))
    terraform_format_command_list = ['terraform', 'fmt', '-recursive', '-diff', '-check']

    p1 = subprocess.run(terraform_format_command_list, capture_output=True)
    # Formating successful
    if(p1.returncode == 0):
      utilities.print_success("Terraform Format Succeeded")
      utilities.print_success(p1.stdout.decode())
      os.chdir("../../scripts")
      self.format_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Format_Check_Results.html", 'w')
      self.format_check.write(utilities.construct_html_success("Terraform Format Succeeded", p1.stdout.decode()))
      self.format_check.close()
    # Formatting failed
    else:
      utilities.print_error("Return code")
      utilities.print_error(p1.returncode)
      utilities.print_error("Diagnostics")
      utilities.print_error(p1.stdout.decode())
      utilities.print_error(p1.stderr.decode())
      os.chdir("../../scripts")
      self.format_check = open(self.artifact_dir+"/"+self.cloud_provider+"_"+self.policy_type+"_Format_Check_Results.html", 'w')
      self.format_check.write(utilities.construct_html_error("Terraform Format Failed", p1.stdout.decode(), p1.stderr.decode()))
      self.format_check.close()
      # Bubble up the failure and hard stop the build
      # sys.exit(1)
    utilities.print_success("\n ********** Completed Terraform Format Check **********\n")

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Gather Terraform Container Image, Cloud Platform, to validate the native policies for given cloud provider")

  parser.add_argument("--cloud", dest="cloud_provider", help="Cloud Provider", required=True)
  parser.add_argument("--policyType", dest="policy_type", help="Mounting Workspace", required=True)
  parser.add_argument("--artifact_dir", dest="artifact_dir", help="Artifact Directory", required=True)

  parsed_args = parser.parse_args()
  cloud_provider = parsed_args.cloud_provider
  policy_type = parsed_args.policy_type
  artifact_dir = parsed_args.artifact_dir

  #Create Object
  policy_check_obj = TerraformFormatCheck(cloud_provider, policy_type, artifact_dir)
  policy_check_obj.terraform_format_check()
  
  #utilities.print_notification("Native Policies validation completed for "+cloud_provider)
