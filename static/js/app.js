const $ = (id) => document.getElementById(id);
const form = $('search-form'), range = $('range'), message = $('message'), results = $('results');

range.addEventListener('change', () => $('custom-dates').classList.toggle('d-none', range.value !== 'custom'));
function text(value) { return value === null || value === undefined || value === '' ? '-' : String(value); }
function node(tag, content, className) { const element = document.createElement(tag); element.textContent = content; if (className) element.className = className; return element; }
function prettyPayload(value) {
  const raw = value == null ? '' : String(value);
  try { return JSON.stringify(JSON.parse(raw), null, 2); } catch (_) {}
  if (/^\s*</.test(raw)) { try { return new XMLSerializer().serializeToString(new DOMParser().parseFromString(raw, 'application/xml')).replace(/></g, '>\n<'); } catch (_) {} }
  return raw;
}
function render(data) {
  $('summary-rrn').textContent = data.rrn; $('summary-environment').textContent = data.environment;
  $('summary-ace').textContent = data.summary.ace_records; $('summary-dtl').textContent = data.summary.dtl_records;
  const services = $('services'); services.replaceChildren();
  const errorDetails = $('error-details'); errorDetails.replaceChildren();
  data.services.forEach(item => {
    const row = document.createElement('tr'); ['service_name','url','status','error_source','error_code'].forEach(key => { const cell = document.createElement('td'); if (key === 'status') { cell.append(node('span', text(item[key]), 'status')); } else { cell.textContent = text(item[key]); } row.append(cell); }); services.append(row);
    if (item.error_desc !== null && item.error_desc !== undefined && String(item.error_desc).trim()) {
      const detail = document.createElement('article'); detail.className = 'error-detail';
      const heading = node('h3', text(item.service_name), 'error-detail-title');
      const meta = node('p', `Status ${text(item.status)} · ${text(item.error_source)} · ${text(item.error_code)}`, 'error-detail-meta');
      const description = node('p', String(item.error_desc), 'error-detail-description');
      detail.append(heading, meta, description); errorDetails.append(detail);
    }
  });
  $('services-empty').classList.toggle('d-none', data.services.length !== 0);
  $('error-details-section').classList.toggle('d-none', !errorDetails.childElementCount);
  const timeline = $('timeline'); timeline.replaceChildren();
  data.audit_timeline.forEach(item => { const entry = document.createElement('article'); entry.className = 'timeline-item'; entry.append(node('div', text(item.timestamp), 'timeline-time'), node('div', text(item.log_point), 'timeline-point')); const payload = document.createElement('details'); payload.className = 'payload'; payload.open = true; payload.append(node('summary', 'Payload'), node('pre', prettyPayload(item.payload))); entry.append(payload); timeline.append(entry); });
  $('timeline-empty').classList.toggle('d-none', data.audit_timeline.length !== 0); results.classList.remove('d-none');
  if (!data.summary.ace_records && !data.summary.dtl_records) showMessage(`No ESB audit records found for RRN ${data.rrn} within the selected time range.`, 'info'); else hideMessage();
}
function showMessage(value, type = 'danger') { message.textContent = value; message.className = `alert alert-${type} mt-4 mb-0`; }
function hideMessage() { message.classList.add('d-none'); }
form.addEventListener('submit', async (event) => { event.preventDefault(); hideMessage(); const rrn = $('rrn').value.trim(); if (!rrn) { showMessage('RRN is required.'); return; } const payload = { rrn, environment: $('environment').value, range: range.value }; if (payload.range === 'custom') { payload.from_date = $('from-date').value; payload.to_date = $('to-date').value; } const button = $('submit'); button.disabled = true; button.querySelector('.button-text').textContent = 'Searching…'; button.querySelector('.spinner-border').classList.remove('d-none'); try { const response = await fetch('/api/audit/search', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) }); const data = await response.json(); if (!response.ok || !data.success) throw new Error(data.message || 'Database query failed.'); render(data); } catch (error) { showMessage(error.message); } finally { button.disabled = false; button.querySelector('.button-text').textContent = 'Execute Query'; button.querySelector('.spinner-border').classList.add('d-none'); } });
