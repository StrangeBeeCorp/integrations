## Analyzers (4)

### Enrich observables with intelligence

#### [MSEntraID GetDirectoryAuditLogs v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID)
Pull Microsoft Entra ID directory audit logs for a user within the specified timeframe.

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`

#### [MSEntraID GetUserInfo v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID)
Get information about the user from Microsoft Entra ID, using mail or user identifier (UPN/sAMAccountName/employeeId)

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`, `other`, `user`, `username`

#### [MSEntraID GetManagedDevicesInfo v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID)
Get Microsoft Intune Managed Device(s) Details from hostname or mail

- **Author:** Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `mail`, `hostname`

#### [MSEntraID GetSignIns v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/analyzers/MSEntraID)
Pull all Microsoft Entra ID sign ins for a user within the specified amount of time.

- **Author:** @jahamilto
- **License:** AGPL-V3
- **Data Types:** `mail`

---

## Responders (5)

### Trigger automated responses

#### [MSEntraID ForcePasswordReset v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID)
Force password reset at next login for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSEntraID ForcePasswordResetWithMFA v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID)
Force password reset at next login with MFA verification before password change for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSEntraID disableUser v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID)
Disable user in Microsoft Entra ID for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSEntraID revokeSignInSessions v1.1](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID)
Invalidates all the refresh tokens issued to applications for a Microsoft Entra ID user (as well as session cookies in a user's browser)

- **Author:** Daniel Weiner @dmweiner; revised by @jahamilto; Fabien Bloume, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`

#### [MSEntraID enableUser v1.0](https://github.com/TheHive-Project/Cortex-Analyzers/blob/master/responders/MSEntraID)
Enable user in Microsoft Entra ID for a User Principal Name. (mail)

- **Author:** nusatanra-self, StrangeBee
- **License:** AGPL-V3
- **Data Types:** `thehive:case_artifact`
