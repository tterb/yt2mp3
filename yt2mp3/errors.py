import sys, importlib_metadata, json, logging, requests
from packaging.version import parse
from colorama import Fore, Style
from yt2mp3 import util

def handle_error(error):
  if 'youtube_dl' in str(type(error)):
    local_ver, pkg_ver = get_package_versions('youtube_dl')
    if local_ver != pkg_ver:
      msg = 'This error is likely caused by an outdated version of youtube_dl.\nYou are using version '+str(local_ver)+', however version '+str(pkg_ver)+' is available. You can upgrade the package with the \'pip install --upgrade youtube_dl\' command.'
      logging.warning('\n'+Fore.YELLOW+'✘ '+msg+Style.RESET_ALL)
  util.cleanup()
  sys.exit()


def get_package_versions(pkg):
  local_ver = importlib_metadata.version(pkg)
  pkg_ver = get_latest_release(pkg)
  return local_ver, pkg_ver

def get_latest_release(pkg):
  url_pattern = 'https://pypi.python.org/pypi/{package}/json'
  req = requests.get(url_pattern.format(package=pkg))
  data = json.loads(req.text)
  versions = list()
  releases = data.get('releases', [])
  for release in releases:
    ver = parse(release)
    if not ver.is_prerelease:
      versions.append(ver)
  return max(versions)
