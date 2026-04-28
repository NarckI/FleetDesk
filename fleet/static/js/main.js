// Generic fetch helper for JSON
async function fetchJSON(url) {
  const res = await fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
  return res.json();
}

// ── Render Django messages as Bootstrap toasts (reads JSON from template) ──────
document.addEventListener('DOMContentLoaded', function() {
  try {
    var msgsEl = document.getElementById('django-messages');
    var container = document.getElementById('toast-container');
    if (!msgsEl || !container) return;
    var msgs = JSON.parse(msgsEl.textContent || '[]');
    msgs.forEach(function(m) {
      var tags = (m.tags || '').toLowerCase();
      var bgClass = 'bg-light text-dark';
      var useWhiteClose = false;
      if (tags.indexOf('success') !== -1) { bgClass = 'bg-success text-white'; useWhiteClose = true; }
      else if (tags.indexOf('error') !== -1 || tags.indexOf('danger') !== -1) { bgClass = 'bg-danger text-white'; useWhiteClose = true; }
      else if (tags.indexOf('warning') !== -1) { bgClass = 'bg-warning text-dark'; }
      else if (tags.indexOf('info') !== -1) { bgClass = 'bg-info text-dark'; }

      var toastEl = document.createElement('div');
      toastEl.className = 'toast align-items-center ' + bgClass + ' border-0 mb-2';
      toastEl.setAttribute('role','alert');
      toastEl.setAttribute('aria-live','assertive');
      toastEl.setAttribute('aria-atomic','true');
      toastEl.setAttribute('data-bs-autohide','true');
      toastEl.setAttribute('data-bs-delay','3000');

      var inner = document.createElement('div');
      inner.className = 'd-flex';
      var body = document.createElement('div');
      body.className = 'toast-body';
      body.textContent = m.message || '';
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'btn-close me-2 m-auto' + (useWhiteClose ? ' btn-close-white' : '');
      btn.setAttribute('data-bs-dismiss','toast');
      btn.setAttribute('aria-label','Close');

      inner.appendChild(body);
      inner.appendChild(btn);
      toastEl.appendChild(inner);
      container.appendChild(toastEl);

      try { var t = new bootstrap.Toast(toastEl); t.show(); } catch (e) { /* bootstrap missing */ }
    });
  } catch (e) {
    console.error('Could not render django messages as toasts', e);
  }
});

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

// ── Vehicle modal helpers ─────────────────────────────────────────────────────
function openEditVehicle(pk) {
  fetchJSON('/vehicles/' + pk + '/data/').then(function (d) {
    document.getElementById('editVehicleForm').action = '/vehicles/' + d.id + '/edit/';
    document.getElementById('editPlateNumber').value = d.plate_number;
    document.getElementById('editVehicleRegistration').value = d.vehicle_registration;
    document.getElementById('editVehicleType').value = d.vehicle_type;
    document.getElementById('editBrand').value = d.brand;
    document.getElementById('editModel').value = d.model;
    document.getElementById('editYear').value = d.year;
    document.getElementById('editMileage').value = d.mileage;
    document.getElementById('editLastMaintenance').value = d.last_maintenance;
    document.getElementById('editVehicleStatus').value = d.status;
    document.getElementById('editOrExpiry').value = d.or_expiry;
    document.getElementById('editCrExpiry').value = d.cr_expiry;
    document.getElementById('editCpcExpiry').value = d.cpc_expiry;
    bootstrap.Modal.getOrCreateInstance(document.getElementById('editVehicleModal')).show();
  });
}

function confirmDeleteVehicle(pk, name, brand, model) {
  document.getElementById('deleteVehicleForm').action = '/vehicles/' + pk + '/delete/';
  document.getElementById('deleteVehicleName').textContent = name;
  document.getElementById('deleteVehicleBrand').textContent = brand;
  document.getElementById('deleteVehicleModel').textContent = model;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('deleteVehicleModal')).show();
}

function confirmRepair(pk, name, brand, model) {
  document.getElementById('repairVehicleForm').action = '/vehicles/' + pk + '/repair/';
  document.getElementById('repairVehicleName').textContent = name;
  document.getElementById('repairVehicleBrand').textContent = brand;
  document.getElementById('repairVehicleModel').textContent = model;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('repairConfirmModal')).show();
}

// ── Contract modal helpers ────────────────────────────────────────────────────
function openAddContract() {
  Promise.all([fetchJSON('/contracts/drivers/'), fetchJSON('/contracts/vehicles/')]).then(function (results) {
    var driverSel = document.getElementById('addContractDriver');
    var vehicleSel = document.getElementById('addContractVehicle');
    driverSel.innerHTML = '<option value="">Select driver</option>';
    vehicleSel.innerHTML = '<option value="">Select vehicle</option>';
    results[0].drivers.forEach(function (d) {
      driverSel.innerHTML += '<option value="' + d.id + '">' + d.first_name + ' ' + d.last_name + '</option>';
    });
    results[1].vehicles.forEach(function (v) {
      vehicleSel.innerHTML += '<option value="' + v.id + '">' + v.plate_number + ' - ' + v.brand + ' ' + v.model + '</option>';
    });
    bootstrap.Modal.getOrCreateInstance(document.getElementById('addContractModal')).show();
  });
}

function openEditContract(pk) {
  Promise.all([
    fetchJSON('/contracts/' + pk + '/data/'),
    fetchJSON('/contracts/drivers/'),
    fetchJSON('/contracts/vehicles/'),
  ]).then(function (results) {
    console.log('Contract data loaded:', results);
    var d = results[0];
    var driverSel = document.getElementById('editContractDriver');
    var vehicleSel = document.getElementById('editContractVehicle');

    console.log('Driver select elem:', driverSel, 'Vehicle select elem:', vehicleSel);
    console.log('Contract data:', d);

    // Populate drivers (include current driver even if has active contract)
    driverSel.innerHTML = '<option value="' + d.driver_id + '">' + d.driver_name + '</option>';
    results[1].drivers.forEach(function (dr) {
      if (dr.id !== d.driver_id) {
        driverSel.innerHTML += '<option value="' + dr.id + '">' + dr.first_name + ' ' + dr.last_name + '</option>';
      }
    });

    // Populate vehicles (include current vehicle even if in-use)
    vehicleSel.innerHTML = '<option value="' + d.vehicle_id + '">' + d.vehicle_display + '</option>';
    results[2].vehicles.forEach(function (v) {
      if (v.id !== d.vehicle_id) {
        vehicleSel.innerHTML += '<option value="' + v.id + '">' + v.plate_number + ' - ' + v.brand + ' ' + v.model + '</option>';
      }
    });

    document.getElementById('editContractForm').action = '/contracts/' + d.id + '/edit/';
    document.getElementById('editContractDailyRate').value = d.daily_rate;
    document.getElementById('editContractStartDate').value = d.start_date;
    document.getElementById('editContractEndDate').value = d.end_date;
    document.getElementById('editContractStatus').value = d.status;

    console.log('Form populated, showing modal');
    bootstrap.Modal.getOrCreateInstance(document.getElementById('editContractModal')).show();
  }).catch(function (err) {
    console.error('Failed to load contract edit data:', err);
    alert('Error loading contract edit data. Check browser console.');
    bootstrap.Modal.getOrCreateInstance(document.getElementById('editContractModal')).show();
  });
}

function confirmTerminateContract(pk, name) {
  document.getElementById('terminateContractForm').action = '/contracts/' + pk + '/delete/';
  document.getElementById('terminateContractName').textContent = name;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('terminateContractModal')).show();
}

// ── Payment modal helpers ─────────────────────────────────────────────────────
function openPartialPayment(pk, balance) {
  document.getElementById('partialPayForm').action = '/payments/' + pk + '/partial/';
  document.getElementById('partialBalance').textContent = '₱' + parseFloat(balance).toLocaleString('en-PH', {minimumFractionDigits: 2});
  document.getElementById('partialAmount').value = '';
  document.getElementById('partialAmount').max = balance;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('partialPayModal')).show();
}

function confirmDeletePayment(pk) {
  document.getElementById('deletePaymentForm').action = '/payments/' + pk + '/delete/';
  bootstrap.Modal.getOrCreateInstance(document.getElementById('deletePaymentModal')).show();
}


// ── live search ─────────────────────────────────────────────────────
const searchInput = document.querySelector('input[name="q"]');
const rows = document.querySelectorAll('tbody tr');

if (searchInput && rows.length > 0) {
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            const first = cells[0]?.textContent.toLowerCase();
            const second = cells[1]?.textContent.toLowerCase();
            const third = cells[2]?.textContent.toLowerCase();
            const fourth = cells[3]?.textContent.toLowerCase();

            const match =
                first.includes(query) ||
                second.includes(query) ||
                third.includes(query) ||
                fourth.includes(query);

            row.style.display = query === '' || match ? '' : 'none';
        });
    });
}
