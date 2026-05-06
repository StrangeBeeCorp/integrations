# alertfeeder_ingestSentinelIncidents

## Metadata

- **Version:** `1.0.0`
- **Type:** Generic Function
- **Function Type:** `Feeder`
- **Kind:** `function`
- **Mode:** `Enabled`
- **Source File:** `integrations/generic/functions/function_alertfeeder_ingestSentinelIncidents.js`

## Description

Ingests Microsoft Sentinel incidents from the Microsoft 365 Defender API and creates TheHive alerts, one per incident

## Code

```javascript
const severityMap = { Informational: 1, Low: 1, Medium: 2, High: 3, Critical: 4 };

const sourceTypeMap = {
  'MicrosoftDefenderForEndpoint':  'EDR',
  'MicrosoftSentinel':             'SIEM',
  'MicrosoftDefenderForIdentity':  'SIEM',
  'MicrosoftDefenderForOffice365': 'SIEM',
  'MicrosoftCloudAppSecurity':     'SIEM',
};

// Maps M365 Defender API entityType values to TheHive observable types.
// Entity fields are flat (unlike the ARM API where they're nested under .properties).
// Array entries produce multiple observables from a single entity kind.
const EntityToObservableMap = {
  Ip:          { dataType: 'ip',       valueProperty: 'ipAddress' },
  Url:         { dataType: 'url',      valueProperty: 'url' },
  User:        { dataType: 'other',    valueProperty: 'userPrincipalName', tags: ['account'] },
  Process:     { dataType: 'other',    valueProperty: 'processCommandLine', tags: ['process-cmdline'] },
  MailBox:     { dataType: 'mail',     valueProperty: 'mailboxPrimaryAddress', tags: ['mailbox'] },
  MailCluster: { dataType: 'other',    valueProperty: 'networkMessageIds', tags: ['mail-network-message-id'] },
  File: [
    { dataType: 'filename', valueProperty: 'fileName' },
    { dataType: 'hash',     valueProperty: 'sha256' },
  ],
  MailMessage: [
    { dataType: 'mail-subject', valueProperty: 'subject' },
    { dataType: 'mail',         valueProperty: 'recipient',        tags: ['mail-recipient'] },
    { dataType: 'mail',         valueProperty: 'p1Sender',         tags: ['mail-sender'] },
    { dataType: 'other',        valueProperty: 'networkMessageId', tags: ['mail-network-message-id'] },
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

function processObservables(alerts) {
  const observables = [];
  alerts.forEach(alert => {
    (alert.devices || []).forEach(device => {
      if (device.deviceDnsName) addObservable('hostname', device.deviceDnsName, ['device'], observables);
      if (device.publicIp)      addObservable('ip',       device.publicIp,      ['device', 'public-ip'], observables);
    });
    (alert.entities || []).forEach(entity => {
      const map = EntityToObservableMap[entity.entityType];
      if (!map) return;
      const maps = Array.isArray(map) ? map : [map];
      maps.forEach(m => {
        const values = entity[m.valueProperty];
        if (Array.isArray(values)) {
          values.forEach(v => addObservable(m.dataType, v, m.tags, observables));
        } else {
          addObservable(m.dataType, values, m.tags, observables);
        }
      });
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

function handle(input, context) {
  const incidents = input.value || [];

  incidents.forEach(incident => {
    const sourceRef = 'sentinel-incident-' + incident.incidentId;

    // Deduplication
    const filters = [{ _name: 'filter', _and: [{ _field: 'sourceRef', _value: sourceRef }] }];
    if (context.alert.find(filters).length > 0) return;

    const alerts = incident.alerts || [];
    const firstAlert = alerts[0] || {};
    const createdTimestamp = incident.createdTime ? new Date(incident.createdTime).getTime() : Date.now();

    const sources = [...new Set(alerts.map(a => a.serviceSource).filter(Boolean))];
    const alertType = sources.length === 1 ? (sourceTypeMap[sources[0]] || 'SIEM') : 'SIEM';
    const firstActivityTimestamp = firstAlert.firstActivity ? new Date(firstAlert.firstActivity).getTime() : createdTimestamp;

    // MITRE: deduplicate technique IDs across all child alerts, resolve full patterns from TheHive's database
    const mitreTechniques = [...new Set(alerts.flatMap(a => a.mitreTechniques || []))];
    const tactics = findTactics(mitreTechniques, context);
    const procedures = tactics.map(tactic => ({
      patternId: tactic.patternId,
      tactic: (tactic.tactics || [])[0],
      occurDate: firstActivityTimestamp,
      description: tactic.description,
    }));

    const unresolvedTechniques = mitreTechniques.filter(
      t => !tactics.some(p => p.patternId === t)
    );

    const tags = [
      'Microsoft Sentinel',
      'severity:' + incident.severity,
      'status:' + incident.status,
      ...(incident.classification && incident.classification !== 'Unknown' ? ['classification:' + incident.classification] : []),
      ...(incident.determination && incident.determination !== 'NotAvailable' ? ['determination:' + incident.determination] : []),
      ...(incident.tags || []),
      ...(firstAlert.category ? ['category:' + firstAlert.category] : []),
      ...(firstAlert.serviceSource ? [firstAlert.serviceSource] : []),
      ...tactics.map(t => t.name),
      ...unresolvedTechniques.map(t => 'TTP:' + t),
    ].filter(Boolean);

    const alertDescriptions = alerts.map(alert =>
      `### ${alert.title}\n` +
      `- **Alert ID:** ${alert.alertId}\n` +
      `- **Status:** ${alert.status} | **Severity:** ${alert.severity}\n` +
      `- **Category:** ${alert.category}\n` +
      `- **Service source:** ${alert.serviceSource} | **Detection source:** ${alert.detectionSource}\n` +
      `- **First activity:** ${alert.firstActivity}\n` +
      `- **Last activity:** ${alert.lastActivity}\n` +
      (alert.description ? `- **Description:** ${alert.description}\n` : '') +
      (alert.actorName ? `- **Actor:** ${alert.actorName}\n` : '') +
      (alert.threatFamilyName ? `- **Threat family:** ${alert.threatFamilyName}\n` : '') +
      ((alert.mitreTechniques || []).length > 0 ? `- **MITRE techniques:** ${alert.mitreTechniques.join(', ')}\n` : '')
    ).join('\n---\n\n');

    const description =
      `## Incident #${incident.incidentId}\n\n` +
      `**URL:** ${incident.incidentUri}\n\n` +
      `| Field | Value |\n` +
      `|---|---|\n` +
      `| Status | ${incident.status} |\n` +
      `| Severity | ${incident.severity} |\n` +
      `| Classification | ${incident.classification || 'N/A'} |\n` +
      `| Determination | ${incident.determination || 'N/A'} |\n` +
      `| Assigned to | ${incident.assignedTo || 'Unassigned'} |\n` +
      `| Created | ${incident.createdTime} |\n` +
      `| Last updated | ${incident.lastUpdateTime} |\n` +
      `| Tags | ${(incident.tags || []).join(', ') || 'None'} |\n\n` +
      `## Alerts (${alerts.length})\n\n` +
      alertDescriptions;

    context.alert.create({
      type: alertType,
      source: 'MicrosoftSentinel',
      sourceRef: sourceRef,
      title: '[Sentinel] ' + incident.incidentName + ' - #' + incident.incidentId,
      description: description,
      date: createdTimestamp,
      severity: severityMap[incident.severity] || 2,
      tags: tags,
      observables: processObservables(alerts),
      procedures: procedures,
    });
  });
}
```

---

*This documentation is auto-generated. Do not edit manually.*
