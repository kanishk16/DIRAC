""" A set of utilities for getting configuration information for the WMS components
"""

__RCSID__ = "$Id$"

from DIRAC import S_OK, S_ERROR, gLogger
from DIRAC.FrameworkSystem.Client.ProxyManagerClient import gProxyManager
from DIRAC.ConfigurationSystem.Client.Helpers import Registry, Operations


def findGenericPilotCredentials(vo=False, group=False):
  if not group and not vo:
    return S_ERROR("Need a group or a VO to determine the Generic pilot credentials")
  if not vo:
    vo = Registry.getVOForGroup(group)
    if not vo:
      return S_ERROR("Group %s does not have a VO associated" % group)
  opsHelper = Operations.Operations(vo=vo)
  pilotGroup = opsHelper.getValue("Pilot/GenericPilotGroup", "")
  pilotDN = opsHelper.getValue("Pilot/GenericPilotDN", "")
  if not pilotDN:
    pilotUser = opsHelper.getValue("Pilot/GenericPilotUser", "")
    if pilotUser:
      result = Registry.getDNForUsername(pilotUser)
      if result['OK']:
        pilotDN = result['Value']
  if pilotDN and pilotGroup:
    gLogger.verbose("Pilot credentials from CS: %s@%s" % (pilotDN, pilotGroup))
    result = gProxyManager.userHasProxy(pilotDN, pilotGroup, 86400)
    if not result['OK']:
      return S_ERROR("%s@%s has no proxy in ProxyManager")
    return S_OK((pilotDN, pilotGroup))

  if pilotDN:
    return S_ERROR("DN %s does not have group %s" % (pilotDN, pilotGroup))
  return S_ERROR("No generic proxy in the Proxy Manager with groups %s" % pilotGroup)
