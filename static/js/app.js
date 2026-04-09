const EMAIL_RE = /^[a-zA-Z0-9._%+\-]+@(gmail|hotmail|yahoo|outlook|live|icloud)\.(com|com\.br|net|org)$/i;
const SYM_RE   = /[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]/;

/* helpers */
const $  = id => document.getElementById(id);
const setErr = (fid, eid, msg) => { $(fid).classList.add('has-error'); $(eid).textContent = msg; };
const clrErr = (fid, eid)      => { $(fid).classList.remove('has-error'); $(eid).textContent = ''; };

function clrF(fid, eid) { clrErr(fid, eid); }
function clearGlobal()  { $('err-global').textContent = ''; }

/* tab */
function switchTab(tab) {
  $('track').style.transform = tab === 'login' ? 'translateX(0)' : 'translateX(-50.04%)';
  $('tab-login').classList.toggle('active', tab === 'login');
  $('tab-cad').classList.toggle('active',   tab === 'cad');
  clearGlobal();
}

/* eye toggle */
function togglePw(id, btn) {
  const inp = $(id);
  const show = inp.type === 'password';
  inp.type = show ? 'text' : 'password';
  btn.classList.toggle('on', show);
}

/* email */
function valEmail() {
  const v = $('c-email').value.trim();
  v && !EMAIL_RE.test(v)
    ? setErr('f-ce', 'e-ce', 'E-mail inválido (ex: nome@gmail.com)')
    : clrErr('f-ce', 'e-ce');
}

/* senha strength */
function strength(v) {
  return { len: v.length >= 8, num: /\d/.test(v), let: /[a-zA-Z]/.test(v), sym: SYM_RE.test(v) };
}

function valSenha() {
  const v = $('c-senha').value;
  const h = $('hints');

  if (!v) { h.classList.remove('show'); return; }
  h.classList.add('show');

  const s = strength(v);
  $('h-len').classList.toggle('ok', s.len);
  $('h-num').classList.toggle('ok', s.num);
  $('h-let').classList.toggle('ok', s.let);
  $('h-sym').classList.toggle('ok', s.sym);

  clrErr('f-cs', 'e-cs');
  if ($('c-conf').value) valConf();
}

/* confirm */
function valConf() {
  const s = $('c-senha').value, c = $('c-conf').value;
  c && s !== c ? setErr('f-cc', 'e-cc', 'As senhas não coincidem') : clrErr('f-cc', 'e-cc');
}

/* login */
function doLogin() {
  const email = $('l-email').value.trim();
  const senha = $('l-senha').value;
  let ok = true;

  clrErr('f-le','e-le'); clrErr('f-ls','e-ls'); clearGlobal();

  if (!email)               { setErr('f-le','e-le','Informe o e-mail'); ok = false; }
  else if (!EMAIL_RE.test(email)) { setErr('f-le','e-le','E-mail inválido (ex: nome@gmail.com)'); ok = false; }

  if (!senha) { setErr('f-ls','e-ls','Informe a senha'); ok = false; }

  if (ok) $('err-global').textContent = 'Senha ou usuário incorreto';
}

/* cadastro */
function doCadastro() {
  const nome  = $('c-nome').value.trim();
  const email = $('c-email').value.trim();
  const senha = $('c-senha').value;
  const conf  = $('c-conf').value;
  let ok = true;

  [['f-cn','e-cn'],['f-ce','e-ce'],['f-cs','e-cs'],['f-cc','e-cc']].forEach(([f,e]) => clrErr(f,e));

  if (!nome)  { setErr('f-cn','e-cn','Informe seu nome'); ok = false; }

  if (!email) { setErr('f-ce','e-ce','Informe o e-mail'); ok = false; }
  else if (!EMAIL_RE.test(email)) { setErr('f-ce','e-ce','E-mail inválido (ex: nome@gmail.com)'); ok = false; }

  const s = strength(senha);
  if (!senha || !(s.len && s.num && s.let && s.sym)) {
    setErr('f-cs','e-cs','A senha não atende aos requisitos');
    $('hints').classList.add('show');
    if (senha) { $('h-len').classList.toggle('ok',s.len); $('h-num').classList.toggle('ok',s.num); $('h-let').classList.toggle('ok',s.let); $('h-sym').classList.toggle('ok',s.sym); }
    ok = false;
  }

  if (!conf)        { setErr('f-cc','e-cc','Confirme sua senha'); ok = false; }
  else if (senha !== conf) { setErr('f-cc','e-cc','As senhas não coincidem'); ok = false; }

  if (ok) alert('Conta criada com sucesso! 🎬');
}
