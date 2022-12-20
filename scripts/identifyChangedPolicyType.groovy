def isNativePolicyChanged(commit_flag) {
  // print "Inside Native"
  // print commit_flag
  if("native" == commit_flag) {
    return true;
  } else if ("native_sentinel" == commit_flag || "sentinel_native" == commit_flag) {
    return true;
  } else if ("native_prisma" == commit_flag || "prisma_native" == commit_flag) {
    return true;
  } else if ("build_all" == commit_flag) {
    return true;
  } else {
    return false;
  }
}

def isSentinelPolicyChanged(commit_flag) {
  // print "Inside Sentinel"
  // print commit flag
  if("sentinel" == commit_flag) {
    return true;
  } else if ("native_sentinel" == commit_flag || "sentinel_native" == commit_flag) {
    return true;
  } else if ("sentinel_prisma"== commit_flag || "prisma_sentinel" == commit_flag) {
    return true;
  } else if ("build_all" == commit_flag) {
    return true;
  } else {
    return false;
  }
}

def isPrismaPolicyChanged(commit_flag) {
  // print "Inside Prisma"
  // print commit flag
  if("prisma" == commit_flag) {
    return true;
  } else if ("native_prisma" == commit_flag || "prisma_native" == commit_flag) {
    return true;
  } else if ("sentinel_prisma"== commit_flag || "prisma_sentinel" == commit_flag) {
    return true;
  } else if ("build_all" == commit_flag) {
    return true;
  } else {
    return false;
  }
}
return this