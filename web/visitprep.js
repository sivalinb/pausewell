let vpPatient = null, vpRecords = [], vpBrief = null, vpAgenda = null;
let vpSelectionInitialized = false, vpDirty = false, vpSaving = false;
let vpEpoch = 0, vpPreparing = 0, vpPrepareSequence = 0;
let vpImporting = false, vpErasing = false;
const vpSelected = new Set();
function vpCanReplace() {
  if (vpSaving || vpPreparing) { notice('Your agenda is being prepared or saved. Please wait before opening another brief.'); return false; }
  return !vpDirty || confirm('You have unsaved agenda changes. Discard them and open another brief?');
}
function vpClearBrief(message = 'Prepare a new brief from your available records.') {
  vpEpoch++; vpPreparing = 0; $('vp-progress').textContent = ''; $('vp-cloud-consent').checked = false; vpBrief = null; vpAgenda = null; vpDirty = false;
  $('vp-result').replaceChildren(text('h2', 'Your appointment agenda'), text('p', message));
  $('vp-source-dialog').close(); $('vp-source-dialog-text').textContent = '';
  $('vp-source-dialog-title').textContent = 'Original source'; $('vp-source-dialog-meta').textContent = '';
  $('vp-print-dialog').close(); $('vp-print-frame').removeAttribute('srcdoc');
}
function vpBeginErase() {
  if (vpImporting) { notice('A record is being saved. Wait for it to finish before deleting all data.'); return false; }
  if (vpErasing) return false;
  vpErasing = true; return true;
}
function vpEndErase() { vpErasing = false; }
function vpClearWorkspace() {
  vpClearBrief('All local records and agendas were deleted.');
  vpRecords = []; vpPatient = null; vpSelected.clear(); vpSelectionInitialized = true; vpRenderRecords();
  $('vp-patient').textContent = 'No records in this workspace';
  $('vp-add-form').reset(); $('vp-brief-form').reset();
  $('vp-history').replaceChildren(text('p', 'No saved briefs.'));
}
function vpCount() { $('vp-selection').textContent = `${vpSelected.size} of ${vpRecords.length} records selected`; }
function vpSource(id) {
  const record = vpRecords.find(r => r.id === id);
  if (!record) { notice('This source is unavailable. Refresh your records.'); return; }
  $('vp-source-dialog-title').textContent = record.title;
  $('vp-source-dialog-meta').textContent = `${record.date} · Original recorded text · ${record.synthetic ? 'Fictional example' : 'Imported record'}`;
  $('vp-source-dialog-text').textContent = record.text;
  $('vp-source-dialog').showModal();
}
$('vp-source-close').onclick = () => $('vp-source-dialog').close();
function vpCitation(fact) {
  const button = text('button', `${fact.source_date} · ${fact.source_title} ↗`, 'vp-citation');
  button.type = 'button'; button.onclick = () => vpSource(fact.record_id); return button;
}
function vpQuote(fact) {
  const article = document.createElement('article'); article.className = 'vp-fact';
  article.append(text('blockquote', fact.quote), vpCitation(fact)); return article;
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
      await api('visitprep/records/' + encodeURIComponent(record.id), 'DELETE');
      vpRecords = vpRecords.filter(r => r.id !== record.id); vpSelected.delete(record.id); vpRenderRecords();
      $('vp-history').replaceChildren(text('p', 'Refreshing available briefs…'));
      vpClearBrief('Record deleted. Prepare a new brief from the remaining records.');
      await visitprepLoad();
    }, remove); };
    item.append(label, text('small', `${record.date} · ${record.kind} · ${record.synthetic ? 'Fictional demo' : 'Your imported record'}`), details, remove);
    list.append(item);
  }
  $('vp-reset-demo').hidden = vpRecords.length > 0;
  vpCount();
}
async function visitprepLoad() {
  const epoch = vpEpoch;
  const data = await api('visitprep/bootstrap'); if (epoch !== vpEpoch) return; vpPatient = data.patient; vpRecords = data.records;
  const old = new Set(vpSelected); vpSelected.clear();
  for (const r of vpRecords) if (!vpSelectionInitialized || old.has(r.id)) vpSelected.add(r.id);
  vpSelectionInitialized = true;
  $('vp-patient').textContent = `${vpPatient.name} · ${vpPatient.synthetic ? 'Fictional demo workspace' : 'Private records'}`;
  for (const option of $('vp-provider').options) {
    const provider = data.providers.find(p => p.id === option.value);
    option.disabled = option.value !== 'local' && !provider?.configured;
  }
  vpRenderRecords(); await vpHistory();
}
async function vpRenderBrief(brief) {
  vpEpoch++; vpBrief = brief; vpAgenda = null; vpDirty = false; const panel = $('vp-result'); panel.replaceChildren();
  panel.append(text('div', '03 / YOUR APPOINTMENT AGENDA', 'section-label'), text('h2', 'Start with what matters to you.'), text('p', brief.message));
  const agendaPanel = document.createElement('section'); agendaPanel.id = 'vp-agenda'; agendaPanel.className = 'vp-agenda';
  agendaPanel.append(text('p', 'Loading your private agenda…')); panel.append(agendaPanel);
  if (brief.recorded_differences?.length) {
    const differences = document.createElement('section'); differences.className = 'vp-differences';
    differences.append(text('h3', 'Recorded differences to clarify'), text('p', 'These dated records contain different medication or allergy wording. Only some text formats can be compared; the app does not determine which entry is current or correct.'));
    for (const difference of brief.recorded_differences) {
      differences.append(text('h4', difference.label));
      for (const item of difference.items) differences.append(vpQuote(item));
      if (difference.notice) differences.append(text('p', difference.notice, 'muted'));
    }
    panel.append(differences);
  }
  panel.append(text('h3', 'Selected source passages'));
  const coverage = brief.evidence_coverage;
  if (coverage) {
    panel.append(text('p', `${coverage.selected_record_count} records selected · ${brief.facts.length} brief passages · ${coverage.omitted_eligible_excerpt_count} eligible passages not shown in the brief or differences.`, 'vp-coverage'));
    const details = document.createElement('details'); details.className = 'vp-coverage-details';
    details.append(text('summary', 'See record coverage and selection limits'));
    details.append(text('p', coverage.notice || 'Selected evidence only; no complete medical reconciliation is established.'));
    const list = document.createElement('ul');
    for (const item of (coverage.records || [])) {
      const row = text('li', `${item.title}: ${item.brief_fact_count} brief passage(s), ${item.difference_excerpt_count} difference passage(s), ${item.omitted_count} eligible passage(s) not shown, ${item.excluded_count} excluded segment(s). `);
      row.append(vpCitation({record_id: item.record_id, source_title: 'Open original', source_date: item.date})); list.append(row);
    }
    details.append(list, text('p', 'Difference passages are shown separately from the eight-passage brief limit. An excluded segment may be an instruction aimed at the app or outside the supported passage length. Open the source to review its full text.', 'muted')); panel.append(details);
  } else if (brief.coverage) panel.append(text('p', `${brief.coverage.selected_records} records selected · ${brief.facts.length} passages included. Selected evidence only.`, 'vp-coverage'));
  const sections = [...new Set(brief.facts.map(f => f.section))];
  for (const section of sections) {
    panel.append(text('h3', section.replaceAll('_', ' '), 'vp-section-heading'));
    for (const fact of brief.facts.filter(f => f.section === section)) panel.append(vpQuote(fact));
  }
  if (!brief.facts.length) panel.append(text('p', 'No passages were included. Open the original records to review their content.'));
  if (brief.questions.length) {
    panel.append(text('h3', 'Questions you could bring'));
    const list = document.createElement('ul');
    for (const q of brief.questions) list.append(text('li', q.text));
    panel.append(list);
  }
  panel.append(text('p', 'These are statements recorded in source documents, not verified current facts or instructions to change treatment. Review the original records with your clinician.', 'muted'));
  const m = brief.model;
  panel.append(text('p', `Prepared with ${m.provider} · ${m.status.replaceAll('_', ' ')} · ${m.tokens} reported tokens · ${Math.round(m.latency_ms)} ms`, 'vp-model-status'));
  const raw = document.createElement('details'); raw.className = 'vp-raw-exports'; raw.append(text('summary', 'Download the source-linked brief'));
  const actions = document.createElement('div'); actions.className = 'row';
  for (const [label, format] of [['Download brief', 'markdown'], ['Download JSON', 'json']]) {
    const b = text('button', label); b.type = 'button'; b.onclick = () => run(() => vpExport(brief.id, format), b); actions.append(b);
  }
  raw.append(actions); panel.append(raw);
  try {
    const agenda = await api(`visitprep/briefs/${encodeURIComponent(brief.id)}/agenda`);
    if (vpBrief?.id === brief.id) { vpAgenda = agenda; vpRenderAgenda(agendaPanel); }
  } catch (error) { if (vpBrief?.id === brief.id) agendaPanel.replaceChildren(text('p', 'This agenda is unavailable. Its source may have been deleted.')); }
}
function vpAgendaValues() {
  return {priorities: [0,1,2].map(i => $('vp-priority-'+i).value.trim()).filter(Boolean), questions: [0,1,2].map(i => $('vp-agenda-question-'+i).value.trim()).filter(Boolean)};
}
function vpRenderAgenda(panel) {
  panel.replaceChildren(); panel.append(text('h3', 'My three priorities'), text('p', 'Write what you want to discuss. Your agenda stays on your private server and is not sent to the AI provider.', 'muted'));
  const form = document.createElement('form'); form.id = 'vp-agenda-form';
  for (const [key, prefix, title] of [['priorities', 'vp-priority-', 'Priority'], ['questions', 'vp-agenda-question-', 'Question']]) {
    if (key === 'questions') form.append(text('h3', 'Questions I want answered'));
    for (let i=0;i<3;i++) {
      const label = text('label', `${title} ${i+1}`); label.htmlFor = prefix+i;
      const input = document.createElement('textarea'); input.rows = 2; input.id = prefix+i; input.maxLength = 300;
      input.value = vpAgenda[key]?.[i] || ''; input.placeholder = key === 'priorities' ? 'What matters to you for this visit?' : 'What would you like to clarify?';
      form.append(label, input);
    }
  }
  const status = text('p', vpAgenda.approved ? 'Approved by you · ready to print' : 'Draft · review your priorities and questions', 'vp-agenda-status'); status.id = 'vp-agenda-status'; status.setAttribute('aria-live','polite');
  const actions = document.createElement('div'); actions.className = 'row';
  const save = text('button', 'Save draft'); save.type = 'submit';
  const approve = text('button', 'Approve my agenda', 'primary'); approve.type = 'button';
  const print = text('button', 'Print approved agenda'); print.type = 'button'; print.id = 'vp-print-agenda'; print.disabled = !vpAgenda.approved;
  const download = text('button', 'Download approved agenda'); download.type = 'button'; download.id = 'vp-download-agenda'; download.disabled = !vpAgenda.approved;
  form.oninput = () => { vpDirty = true; status.textContent = 'Unsaved changes · save or approve this version'; print.disabled = true; download.disabled = true; };
  async function persist(approved) {
    if (vpSaving || vpPreparing) return;
    const id = vpBrief.id, values = vpAgendaValues();
    vpSaving = true;
    form.querySelectorAll('input,textarea,button').forEach(control => control.disabled = true);
    status.textContent = approved ? 'Saving your reviewed version…' : 'Saving your draft…';
    try {
      const saved = await api(`visitprep/briefs/${encodeURIComponent(id)}/agenda`, 'PUT', {...values, approved, expected_revision: vpAgenda.revision});
      if (vpBrief?.id === id) { vpAgenda = saved; vpDirty = false; vpRenderAgenda(panel); }
      notice(approved ? 'Your reviewed agenda is ready to print.' : 'Agenda draft saved locally.');
    } finally {
      vpSaving = false;
      if (form.isConnected) {
        form.querySelectorAll('input,textarea,button').forEach(control => control.disabled = false);
        print.disabled = download.disabled = !vpAgenda?.approved || vpDirty;
        status.textContent = vpDirty ? 'Changes still unsaved · check the message above' : 'Review this agenda before exporting';
      }
    }
  }
  form.onsubmit = e => { e.preventDefault(); run(() => persist(false), save); };
  approve.onclick = () => run(() => persist(true), approve);
  download.onclick = () => run(() => vpAgendaExport('markdown'), download);
  print.onclick = () => run(async () => {
    const epoch = vpEpoch, id = vpBrief.id, revision = vpAgenda.revision;
    const response = await vpAgendaResponse('html', id, revision);
    const html = await response.text();
    if (epoch !== vpEpoch || vpBrief?.id !== id || vpDirty || !vpAgenda?.approved || vpAgenda.revision !== revision) return;
    $('vp-print-frame').srcdoc = html;
    $('vp-print-dialog').showModal();
  }, print);
  actions.append(save, approve, print, download); form.append(status, text('p', 'Approval records that you reviewed this agenda. It does not verify the medical records. Editing creates a new version that needs approval.', 'muted'), actions); panel.append(form);
  if (vpPreparing) form.querySelectorAll('input,textarea,button').forEach(control => control.disabled = true);
}
async function vpAgendaResponse(format, id = vpBrief?.id, revision = vpAgenda?.revision) {
  if (!id) throw new Error('This agenda is no longer available.');
  const response = await fetch(`/api/visitprep/briefs/${encodeURIComponent(id)}/agenda/export?format=${format}`, {headers: {Authorization: 'Bearer ' + token}});
  if (!response.ok) throw new Error('This agenda needs current approval or its source is no longer available. Reload the brief and review it again.');
  if (response.headers.get('X-Agenda-Revision') !== String(revision)) throw new Error('The saved agenda has changed. Open it again and review the current version.');
  return response;
}
async function vpAgendaExport(format) {
  const epoch = vpEpoch, id = vpBrief.id, revision = vpAgenda.revision;
  const response = await vpAgendaResponse(format, id, revision); const blob = await response.blob();
  if (epoch !== vpEpoch || vpBrief?.id !== id || vpDirty || !vpAgenda?.approved || vpAgenda.revision !== revision) return;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = 'visitprep-approved-agenda.' + (format === 'json' ? 'json' : 'md'); a.click(); URL.revokeObjectURL(url);
}
async function vpHistory() {
  const epoch = vpEpoch;
  const result = await api('visitprep/briefs'); if (epoch !== vpEpoch) return; const briefs = Array.isArray(result) ? result : result.briefs;
  if (vpBrief && !(briefs || []).some(b => b.id === vpBrief.id)) vpClearBrief('This brief is no longer available. Its source may have been deleted or its retention limit reached.');
  const list = $('vp-history'); list.replaceChildren();
  for (const b of (briefs || []).slice(0, 5)) {
    const button = text('button', `${b.created_at ? new Date(b.created_at).toLocaleString() : 'Saved brief'} · ${b.facts?.length ?? b.fact_count ?? ''} passages`, 'vp-history-button');
    button.type = 'button'; button.onclick = () => run(async () => {
      if (!vpCanReplace()) return;
      if (b.facts) await vpRenderBrief(b); else { const full = await vpExport(b.id, 'json', true); await vpRenderBrief(full); }
      $('vp-result').scrollIntoView({behavior: 'smooth', block: 'start'});
    }, button); list.append(button);
  }
  if (!briefs?.length) list.append(text('p', 'No saved briefs yet.'));
}
async function vpExport(id, format, returnData = false) {
  const epoch = vpEpoch;
  const response = await fetch(`/api/visitprep/briefs/${encodeURIComponent(id)}/export?format=${format}`, {headers: {Authorization: 'Bearer ' + token}});
  if (!response.ok) throw new Error('This brief is no longer available. Its source may have been deleted.');
  if (returnData) { const data = await response.json(); if (epoch !== vpEpoch) throw new Error('This brief view changed. Open the current saved brief again.'); return data; }
  const blob = await response.blob(); if (epoch !== vpEpoch) return; const url = URL.createObjectURL(blob); const a = document.createElement('a');
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
  if (vpErasing) throw new Error('Data deletion is in progress. Wait before adding a record.');
  if (vpImporting) return;
  const epoch = vpEpoch, form = $('vp-add-form');
  const input = {title: $('vp-title').value, date: $('vp-record-date').value, kind: $('vp-kind').value, text: $('vp-record-text').value, synthetic: false};
  vpImporting = true;
  form.querySelectorAll('input,select,textarea,button').forEach(control => control.disabled = true);
  try {
    const record = await api('visitprep/records', 'POST', input);
    if (epoch !== vpEpoch) return;
    vpSelected.add(record.id); form.reset(); await visitprepLoad(); notice('Record saved locally. It has not been sent to an AI provider.');
  } finally {
    vpImporting = false;
    form.querySelectorAll('input,select,textarea,button').forEach(control => control.disabled = false);
  }
}, e.submitter); };
$('vp-brief-form').onsubmit = e => { e.preventDefault(); run(async () => {
  if (vpErasing) throw new Error('Data deletion is in progress. Wait before preparing a brief.');
  if (!vpPatient) throw new Error('Connect to your private space first.');
  if (!vpCanReplace()) return;
  if (!vpSelected.size) throw new Error('Select at least one record.');
  const provider = $('vp-provider').value;
  if (provider !== 'local' && !$('vp-cloud-consent').checked) throw new Error('Allow selected record text to be sent, or choose the local brief.');
  const epoch = vpEpoch, preparation = ++vpPrepareSequence; vpPreparing = preparation;
  const oldAgendaForm = $('vp-agenda-form');
  oldAgendaForm?.querySelectorAll('input,textarea,button').forEach(control => control.disabled = true);
  $('vp-progress').textContent = 'Checking access, reading selected sources and validating citations…';
  try {
    const brief = await api('visitprep/brief', 'POST', {patient_id: vpPatient.id, question: $('vp-question').value, provider, cloud_consent: provider !== 'local' && $('vp-cloud-consent').checked, record_ids: [...vpSelected]});
    if (epoch !== vpEpoch) return;
    await vpRenderBrief(brief); await vpHistory();
  } finally {
    if (vpPreparing === preparation) {
      vpPreparing = 0;
      const currentAgendaForm = $('vp-agenda-form');
      if (currentAgendaForm) {
        currentAgendaForm.querySelectorAll('input,textarea,button').forEach(control => control.disabled = false);
        $('vp-print-agenda').disabled = $('vp-download-agenda').disabled = !vpAgenda?.approved || vpDirty;
      }
      $('vp-progress').textContent = ''; $('vp-cloud-consent').checked = false;
    }
  }
}, e.submitter); };
$('vp-reset-demo').onclick = e => { if (confirm('Restore the fictional demo records into this empty workspace?')) run(async () => { if (vpErasing) throw new Error('Data deletion is in progress.'); await api('visitprep/demo/reset', 'POST'); vpSelectionInitialized = false; await visitprepLoad(); }, e.currentTarget); };

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

$('vp-print-close').onclick = () => { $('vp-print-dialog').close(); $('vp-print-frame').removeAttribute('srcdoc'); };
$('vp-print-now').onclick = () => { $('vp-print-frame').contentWindow.focus(); $('vp-print-frame').contentWindow.print(); };
