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

function confirmRepair(pk, name) {
  document.getElementById('repairVehicleForm').action = '/vehicles/' + pk + '/repair/';
  document.getElementById('repairVehicleName').textContent = name;
  bootstrap.Modal.getOrCreateInstance(document.getElementById('repairConfirmModal')).show();
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
