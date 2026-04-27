// Generic fetch helper for JSON
async function fetchJSON(url) {
  const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  return res.json();
}

// ── Driver modal helpers ──────────────────────────────────────────────────────
function openEditDriver(pk) {
  fetchJSON('/drivers/' + pk + '/data/').then(function (d) {
    document.getElementById('editDriverPk').value = d.id;
    document.getElementById('editDriverForm').action = '/drivers/' + d.id + '/edit/';
    document.getElementById('editFirstName').value = d.first_name;
    document.getElementById('editLastName').value = d.last_name;
    document.getElementById('editLicenseNumber').value = d.license_number;
    document.getElementById('editPhone').value = d.phone;
    document.getElementById('editEmail').value = d.email;
    document.getElementById('editAddress').value = d.address;
    document.getElementById('editLicenseExpiry').value = d.license_expiry;
    document.getElementById('editDateJoined').value = d.date_joined;
    document.getElementById('editDriverStatus').value = d.status;
    bootstrap.Modal.getOrCreateInstance(document.getElementById('editDriverModal')).show();
  });
}

function confirmDeleteDriver(pk, name) {
  document.getElementById('deleteDriverForm').action = '/drivers/' + pk + '/delete/';
  document.getElementById('deleteDriverName').textContent = name;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('deleteDriverModal')).show();
}