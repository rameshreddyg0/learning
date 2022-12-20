from jproperties import Properties

def loadProperties():
    configs = Properties()
    with open("scripts/e0_deployment.properties", "rb") as read_prop:
        configs.load(read_prop)    
    return configs

def identifyChangedPolicyType(branch, changeSets):
    changedPolicyType = []
    if branch.startswith('feature/'):
        #TODO Run this test with a reg ex to identify the cloud provider and policy type
        # Create a multi dimensional dict to store data as {"gcp":{"sentinel","native"}, "aws":{"prisma"}}
        for changeSet in changeSets:
            if changeSet.startswith('gcp/sentinel') or changeSet.startswith('aws/sentinel') or changeSet.startswith('azure/sentinel'):
                changedPolicyType.append("sentinel")
            elif changeSet.startswith('gcp/native') or changeSet.startswith('aws/native') or changeSet.startswith('azure/native'):
                changedPolicyType.append("native")
            elif changeSet.startswith('gcp/prisma') or changeSet.startswith('aws/prisma') or changeSet.startswith('azure/prisma'):
                changedPolicyType.append("prisma")
    else:
        changedPolicyType.append("all")
    return changedPolicyType
 