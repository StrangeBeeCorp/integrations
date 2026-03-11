## Analyzers (4)

### [MSEntraID_GetDirectoryAuditLogs v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID/MSEntraID_GetDirectoryAuditLogs.json)
Pull Microsoft Entra ID directory audit logs for a user within the specified timeframe.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`

### [MSEntraID_GetSignIns v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID/MSEntraID_GetSignIns.json)
Pull all Microsoft Entra ID sign ins for a user within the specified amount of time.

- **Author:** @jahamilto
- **License:** AGPL-V3
- **Data Types:** `mail`

### [MSEntraID_GetUserInfo v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID/MSEntraID_GetUserInfo.json)
Get information about the user from Microsoft Entra ID, using mail or user identifier (UPN/sAMAccountName/employeeId)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`, `other`, `user`, `username`

### [MSEntraID_GetManagedDevicesInfo v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID/MSEntraID_GetManagedDevicesInfo.json)
Get Microsoft Intune Managed Device(s) Details from hostname or mail

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`, `hostname`

---

## Responders (5)

### [MSEntraID_enableUser v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID/MSEntraID_enableUser.json)
Enable user in Microsoft Entra ID for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [MSEntraID_disableUser v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID/MSEntraID_disableUser.json)
Disable user in Microsoft Entra ID for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [MSEntraID_ForcePasswordReset v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID/MSEntraID_ForcePasswordReset.json)
Force password reset at next login for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [MSEntraID_revokeSignInSessions v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID/MSEntraID_revokeSignInSessions.json)
Invalidates all the refresh tokens issued to applications for a Microsoft Entra ID user (as well as session cookies in a user's browser)

- **Author:** Daniel Weiner @dmweiner; revised by @jahamilto; Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

### [MSEntraID_ForcePasswordResetWithMFA v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID/MSEntraID_ForcePasswordResetWithMFA.json)
Force password reset at next login with MFA verification before password change for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
