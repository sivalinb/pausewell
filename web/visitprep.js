let vpPatient = null, vpRecords = [], vpBrief = null;
const vpSelected = new Set();
function vpCount() { $('vp-selection').textContent = `${vpSelected.size} of ${vpRecords.length} records selected`; }
function vpSource(id) {
  const source = document.getElementById('vp-source-' + id);
  if (source) { source.open = true; source.scrollIntoView({behavior: 'smooth', block: 'center'}); }
}
function vpRenderRecords() {
  const list = $('vp-records'); list.replaceChildren();
  if (!vpRecords.length) list.append(text('p', 'No records yet. Add record text or restore the fictional demo.'));
  for (const record of vpRecords) {
    const item = document.createElement('article'); item.className = 'vp-record';
    const label = document.createElement('label'); label.className = 'vp-record-title';
    const selected = document.createElement('input'); selected.type = 'checkbox'; selected.checked = vpSelected.has(record.id);
    selected.onchange = () => { selected.checked ? vpSelected.add(record.id) : vpSelected.delete(record.id); vpCount(); };
    label.append(selected, text('span', record.title));
    const details = document.createElement('details'); details.id = 'vp-source-' + record.id;
    details.append(text('summary', 'View source text'), text('pre', record.text, 'vp-source-text'));
    const remove = text('button', 'Delete record', 'small-button'); remove.type = 'button';
    remove.onclick = () => { if (confirm('Delete this record and saved briefs that cite it?')) run(async () => {
      await api('visitprep/records/' + encodeURIComponent(record.id), 'DELETE'); vpBrief = null;
      $('vp-result').replaceChildren(text('h2', 'Record deleted'), text('p', 'Prepare a new brief from the remaining records.'));
      await visitprepLoad();
    }, remove); };
    item.append(label, text('small', `${record.date} · ${record.kind} · ${record.synthetic ? 'Fictional demo' : 'Your imported record'}`), details, remove);
    list.append(item);
  }
  $('vp-reset-demo').hidden = vpRecords.length > 0;
  vpCount();
}
async function visitprepLoad() {
  const data = await api('visitprep/bootstrap'); vpPatient = data.patient; vpRecords = data.records;
  const old = new Set(vpSelected); vpSelected.clear();
  for (const r of vpRecords) if (!old.size || old.has(r.id)) vpSelected.add(r.id);
  $('vp-patient').textContent = `${vpPatient.name} · ${vpPatient.synthetic ? 'Fictional demo workspace' : 'Private records'}`;
  for (const option of $('vp-provider').options) {
    const provider = data.providers.find(p => p.id === option.value);
    option.disabled = option.value !== 'local' && !provider?.configured;
  }
  vpRenderRecords(); await vpHistory();
}
function vpRenderBrief(brief) {
  vpBrief = brief; const panel = $('vp-result'); panel.replaceChildren();
  panel.append(text('div', '03 / YOUR APPOINTMENT BRIEF', 'section-label'), text('h2', 'Bring the sources. Ask the questions.'), text('p', brief.message));
  if (brief.coverage) panel.append(text('p', `${brief.coverage.selected_records} records selected · ${brief.facts.length} passages included. Selected evidence only; this is not a complete medication or medical reconciliation.`, 'vp-coverage'));
  const sections = [...new Set(brief.facts.map(f => f.section))];
  for (const section of sections) {
    panel.append(text('h3', section.replaceAll('_', ' '), 'vp-section-heading'));
    for (const fact of brief.facts.filter(f => f.section === section)) {
      const article = document.createElement('article'); article.className = 'vp-fact';
      article.append(text('blockquote', fact.quote));
      const source = text('button', `${fact.source_date} · ${fact.source_title} ↗`, 'vp-citation'); source.type = 'button'; source.onclick = () => vpSource(fact.record_id);
      article.append(source); panel.append(article);
    }
  }
  if (!brief.facts.length) panel.append(text('p', 'No passages were included. Review the selected records or choose a different preparation question.'));
  if (brief.questions.length) {
    panel.append(text('h3', 'Questions for your clinician'));
    const list = document.createElement('ul');
    for (const q of brief.questions) list.append(text('li', q.text));
    panel.append(list);
  }
  panel.append(text('p', 'These are statements recorded in source documents, not verified current facts or instructions to change treatment. Review the original records with your clinician.', 'muted'));
  const m = brief.model;
  panel.append(text('p', `Prepared with ${m.provider} · ${m.status.replaceAll('_', ' ')} · ${m.tokens} reported tokens · ${Math.round(m.latency_ms)} ms`, 'vp-model-status'));
  const actions = document.createElement('div'); actions.className = 'row';
  for (const [label, format] of [['Download brief', 'markdown'], ['Download JSON', 'json']]) {
    const b = text('button', label); b.type = 'button'; b.onclick = () => run(() => vpExport(brief.id, format), b); actions.append(b);
  }
  panel.append(actions);
}
async function vpHistory() {
  const result = await api('visitprep/briefs'); const briefs = Array.isArray(result) ? result : result.briefs;
  const list = $('vp-history'); list.replaceChildren();
  for (const b of (briefs || []).slice(0, 5)) {
    const button = text('button', `${b.created_at ? new Date(b.created_at).toLocaleString() : 'Saved brief'} · ${b.facts?.length ?? b.fact_count ?? ''} passages`, 'vp-history-button');
    button.type = 'button'; button.onclick = () => run(async () => {
      if (b.facts) vpRenderBrief(b); else { const full = await vpExport(b.id, 'json', true); vpRenderBrief(full); }
      $('vp-result').scrollIntoView({behavior: 'smooth', block: 'start'});
    }, button); list.append(button);
  }
  if (!briefs?.length) list.append(text('p', 'No saved briefs yet.'));
}
async function vpExport(id, format, returnData = false) {
  const response = await fetch(`/api/visitprep/briefs/${encodeURIComponent(id)}/export?format=${format}`, {headers: {Authorization: 'Bearer ' + token}});
  if (!response.ok) throw new Error('This brief is no longer available. Its source may have been deleted.');
  if (returnData) return response.json();
  const blob = await response.blob(); const url = URL.createObjectURL(blob); const a = document.createElement('a');
  a.href = url; a.download = 'pausewell-appointment-brief.' + (format === 'json' ? 'json' : 'md'); a.click(); URL.revokeObjectURL(url);
}
$('vp-refresh').onclick = e => run(visitprepLoad, e.currentTarget);
$('vp-provider').onchange = () => { $('vp-cloud-notice').hidden = $('vp-provider').value === 'local'; $('vp-cloud-consent').checked = false; };
$('vp-file').onchange = e => run(async () => {
  const file = e.target.files[0]; if (!file) return;
  if (!file.name.toLowerCase().endsWith('.txt') || file.size > 20000) throw new Error('Choose a .txt file smaller than 20 KB.');
  const content = await file.text(); if (content.length > 6000) throw new Error('Choose a record with up to 6,000 characters.');
  $('vp-record-text').value = content; if (!$('vp-title').value) $('vp-title').value = file.name.replace(/\.txt$/i, '').slice(0, 120);
});
$('vp-add-form').onsubmit = e => { e.preventDefault(); run(async () => {
  const record = await api('visitprep/records', 'POST', {title: $('vp-title').value, date: $('vp-record-date').value, kind: $('vp-kind').value, text: $('vp-record-text').value, synthetic: false});
  vpSelected.add(record.id); $('vp-add-form').reset(); await visitprepLoad(); notice('Record saved locally. It has not been sent to an AI provider.');
}, e.submitter); };
$('vp-brief-form').onsubmit = e => { e.preventDefault(); run(async () => {
  if (!vpPatient) throw new Error('Connect to your private space first.');
  if (!vpSelected.size) throw new Error('Select at least one record.');
  const provider = $('vp-provider').value;
  if (provider !== 'local' && !$('vp-cloud-consent').checked) throw new Error('Allow selected record text to be sent, or choose the local brief.');
  $('vp-progress').textContent = 'Checking access, reading selected sources and validating citations…';
  try {
    const brief = await api('visitprep/brief', 'POST', {patient_id: vpPatient.id, question: $('vp-question').value, provider, cloud_consent: provider !== 'local' && $('vp-cloud-consent').checked, record_ids: [...vpSelected]});
    vpRenderBrief(brief); await vpHistory();
  } finally { $('vp-progress').textContent = ''; $('vp-cloud-consent').checked = false; }
}, e.submitter); };
$('vp-reset-demo').onclick = e => { if (confirm('Restore the fictional demo records into this empty workspace?')) run(async () => { await api('visitprep/demo/reset', 'POST'); await visitprepLoad(); }, e.currentTarget); };

async function visitprepObserve() {
  const data = await api('visitprep/observability');
  $('vp-counters').replaceChildren();
  for (const [key, value] of Object.entries(data.counters)) {
    const item = document.createElement('article'); item.append(text('span', key.replaceAll('_', ' ').toUpperCase()), text('strong', value)); $('vp-counters').append(item);
  }
  $('vp-traces').replaceChildren();
  for (const trace of data.traces) $('vp-traces').append(text('div', `${trace.operation} · ${trace.outcome} · ${Math.round(trace.latency_ms)} ms · ${trace.tokens} tokens · ${trace.provider} · ${trace.synthetic ? 'fictional demo' : 'private workspace'}`, 'trace'));
  if (!data.traces.length) $('vp-traces').append(text('p', 'No appointment operations yet.'));
}
