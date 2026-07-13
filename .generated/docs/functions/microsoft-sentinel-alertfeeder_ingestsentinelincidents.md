# alertfeeder_ingestSentinelIncidents

## Metadata

- **Version:** `1.0.0`
- **Vendor:** Microsoft Sentinel
- **Kind:** `function`
- **Mode:** `Enabled`
- **Source File:** `integrations/vendors/MSSentinel/thehive/functions/function_alertfeeder_ingestSentinelIncidents.js`

## Description

Polls Microsoft Sentinel/Defender alerts from the Microsoft Graph Security API (/security/alerts_v2), groups them by incidentId, and creates one TheHive alert per incident

## Code

```javascript
const severityMap = { informational: 1, low: 1, medium: 2, high: 3 };

const sourceTypeMap = {
  microsoftDefenderForEndpoint:  'EDR',
  microsoft365Defender:          'SIEM',
  azureAdIdentityProtection:     'SIEM',
  microsoftDefenderForCloud:     'SIEM',
  microsoftDefenderForCloudApps: 'SIEM',
  microsoftDefenderForIdentity:  'SIEM',
  microsoftDefenderForOffice365: 'SIEM',
  dataLossPrevention:            'SIEM',
  microsoftAppGovernance:        'SIEM',
  microsoftSecurityForAI:        'SIEM',
};

// Maps Graph Security API evidence['@odata.type'] (minus the '#microsoft.graph.security.' prefix)
// to observable specs. Each extractor returns an array since one evidence item can yield several observables.
const EvidenceExtractors = {
  ipEvidence:     e => [{ dataType: 'ip', data: e.ipAddress }],
  urlEvidence:    e => [{ dataType: 'url', data: e.url }],
  userEvidence:   e => [{ dataType: 'other', data: e.userAccount && e.userAccount.userPrincipalName, tags: ['account'] }],
  deviceEvidence: e => [
    { dataType: 'hostname', data: e.deviceDnsName, tags: ['device'] },
    { dataType: 'ip',       data: e.lastExternalIpAddress, tags: ['device', 'public-ip'] },
  ],
  fileEvidence: e => [
    { dataType: 'filename', data: e.fileDetails && e.fileDetails.fileName },
    { dataType: 'hash',     data: e.fileDetails && e.fileDetails.sha256 },
  ],
  processEvidence: e => [
    { dataType: 'other', data: e.processCommandLine, tags: ['process-cmdline'] },
    { dataType: 'hash',  data: e.imageFile && e.imageFile.sha256 },
  ],
  mailboxEvidence: e => [{ dataType: 'mail', data: e.primaryAddress, tags: ['mailbox'] }],
  mailClusterEvidence: e => (e.networkMessageIds || []).map(id => ({
    dataType: 'other', data: id, tags: ['mail-network-message-id'],
  })),
  analyzedMessageEvidence: e => [
    { dataType: 'mail-subject', data: e.subject },
    { dataType: 'mail', data: e.recipientEmailAddress, tags: ['mail-recipient'] },
    { dataType: 'mail', data: e.p1Sender && e.p1Sender.emailAddress, tags: ['mail-sender'] },
    { dataType: 'ip',   data: e.senderIp, tags: ['mail-sender-ip'] },
    { dataType: 'other', data: e.networkMessageId, tags: ['mail-network-message-id'] },
  ],
};

function addObservable(dataType, data, tags, observables) {
  if (data === undefined || data === null || data === '') return;
  const existing = observables.find(o => o.dataType === dataType && o.data === data);
  if (existing) {
    if (tags) existing.tags = Array.from(new Set([...(existing.tags || []), ...tags]));
  } else {
    const obs = { dataType: dataType, data: data };
    if (tags) obs.tags = tags;
    observables.push(obs);
  }
}

function evidenceType(evidence) {
  return (evidence['@odata.type'] || '').replace('#microsoft.graph.security.', '');
}

function processObservables(alerts) {
  const observables = [];
  alerts.forEach(alert => {
    (alert.evidence || []).forEach(evidence => {
      const extractor = EvidenceExtractors[evidenceType(evidence)];
      if (!extractor) return;
      extractor(evidence).forEach(({ dataType, data, tags }) => addObservable(dataType, data, tags, observables));
    });
  });
  return observables;
}

function findTactics(techniques, context) {
  const patterns = [];
  techniques.forEach(t => {
    const lookup = context.query.execute([{ _name: 'getPattern', idOrName: t }]);
    if (Array.isArray(lookup)) patterns.push(...lookup);
  });
  return patterns;
}

function groupByIncident(alerts) {
  const groups = {};
  alerts.forEach(alert => {
    if (!alert.incidentId) return;
    (groups[alert.incidentId] = groups[alert.incidentId] || []).push(alert);
  });
  return groups;
}

function handle(input, context) {
  const alerts = input.value || [];
  const incidentGroups = groupByIncident(alerts);

  Object.keys(incidentGroups).forEach(incidentId => {
    const group = incidentGroups[incidentId];
    const sourceRef = 'sentinel-incident-' + incidentId;

    // Deduplication
    const filters = [{ _name: 'filter', _and: [{ _field: 'sourceRef', _value: sourceRef }] }];
    if (context.alert.find(filters).length > 0) return;

    // Use the highest-severity alert in the group as the representative for title/classification/etc.
    const primary = [...group].sort((a, b) => (severityMap[b.severity] || 0) - (severityMap[a.severity] || 0))[0];

    const createdTimestamp = group.reduce((min, a) => {
      const t = a.createdDateTime ? new Date(a.createdDateTime).getTime() : Date.now();
      return Math.min(min, t);
    }, Infinity);

    const sources = [...new Set(group.map(a => a.serviceSource).filter(Boolean))];
    const alertType = sources.length === 1 ? (sourceTypeMap[sources[0]] || 'SIEM') : 'SIEM';

    // MITRE: deduplicate technique IDs across all child alerts, resolve full patterns from TheHive's database
    const mitreTechniques = [...new Set(group.flatMap(a => a.mitreTechniques || []))];
    const tactics = findTactics(mitreTechniques, context);
    const procedures = tactics.map(tactic => ({
      patternId: tactic.patternId,
      tactic: (tactic.tactics || [])[0],
      occurDate: createdTimestamp,
      description: tactic.description,
    }));
    const unresolvedTechniques = mitreTechniques.filter(t => !tactics.some(p => p.patternId === t));

    const tags = [
      'Microsoft Sentinel',
      'severity:' + primary.severity,
      'status:' + primary.status,
      ...(primary.classification && primary.classification !== 'unknown' ? ['classification:' + primary.classification] : []),
      ...(primary.determination && primary.determination !== 'unknown' ? ['determination:' + primary.determination] : []),
      ...new Set(group.flatMap(a => a.systemTags || [])),
      ...new Set(group.flatMap(a => a.categories || [])),
      ...sources,
      ...tactics.map(t => t.name),
      ...unresolvedTechniques.map(t => 'TTP:' + t),
    ].filter(Boolean);

    const alertDescriptions = group.map(alert =>
      `### ${alert.title}\n` +
      `- **Alert ID:** ${alert.id}\n` +
      `- **Status:** ${alert.status} | **Severity:** ${alert.severity}\n` +
      `- **Categories:** ${(alert.categories || []).join(', ')}\n` +
      `- **Service source:** ${alert.serviceSource} | **Detection source:** ${alert.detectionSource}\n` +
      `- **First activity:** ${alert.firstActivityDateTime}\n` +
      `- **Last activity:** ${alert.lastActivityDateTime}\n` +
      (alert.description ? `- **Description:** ${alert.description}\n` : '') +
      (alert.actorDisplayName ? `- **Actor:** ${alert.actorDisplayName}\n` : '') +
      (alert.threatFamilyName ? `- **Threat family:** ${alert.threatFamilyName}\n` : '') +
      ((alert.mitreTechniques || []).length > 0 ? `- **MITRE techniques:** ${alert.mitreTechniques.join(', ')}\n` : '')
    ).join('\n---\n\n');

    const description =
      `## Incident #${incidentId}\n\n` +
      `**URL:** ${primary.incidentWebUrl}\n\n` +
      `| Field | Value |\n` +
      `|---|---|\n` +
      `| Status | ${primary.status} |\n` +
      `| Severity | ${primary.severity} |\n` +
      `| Classification | ${primary.classification || 'N/A'} |\n` +
      `| Determination | ${primary.determination || 'N/A'} |\n` +
      `| Assigned to | ${primary.assignedTo || 'Unassigned'} |\n` +
      `| Created | ${new Date(createdTimestamp).toISOString()} |\n\n` +
      `## Alerts (${group.length})\n\n` +
      alertDescriptions;

    context.alert.create({
      type: alertType,
      source: 'MicrosoftSentinel',
      sourceRef: sourceRef,
      title: '[Sentinel] ' + primary.title + ' - #' + incidentId,
      description: description,
      date: createdTimestamp,
      severity: severityMap[primary.severity] || 2,
      externalLink: primary.incidentWebUrl,
      tags: tags,
      observables: processObservables(group),
      procedures: procedures,
    });
  });
}
```

---

*This documentation is auto-generated. Do not edit manually.*
