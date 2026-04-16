// Constantes de validação
const EMAIL_RE = /^[a-zA-Z0-9._%+\-]+@(gmail|hotmail|yahoo|outlook|live|icloud)\.(com|com\.br|net|org)$/i;
const SYM_RE   = /[!@#$%^&*()\-_=+\[\]{};:'",.<>/?\\|`~]/;
const DATE_RE  = /^(\d{2})\/(\d{2})\/(\d{4})$/;
const NOME_RE = /^[a-zA-ZÀ-ÿ\s]{8,}$/; 

/* validação do nome */
function valNome() {
    const v = $('c-nome').value.trim();
    if (!v) {
        clrErr('f-cn', 'e-cn');
        return;
    }

    // Verifica se tem pelo menos 8 caracteres e se contém apenas letras e espaços
    if (v.length < 8) {
        setErr('f-cn', 'e-cn', 'O nome deve ter no mínimo 8 caracteres');
    } else if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(v)) {
        setErr('f-cn', 'e-cn', 'O nome não pode conter números ou símbolos');
    } else {
        clrErr('f-cn', 'e-cn');
    }
}

/* helpers */
const $ = id => document.getElementById(id);
const setErr = (fid, eid, msg) => { 
    if($(fid)) $(fid).classList.add('has-error'); 
    if($(eid)) $(eid).textContent = msg; 
};
const clrErr = (fid, eid) => { 
    if($(fid)) $(fid).classList.remove('has-error'); 
    if($(eid)) $(eid).textContent = ''; 
};

function clrF(fid, eid) { clrErr(fid, eid); }
function clearGlobal()  { if($('err-global')) $('err-global').textContent = ''; }

/* tab */
function switchTab(tab) {
    $('track').style.transform = tab === 'login' ? 'translateX(0)' : 'translateX(-50%)';
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
    if (!v) {
        clrErr('f-ce', 'e-ce');
        return;
    }
    if (!EMAIL_RE.test(v)) {
        setErr('f-ce', 'e-ce', 'E-mail inválido (ex: nome@gmail.com)');
    } else {
        clrErr('f-ce', 'e-ce');
    }
}

/* data de nascimento */
function valDatadeNascimento(event) {
    const input = $('c-data_de_nascimento');
    let v = input.value.replace(/\D/g, ''); // Remove tudo que não é número
    
    // Aplicando a máscara de data (DD/MM/AAAA)
    if (v.length > 2 && v.length <= 4) {
        v = v.replace(/(\d{2})(\d+)/, '$1/$2');
    } else if (v.length > 4) {
        v = v.replace(/(\d{2})(\d{2})(\d+)/, '$1/$2/$3');
    }
    input.value = v;

    // Se a data estiver completa (10 caracteres), validamos a fundo
    if (v.length === 10) {
        const [dia, mes, ano] = v.split('/').map(Number);
        
        // Criamos o objeto Date (Mês no JS começa em 0, por isso mes - 1)
        const dataNasc = new Date(ano, mes - 1, dia);
        const hoje = new Date();
        
        // --- VALIDAÇÃO DE EXISTÊNCIA REAL ---
        // Verificamos se o JS não "rolou" a data para o mês seguinte
        const dataExiste = (
            dataNasc.getFullYear() === ano && 
            dataNasc.getMonth() === mes - 1 && 
            dataNasc.getDate() === dia
        );

        // Cálculo da idade
        let idade = hoje.getFullYear() - dataNasc.getFullYear();
        const m = hoje.getMonth() - dataNasc.getMonth();
        if (m < 0 || (m === 0 && hoje.getDate() < dataNasc.getDate())) {
            idade--;
        }

        // --- SEQUÊNCIA DE ERROS ---
        if (!dataExiste) {
            setErr('f-cd', 'e-cd', 'Esta data não existe');
        } else if (ano < 1900) {
            setErr('f-cd', 'e-cd', 'Ano muito antigo');
        } else if (dataNasc > hoje) {
            setErr('f-cd', 'e-cd', 'Você ainda não nasceu!');
        } else if (idade < 18) {
            setErr('f-cd', 'e-cd', 'Você deve ter pelo menos 18 anos');
        } else {
            // Se passou em tudo, limpa o erro
            clrErr('f-cd', 'e-cd');
        }
    } else {
        // Enquanto o usuário digita, não mostramos erro de "data incompleta"
        // para não irritar o usuário, apenas limpamos se houver um antigo.
        clrErr('f-cd', 'e-cd');
    }
}

/* senha strength */
function strength(v) {
    return { 
        len: v.length >= 8, 
        num: /\d/.test(v), 
        let: /[a-zA-Z]/.test(v), 
        sym: SYM_RE.test(v) 
    };
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

    // Se o usuário começar a digitar de novo, limpamos o erro de "requisitos não atendidos"
    clrErr('f-cs', 'e-cs');
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

    if (!email) { setErr('f-le','e-le','Informe o e-mail'); ok = false; }
    else if (!EMAIL_RE.test(email)) { setErr('f-le','e-le','E-mail inválido'); ok = false; }

    if (!senha) { setErr('f-ls','e-ls','Informe a senha'); ok = false; }

    // SE TUDO ESTIVER OK NO FRONT-END, ENVIA PARA O BACK-END (FASTAPI)
    if (ok) {
        $('form-login').submit();
    }
}

/* cadastro */
function doCadastro() {
    if (event) event.preventDefault();
    const nome     = $('c-nome').value.trim();
    const email    = $('c-email').value.trim();
    const dataNasc = $('c-data_de_nascimento').value.trim();
    const senha    = $('c-senha').value;
    const conf     = $('c-conf').value;
    
    let ok = true;

    // Limpa erros anteriores
    [['f-cn','e-cn'],['f-ce','e-ce'],['f-cd','e-cd'],['f-cs','e-cs'],['f-cc','e-cc']].forEach(([f,e]) => clrErr(f,e));

    if (!nome) { 
        setErr('f-cn','e-cn','Informe seu nome'); 
        ok = false; 
    } else if (nome.length < 8) {
        setErr('f-cn', 'e-cn', 'O nome deve ter no mínimo 8 caracteres');
        ok = false;
    } else if (!/^[a-zA-ZÀ-ÿ\s]+$/.test(nome)) {
        setErr('f-cn', 'e-cn', 'O nome não deve conter números ou símbolos');
        ok = false;
    }

    if (!email) { setErr('f-ce','e-ce','Informe o e-mail'); ok = false; }
    else if (!EMAIL_RE.test(email)) { setErr('f-ce','e-ce','E-mail inválido'); ok = false; }

    const s = strength(senha);
    if (!senha || !(s.len && s.num && s.let && s.sym)) {
        setErr('f-cs','e-cs','A senha não atende aos requisitos');
        $('hints').classList.add('show');
        ok = false;
    }

    if (!dataNasc) {
        setErr('f-cd', 'e-cd', 'Informe sua data de nascimento');
        ok = false;
    } else if (!DATE_RE.test(dataNasc)) {
        setErr('f-cd', 'e-cd', 'Formato inválido (DD/MM/AAAA)');
        ok = false;
    } else {
        // Verificação extra de 18 anos no clique do botão
        const [d, m, a] = dataNasc.split('/').map(Number);
        const nasc = new Date(a, m - 1, d);
        const hoje = new Date();
        let idade = hoje.getFullYear() - nasc.getFullYear();
        if (hoje.getMonth() < m-1 || (hoje.getMonth() === m-1 && hoje.getDate() < d)) idade--;

        if (idade < 18) {
            setErr('f-cd', 'e-cd', 'Menores de 18 anos não são permitidos');
            ok = false;
        }
    }

    if (!conf) { setErr('f-cc','e-cc','Confirme sua senha'); ok = false; }
    else if (senha !== conf) { setErr('f-cc','e-cc','As senhas não coincidem'); ok = false; }

    // SE TUDO ESTIVER OK NO FRONT-END, ENVIA PARA O BACK-END (FASTAPI)
    if (ok) {
        $('form-cadastro').submit(); // Aqui ele envia para o FastAPI
    } 
}

function checarFormulario() {
    const btn = document.querySelector('.area-botao .btn');
    // Se todos os campos estiverem preenchidos (lógica simplificada)
    if ($('c-nome').value && $('c-email').value && $('c-data_de_nascimento').value.length === 10) {
        btn.style.opacity = "1";
    } else {
        btn.style.opacity = "0.5";
    }
}