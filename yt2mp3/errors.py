import sys, json, logging, requests, importlib_metadata
from packaging import version
from colorama import Fore, Style
from yt2mp3 import util

def handle_error(exception):
  """
  Checks if an out-of-date dependency is the cause of an exception to provide a more informative error message
  Args:
    exception: An exception that was raised within the program
  """
  pkg = 'youtube_dl'
  if pkg in str(type(exception)):
    local_ver = get_local_version(pkg)
    pkg_ver = get_latest_release(pkg)
    if local_ver != pkg_ver:
      msg = 'This error is likely caused by an outdated version of '+pkg+'.\nYou are using version '+str(local_ver)+', however version '+str(pkg_ver)+' is available. You can upgrade the package with the \'pip install --upgrade '+pkg+'\' command.'
      logging.warning('\n'+Fore.YELLOW+'✘ '+msg+Style.RESET_ALL)
  util.cleanup()
  sys.exit()


def get_local_version(pkg):
  """
  Retrieves the local version of the specified package
  Args:
    pkg: A string containing the name of a package
  Returns:
    The local versions of the package
  """
  local_ver = version.parse(importlib_metadata.version(pkg))
  return local_ver

def get_latest_release(pkg):
  """
  Retrieves the most latest version of the specified package
  Args:
    pkg: A string containing the name of a package
  Returns:
    The most recently published versions of the package
  """
  url_pattern = 'https://pypi.python.org/pypi/{package}/json'
  req = requests.get(url_pattern.format(package=pkg))
  data = json.loads(req.text)
  versions = list()
  releases = data.get('releases', [])
  for release in releases:
    ver = version.parse(release)
    if not ver.is_prerelease:
      versions.append(ver)
  return max(versions)
