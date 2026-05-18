const API = "http://localhost:5000/api";
let currentUser = null;
let chartInst   = null;

/* ── UTILS ── */
const $ = id => document.getElementById(id);
const get  = url => fetch(API+url).then(r=>r.json());
const post = (url,d) => fetch(API+url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(r=>r.json());
const put  = (url,d) => fetch(API+url,{method:'PUT', headers:{'Content-Type':'application/json'},body:JSON.stringify(d)}).then(r=>r.json());
const del  = url => fetch(API+url,{method:'DELETE'}).then(r=>r.json());

function toast(msg, type='success'){
  const t = $('toast');
  t.textContent = msg;
  t.className = `toast show ${type}`;
  setTimeout(() => t.className = 'toast', 2800);
}

function togglePw(id, btn){
  const f = $(id);
  f.type = f.type === 'password' ? 'text' : 'password';
  btn.textContent = f.type === 'password' ? '👁' : '🙈';
}

function initials(name){
  return name.split(' ').slice(0,2).map(w=>w[0]).join('').toUpperCase();
}

/* ── AUTH ── */
function switchAuth(mode){
  $('form-login').style.display    = mode === 'login'    ? 'block' : 'none';
  $('form-register').style.display = mode === 'register' ? 'block' : 'none';
  $('login-err').classList.remove('show');
  $('reg-err').classList.remove('show');
}

async function doLogin(){
  const identifier = $('login-id').value.trim();
  const password   = $('login-pw').value.trim();
  const errEl      = $('login-err');
  const btn        = $('btn-login');

  if(!identifier || !password){
    errEl.textContent = 'Email/NIM dan password wajib diisi.';
    errEl.classList.add('show');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Memproses...';
  try {
    const res = await post('/login', {identifier, password});
    if(res.status === 'success'){
      currentUser = res.data;
      enterApp();
      toast(res.message, 'success');
    } else {
      errEl.textContent = res.message;
      errEl.classList.add('show');
    }
  } catch(e){
    errEl.textContent = 'Tidak bisa terhubung ke server. Pastikan backend berjalan.';
    errEl.classList.add('show');
  }
  btn.disabled = false;
  btn.textContent = 'Masuk';
}

async function doRegister(){
  const name     = $('reg-name').value.trim();
  const nim      = $('reg-nim').value.trim();
  const email    = $('reg-email').value.trim();
  const prodi    = $('reg-prodi').value.trim();
  const password = $('reg-pw').value.trim();
  const errEl    = $('reg-err');
  const btn      = $('btn-reg');

  if(!name || !nim || !email || !prodi || !password){
    errEl.textContent = 'Semua field wajib diisi.';
    errEl.classList.add('show');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Mendaftarkan...';
  try {
    const res = await post('/register', {name, nim, email, prodi, password});
    if(res.status === 'success'){
      toast(res.message, 'success');
      switchAuth('login');
      $('login-id').value = email;
    } else {
      errEl.textContent = res.message;
      errEl.classList.add('show');
    }
  } catch(e){
    errEl.textContent = 'Tidak bisa terhubung ke server.';
    errEl.classList.add('show');
  }
  btn.disabled = false;
  btn.textContent = 'Daftar Sekarang';
}

function enterApp(){
  $('auth-screen').classList.add('hidden');
  $('app-screen').classList.remove('hidden');
  $('side-avatar').textContent = initials(currentUser.name);
  $('side-name').textContent   = currentUser.name.split(' ')[0];
  $('side-role').textContent   = currentUser.role;
  $('top-user').textContent    = currentUser.name;
  loadDashboard();
}

function doLogout(){
  if(!confirm('Yakin ingin keluar?')) return;
  currentUser = null;
  if(chartInst){ chartInst.destroy(); chartInst = null; }
  $('app-screen').classList.add('hidden');
  $('auth-screen').classList.remove('hidden');
  $('login-id').value = '';
  $('login-pw').value = '';
  switchAuth('login');
}

/* ── NAVIGATION ── */
const pageTitles = {
  dashboard: 'Dashboard',
  books: 'Katalog Buku',
  members: 'Anggota',
  borrowings: 'Peminjaman',
  borrow: 'Smart Borrowing',
  profile: 'Profil Saya'
};

function navigate(page, el){
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  // Hapus active dari user-chip jika bukan halaman profil
  const chip = $('user-chip-btn');
  chip.classList.remove('active-chip');
  if(page === 'profile'){
    chip.classList.add('active-chip');
  } else if(el) {
    el.classList.add('active');
  }
  $('page-'+page).classList.add('active');
  $('page-title').textContent = pageTitles[page];
  ({
    dashboard: loadDashboard,
    books: () => loadBooks(),
    members: loadMembers,
    borrowings: loadBorrowings,
    borrow: loadBorrow,
    profile: loadProfile
  })[page]?.();
}

/* ── DASHBOARD ── */
async function loadDashboard(){
  const [stats, borrows, monthly] = await Promise.all([
    get('/stats'), get('/borrowings'), get('/borrowings/monthly')
  ]);
  const d = stats.data;
  $('s-books').textContent    = d.total_books;
  $('s-members').textContent  = d.total_members;
  $('s-active').textContent   = d.active_borrowings;
  $('s-returned').textContent = d.returned;

  // Recent table
  const t = $('dash-recent');
  t.innerHTML = '<tr><th>Anggota</th><th>Status</th></tr>';
  borrows.data.slice(-5).reverse().forEach(b => {
    const badge = b.status === 'borrowed'
      ? '<span class="badge badge-amber">Dipinjam</span>'
      : '<span class="badge badge-green">Dikembalikan</span>';
    t.innerHTML += `<tr>
      <td style="font-size:12px;">${b.member_name}<br>
        <span style="font-size:11px;color:var(--muted);">${b.book_title}</span>
      </td>
      <td>${badge}</td>
    </tr>`;
  });

  drawChart(monthly.data);
}

function drawChart(data){
  const canvas = $('mainChart');
  if(!canvas) return;
  if(chartInst){ chartInst.destroy(); chartInst = null; }

  const gridColor = 'rgba(0,0,0,0.05)';
  const textColor = '#888780';

  chartInst = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: data.labels,
      datasets: [
        {
          label: 'Peminjaman',
          data: data.borrowed,
          backgroundColor: '#1D9E75',
          borderRadius: 5,
          borderSkipped: false,
          barPercentage: 0.55,
          categoryPercentage: 0.7,
        },
        {
          label: 'Pengembalian',
          data: data.returned,
          backgroundColor: '#EF9F27',
          borderRadius: 5,
          borderSkipped: false,
          barPercentage: 0.55,
          categoryPercentage: 0.7,
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {display: false},
        tooltip: {
          backgroundColor: '#fff',
          titleColor: '#2C2C2A',
          bodyColor: '#5F5E5A',
          borderColor: '#D3D1C7',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y} buku`
          }
        }
      },
      scales: {
        x: {
          grid: {display: false},
          border: {display: false},
          ticks: {color: textColor, font: {size: 12}}
        },
        y: {
          beginAtZero: true,
          grid: {color: gridColor, drawTicks: false},
          border: {display: false, dash: [4,4]},
          ticks: {color: textColor, font: {size: 11}, stepSize: 5, padding: 8}
        }
      }
    }
  });
}

/* ── BOOKS ── */
async function loadBooks(q=''){
  const res = await get('/books'+(q ? `?q=${q}` : ''));
  const t = $('books-table');
  t.innerHTML = '<tr><th>Judul</th><th>Pengarang</th><th>Tahun</th><th>Kategori</th><th>Stok</th><th>Aksi</th></tr>';
  res.data.forEach(b => {
    const stk = b.stock > 0
      ? `<span class="badge badge-green">${b.stock} tersedia</span>`
      : `<span class="badge badge-red">Habis</span>`;
    t.innerHTML += `<tr>
      <td><strong>${b.title}</strong></td>
      <td>${b.author}</td>
      <td>${b.year}</td>
      <td>${b.category}</td>
      <td>${stk}</td>
      <td><div class="btn-group">
        <button class="btn btn-warning btn-sm" onclick="editBook(${b.id})">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteBook(${b.id})">Hapus</button>
      </div></td>
    </tr>`;
  });
}

function searchBooks(q){ loadBooks(q); }

function openModal(type){
  $('modal-'+type).classList.add('open');
  if(type === 'book'){
    $('modal-book-title').textContent = 'Tambah Buku';
    $('book-edit-id').value = '';
    ['book-title','book-author','book-year','book-category','book-stock'].forEach(id => $(id).value = '');
  } else {
    $('modal-member-title').textContent = 'Tambah Anggota';
    $('member-edit-id').value = '';
    ['member-name','member-nim','member-prodi','member-email'].forEach(id => $(id).value = '');
  }
}

function closeModal(type){ $('modal-'+type).classList.remove('open'); }

async function editBook(id){
  const res = await get('/books/'+id);
  const b = res.data;
  $('modal-book-title').textContent = 'Edit Buku';
  $('book-edit-id').value  = b.id;
  $('book-title').value    = b.title;
  $('book-author').value   = b.author;
  $('book-year').value     = b.year;
  $('book-category').value = b.category;
  $('book-stock').value    = b.stock;
  $('modal-book').classList.add('open');
}

async function saveBook(){
  const editId = $('book-edit-id').value;
  const data = {
    title:    $('book-title').value,
    author:   $('book-author').value,
    year:     parseInt($('book-year').value),
    category: $('book-category').value,
    stock:    parseInt($('book-stock').value)
  };
  const res = editId ? await put('/books/'+editId, data) : await post('/books', data);
  toast(res.message, res.status === 'success' ? 'success' : 'error');
  if(res.status === 'success'){ closeModal('book'); loadBooks(); }
}

async function deleteBook(id){
  if(!confirm('Yakin hapus buku ini?')) return;
  const res = await del('/books/'+id);
  toast(res.message, res.status === 'success' ? 'success' : 'error');
  loadBooks();
}

/* ── MEMBERS ── */
async function loadMembers(){
  const res = await get('/members');
  const t = $('members-table');
  t.innerHTML = '<tr><th>Nama</th><th>NIM</th><th>Program Studi</th><th>Email</th><th>Status</th><th>Aksi</th></tr>';
  res.data.forEach(m => {
    const s = m.active
      ? '<span class="badge badge-green">Aktif</span>'
      : '<span class="badge badge-red">Nonaktif</span>';
    t.innerHTML += `<tr>
      <td><strong>${m.name}</strong></td>
      <td>${m.nim}</td>
      <td>${m.prodi}</td>
      <td>${m.email}</td>
      <td>${s}</td>
      <td><div class="btn-group">
        <button class="btn btn-warning btn-sm" onclick="editMember(${m.id})">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteMember(${m.id})">Hapus</button>
      </div></td>
    </tr>`;
  });
}

async function editMember(id){
  const res = await get('/members/'+id);
  const m = res.data;
  $('modal-member-title').textContent = 'Edit Anggota';
  $('member-edit-id').value  = m.id;
  $('member-name').value     = m.name;
  $('member-nim').value      = m.nim;
  $('member-prodi').value    = m.prodi;
  $('member-email').value    = m.email;
  $('modal-member').classList.add('open');
}

async function saveMember(){
  const editId = $('member-edit-id').value;
  const data = {
    name:  $('member-name').value,
    nim:   $('member-nim').value,
    prodi: $('member-prodi').value,
    email: $('member-email').value
  };
  const res = editId ? await put('/members/'+editId, data) : await post('/members', data);
  toast(res.message, res.status === 'success' ? 'success' : 'error');
  if(res.status === 'success'){ closeModal('member'); loadMembers(); }
}

async function deleteMember(id){
  if(!confirm('Hapus anggota ini?')) return;
  const res = await del('/members/'+id);
  toast(res.message, res.status === 'success' ? 'success' : 'error');
  loadMembers();
}

/* ── BORROWINGS ── */
async function loadBorrowings(){
  const res = await get('/borrowings');
  const t = $('borrowings-table');
  t.innerHTML = '<tr><th>Anggota</th><th>Buku</th><th>Tgl Pinjam</th><th>Tgl Kembali</th><th>Status</th><th>Aksi</th></tr>';
  res.data.forEach(b => {
    const badge = b.status === 'borrowed'
      ? '<span class="badge badge-amber">Dipinjam</span>'
      : '<span class="badge badge-green">Dikembalikan</span>';
    const btnR = b.status === 'borrowed'
      ? `<button class="btn btn-primary btn-sm" onclick="returnBook(${b.id})">Kembalikan</button>`
      : '';
    t.innerHTML += `<tr>
      <td>${b.member_name}</td>
      <td>${b.book_title}</td>
      <td>${b.borrow_date}</td>
      <td>${b.return_date || '—'}</td>
      <td>${badge}</td>
      <td><div class="btn-group">
        ${btnR}
        <button class="btn btn-danger btn-sm" onclick="deleteBorrowing(${b.id})">Hapus</button>
      </div></td>
    </tr>`;
  });
}

async function returnBook(id){
  const res = await post('/return/'+id, {});
  toast(res.message, res.status === 'success' ? 'success' : 'error');
  loadBorrowings();
}

async function deleteBorrowing(id){
  if(!confirm('Hapus data peminjaman ini?')) return;
  const res = await del('/borrowings/'+id);
  toast(res.message, 'success');
  loadBorrowings();
}

/* ── PROFILE ── */
async function loadProfile(){
  const u = currentUser;
  if(!u) return;

  // Avatar & nama besar
  $('profile-avatar-big').textContent = initials(u.name);
  $('profile-fullname').textContent   = u.name;
  $('profile-role-badge').textContent = u.role;
  $('profile-nim').textContent        = u.nim  || '—';
  $('profile-prodi').textContent      = u.prodi || '—';

  // Grid info
  $('p-name').textContent  = u.name  || '—';
  $('p-nim').textContent   = u.nim   || '—';
  $('p-email').textContent = u.email || '—';
  $('p-prodi').textContent = u.prodi || '—';
  $('p-role').textContent  = u.role  || '—';
  $('p-status').innerHTML  = u.active !== false
    ? '<span class="badge badge-green">Aktif</span>'
    : '<span class="badge badge-red">Nonaktif</span>';

  // Riwayat peminjaman milik user ini (filter by nim atau id)
  const t = $('profile-borrow-table');
  t.innerHTML = '<tr><th>Buku</th><th>Tgl Pinjam</th><th>Tgl Kembali</th><th>Status</th></tr>';
  try {
    const res = await get('/borrowings');
    const myBorrows = res.data.filter(b =>
      b.member_nim === u.nim || b.member_id === u.id || b.member_name === u.name
    );
    if(myBorrows.length === 0){
      t.innerHTML += `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:20px;">
        Belum ada riwayat peminjaman.</td></tr>`;
    } else {
      myBorrows.reverse().forEach(b => {
        const badge = b.status === 'borrowed'
          ? '<span class="badge badge-amber">Dipinjam</span>'
          : '<span class="badge badge-green">Dikembalikan</span>';
        t.innerHTML += `<tr>
          <td><strong>${b.book_title}</strong></td>
          <td>${b.borrow_date}</td>
          <td>${b.return_date || '—'}</td>
          <td>${badge}</td>
        </tr>`;
      });
    }
  } catch(e){
    t.innerHTML += `<tr><td colspan="4" style="text-align:center;color:var(--muted);padding:16px;">
      Gagal memuat riwayat.</td></tr>`;
  }
}

/* ── SMART BORROWING ── */
async function loadBorrow(){
  const [mRes, bRes] = await Promise.all([get('/members'), get('/books')]);
  $('borrow-member').innerHTML = mRes.data.map(m =>
    `<option value="${m.id}">${m.name} (${m.nim})</option>`).join('');
  $('borrow-book').innerHTML = bRes.data.map(b =>
    `<option value="${b.id}" ${b.stock < 1 ? 'disabled' : ''}>${b.title} — stok: ${b.stock}</option>`).join('');
  $('borrow-result').className = 'borrow-result';
}

async function submitBorrow(){
  const book_id   = parseInt($('borrow-book').value);
  const member_id = parseInt($('borrow-member').value);
  const res = await post('/borrow', {book_id, member_id});
  const el = $('borrow-result');
  if(res.status === 'success'){
    el.textContent = '✅ ' + res.message;
    el.className = 'borrow-result ok';
    toast(res.message, 'success');
  } else {
    el.textContent = '❌ ' + res.message;
    el.className = 'borrow-result fail';
    toast(res.message, 'error');
  }
  loadBorrow();
}

/* ── ENTER KEY SUPPORT ── */
document.addEventListener('keydown', e => {
  if(e.key !== 'Enter') return;
  if($('form-login').style.display !== 'none') doLogin();
  else if($('form-register').style.display !== 'none') doRegister();
});
