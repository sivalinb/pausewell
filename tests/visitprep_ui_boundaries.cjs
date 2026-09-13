#!/usr/bin/env node
/*
 * Reusable VisitPrep asynchronous-state regression checks.
 *
 * Usage: node work/visitprep_ui_boundaries.cjs outputs/pausewell
 * After adoption into the repository: node tests/visitprep_ui_boundaries.cjs .
 *
 * Requires only Node's standard library. Reads the actual web/visitprep.js and
 * executes it in a fresh VM with synthetic data and a minimal DOM adapter.
 * No server, browser, provider, secrets, network, or application writes are used.
 * These checks cover state/async boundaries, not CSS, browser APIs, or layout.
 */

'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const repository = path.resolve(process.argv[2] || process.cwd());
const script = fs.readFileSync(path.join(repository, 'web/visitprep.js'), 'utf8');

function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return {promise, resolve};
}

function createHarness() {
  const elements = new Map();
  const downloads = [];
  const objects = new Set();

  function element(tag = 'div') {
    return {
      tag, children: [], options: [], value: '', disabled: false,
      textContent: '', resetCount: 0,
      append(...items) { this.children.push(...items); },
      replaceChildren(...items) { this.children = items; },
      close() { this.open = false; },
      showModal() { this.open = true; },
      removeAttribute(name) { delete this[name]; },
      setAttribute() {},
      reset() { this.resetCount++; },
      querySelectorAll() { return []; },
      scrollIntoView() {},
      click() {
        if (tag === 'a') downloads.push({href: this.href, name: this.download});
      },
    };
  }

  function get(id) {
    if (!elements.has(id)) elements.set(id, element());
    return elements.get(id);
  }

  const context = {
    Set,
    token: 'synthetic-ui-test-token',
    document: {createElement: element},
    $: get,
    text: (tag, value) => Object.assign(element(tag), {textContent: value}),
    confirm: () => true,
    notice() {},
    run: async callback => callback(),
    api: () => { throw new Error('Unexpected API call: stub the specific test boundary'); },
    fetch: () => { throw new Error('Unexpected fetch: stub the specific test boundary'); },
    URL: {
      createObjectURL() {
        const value = 'blob:synthetic-' + (downloads.length + 1);
        objects.add(value);
        return value;
      },
      revokeObjectURL(value) { objects.delete(value); },
    },
  };
  vm.createContext(context);
  vm.runInContext(script, context, {filename: 'web/visitprep.js'});

  function evaluate(code) { return vm.runInContext(code, context); }
  function approve() {
    evaluate("vpBrief={id:'synthetic-brief'}; vpAgenda={approved:true,revision:1}; vpDirty=false;");
  }
  function renderedText(node) {
    return String(node.textContent || '') + ' ' + node.children.map(renderedText).join(' ');
  }

  return {context, evaluate, approve, get, downloads, objects, renderedText};
}

async function runChecks() {
  const passed = [];

  // Hold the response body, edit the same brief, then complete the old export.
  // An ID-only guard would incorrectly download that already-approved version.
  {
    const h = createHarness();
    h.approve();
    const body = deferred();
    const bodyRequested = deferred();
    h.context.fetch = async () => ({
      ok: true, headers: {get: () => '1'},
      blob() { bodyRequested.resolve(); return body.promise; },
    });
    const pending = h.evaluate("vpAgendaExport('markdown')");
    await bodyRequested.promise;
    h.evaluate('vpDirty=true');
    body.resolve({synthetic: true});
    await pending;
    assert.equal(h.downloads.length, 0);
    assert.equal(h.objects.size, 0);
    passed.push('Dirty same-brief edits suppress a pending approved export');
  }

  // Another page may have approved a newer server revision. Its response must
  // not silently substitute for the exact revision the current page reviewed.
  {
    const h = createHarness();
    h.approve();
    let bodyRead = false;
    h.context.fetch = async () => ({
      ok: true, headers: {get: () => '2'},
      async blob() { bodyRead = true; return {}; },
    });
    await assert.rejects(h.evaluate("vpAgendaExport('markdown')"), /saved agenda has changed/);
    assert.equal(bodyRead, false);
    assert.equal(h.downloads.length, 0);
    passed.push('A server revision mismatch rejects the export');
  }

  // Positive control: a clean, approved matching version must still download.
  {
    const h = createHarness();
    h.approve();
    h.context.fetch = async () => ({
      ok: true, headers: {get: () => '1'}, blob: async () => ({synthetic: true}),
    });
    await h.evaluate("vpAgendaExport('markdown')");
    assert.equal(h.downloads.length, 1);
    assert.equal(h.downloads[0].name, 'visitprep-approved-agenda.md');
    assert.equal(h.objects.size, 0);
    passed.push('A matching approved export succeeds and revokes its temporary URL');
  }

  // A bootstrap started before erasure must not restore its captured records.
  // Verify immediate cached record, source-dialog, history, and preview removal.
  {
    const h = createHarness();
    const bootstrap = deferred();
    h.context.api = () => bootstrap.promise;
    h.evaluate("vpRecords=[{id:'old',title:'PRIVATE_SOURCE',text:'PRIVATE_TEXT',date:'2026-01-01',kind:'visit',synthetic:false}]; vpSelected.add('old'); vpRenderRecords();");
    h.get('vp-source-dialog-text').textContent = 'PRIVATE_TEXT';
    h.get('vp-source-dialog-title').textContent = 'PRIVATE_SOURCE';
    h.get('vp-source-dialog').open = true;
    h.get('vp-print-frame').srcdoc = '<p>PRIVATE_TEXT</p>';
    h.get('vp-print-dialog').open = true;
    h.get('vp-history').replaceChildren(h.context.text('p', 'PRIVATE_HISTORY'));
    assert.match(h.renderedText(h.get('vp-records')), /PRIVATE_TEXT/);

    const pending = h.evaluate('visitprepLoad()');
    h.evaluate('vpClearWorkspace()');
    assert.equal(h.evaluate('vpRecords.length'), 0);
    assert.equal(h.evaluate('vpSelected.size'), 0);
    assert.equal(h.evaluate('vpBrief'), null);
    assert.equal(h.evaluate('vpPatient'), null);
    assert.equal(h.get('vp-source-dialog-text').textContent, '');
    assert.equal(h.get('vp-source-dialog').open, false);
    assert.equal(h.get('vp-print-frame').srcdoc, undefined);
    assert.equal(h.get('vp-print-dialog').open, false);
    assert.equal(h.get('vp-add-form').resetCount, 1);
    assert.equal(h.get('vp-brief-form').resetCount, 1);
    assert.doesNotMatch(h.renderedText(h.get('vp-records')), /PRIVATE/);
    assert.doesNotMatch(h.renderedText(h.get('vp-history')), /PRIVATE/);

    bootstrap.resolve({records: [{id: 'old', text: 'PRIVATE_TEXT'}], patient: {}, providers: []});
    await pending;
    assert.equal(h.evaluate('vpRecords.length'), 0);
    assert.doesNotMatch(h.renderedText(h.get('vp-records')), /PRIVATE/);
    passed.push('Erasure clears cached content and suppresses an older bootstrap');
  }

  // The browser must not dispatch global erasure while its record import is
  // still pending: a late import could otherwise recreate data after erasure.
  {
    const h = createHarness();
    h.evaluate('vpImporting=true');
    assert.equal(h.evaluate('vpBeginErase()'), false);
    assert.equal(h.evaluate('vpErasing'), false);
    passed.push('Global erasure waits for an in-flight record import');
  }

  // The deletion flag is acquired synchronously before any asynchronous work.
  {
    const h = createHarness();
    assert.equal(h.evaluate('vpBeginErase()'), true);
    assert.equal(h.evaluate('vpErasing'), true);
    assert.equal(h.evaluate('vpBeginErase()'), false);
    h.evaluate('vpEndErase()');
    assert.equal(h.evaluate('vpErasing'), false);
    passed.push('Duplicate global erases are serialized and the flag is released');
  }

  console.log(JSON.stringify({
    suite: 'VisitPrep synthetic UI state boundaries',
    passed: passed.length, checks: passed,
    execution: 'Node VM with minimal DOM adapter; not browser rendering or integration testing',
    network_calls: 0,
  }, null, 2));
}

// Keep a deadline alive so a regression that never reaches a held boundary
// fails instead of letting Node exit successfully with an unresolved promise.
const deadline = setTimeout(() => {
  console.error('UI boundary checks did not finish within five seconds');
  process.exitCode = 1;
}, 5000);

runChecks().catch(error => {
  console.error(error);
  process.exitCode = 1;
}).finally(() => clearTimeout(deadline));
