// Executa o app real com DOM mínimo e respostas HTTP controladas, sem TensorFlow.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');

const codigo = readFileSync(join(__dirname, '../../mnist_demo/web/app.js'), 'utf8');
const aguardar = () => new Promise(resolve => setImmediate(resolve));

function iniciarApp() {
  function elemento() {
    const classes = new Set();
    const eventos = {};
    return {
      textContent: '', className: '', dataset: {}, style: {}, width: 280, height: 280,
      classList: {
        add: c => classes.add(c), remove: c => classes.delete(c),
        contains: c => classes.has(c),
      },
      addEventListener: (tipo, acao) => { eventos[tipo] = acao; },
      disparar: (tipo, evento = {}) => eventos[tipo](evento),
      removeAttribute() {}, replaceChildren() {}, appendChild() {}, setPointerCapture() {},
      getBoundingClientRect: () => ({ left: 0, top: 0, width: 280, height: 280 }),
      toDataURL: () => 'data:image/png;base64,teste',
      getContext: () => ({ fillRect() {}, beginPath() {}, arc() {}, fill() {}, moveTo() {}, closePath() {} }),
    };
  }
  const elementos = new Map();
  const obter = id => {
    if (!elementos.has(id)) elementos.set(id, elemento());
    return elementos.get(id);
  };
  const aba = elemento();
  aba.dataset.tab = 'upload';
  const requisicoes = [];
  let inicializar;
  runInNewContext(codigo, {
    AbortController,
    document: {
      getElementById: obter,
      addEventListener: (_, acao) => { inicializar = acao; },
      querySelectorAll: seletor => seletor === '.tab-btn' ? [aba] : [],
      createElement: elemento,
    },
    window: { addEventListener() {} },
    fetch: url => new Promise((resolve, reject) => requisicoes.push({
      url, falhar: reject,
      responder: (dados, ok = true) => resolve({ ok, json: async () => dados }),
    })),
  });
  inicializar();
  const desenhar = () => obter('paint-canvas').disparar('pointerdown', {
    preventDefault() {}, pointerId: 1, clientX: 100, clientY: 100,
  });
  return {
    obter, requisicoes, desenhar,
    trocarAba: () => aba.disparar('click'),
    predizer: () => { desenhar(); obter('btn-predizer-canvas').disparar('click'); },
    status: () => obter('status-badge').textContent,
  };
}

for (const interacao of ['desenhar', 'trocarAba']) {
  for (const disponivel of [true, false]) {
    test(`status atrasado após ${interacao}: modelo ${disponivel ? 'presente' : 'ausente'}`, async () => {
      const app = iniciarApp();
      app[interacao]();
      assert.equal(app.status(), 'Verificando modelo...');
      app.requisicoes[0].responder({ modelo_disponivel: disponivel });
      await aguardar();
      assert.equal(app.status(), disponivel ? 'CNN Pronta' : 'Modelo Ausente');
      if (!disponivel) {
        assert.match(app.obter('mensagem-alerta').textContent, /CNN ou calibração não encontradas/);
        assert.equal(app.obter('mensagem-alerta').classList.contains('hidden'), false);
      }
    });
  }
}

test('falha de status após uma interação mostra servidor offline', async () => {
  const app = iniciarApp();
  app.trocarAba();
  app.requisicoes[0].falhar(new Error('offline'));
  await aguardar();
  assert.equal(app.status(), 'Servidor Offline');
});

for (const falha of [false, true]) {
  test(`consulta ativa mantém Processando com ${falha ? 'falha' : 'resposta'} de status`, async () => {
    const app = iniciarApp();
    app.predizer();
    assert.equal(app.requisicoes[1].url, '/api/predizer');
    if (falha) app.requisicoes[0].falhar(new Error('offline'));
    else app.requisicoes[0].responder({ modelo_disponivel: true });
    await aguardar();
    assert.equal(app.status(), 'Processando...');
    app.obter('btn-limpar').disparar('click');
    assert.equal(app.status(), falha ? 'Servidor Offline' : 'CNN Pronta');
  });
}

for (const falha of [false, true]) {
  test(`predição concluída tem prioridade sobre ${falha ? 'falha' : 'ausência'} atrasada do status`, async () => {
    const app = iniciarApp();
    app.predizer();
    app.requisicoes[1].responder({
      previsto: 1, confianca: 0.95, temperatura: 1.512,
      probabilidades: [0.01, 0.95, 0.01, 0.01, 0.01, 0.002, 0.002, 0.002, 0.002, 0.002],
    });
    await aguardar();
    if (falha) app.requisicoes[0].falhar(new Error('offline'));
    else app.requisicoes[0].responder({ modelo_disponivel: false });
    await aguardar();
    assert.equal(app.status(), 'CNN Pronta');
    assert.equal(app.obter('resultado-detalhes').classList.contains('hidden'), false);
    assert.equal(app.obter('mensagem-alerta').classList.contains('hidden'), true);
    app.desenhar();
    assert.equal(app.status(), 'CNN Pronta');
  });
}
