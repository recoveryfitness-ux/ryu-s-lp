(function () {
  'use strict';

  /* =========================================================
     RYU-S AI チャットアシスタント
     Google Gemini API（無料枠）を使用
     API_KEY を Google AI Studio で取得して下記に貼り付けてください
     https://aistudio.google.com/app/apikey
  ========================================================= */

  const API_KEY = 'AQ.Ab8RN6KVMtZKNwyh-C_N-SrZxo185BD2WSjx9HgwMRLMKeM2gQ';
  const API_URL =
    'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent';

  /* ── LP 知識ベース（システムプロンプト）── */
  const SYSTEM_INSTRUCTION = [
    'あなたはRECOVERY FITNESS RYU-S（リューズ）立川店の公式AIアシスタントです。',
    '以下に記載されたLP情報のみをもとに、来店を検討しているお客様の質問に日本語で丁寧かつ簡潔に回答してください。',
    '',
    '【基本情報】',
    '店舗名: RECOVERY FITNESS RYU-S（リューズ）立川店',
    '住所: 〒190-0023 東京都立川市柴崎町2-4-17-202（2階）',
    'アクセス: JR立川駅南口 徒歩5分',
    '電話: 042-847-9898',
    '営業時間: 平日10:00〜22:00、土日祝10:00〜20:00、定休日：不定休',
    'スタイル: 完全個室・完全予約制・同時3名限定',
    '実績: Google口コミ★5.0、96.7%が初回で変化を実感',
    '予約: LINEまたはWebフォームから24時間受付、当日1時間前まで予約可能',
    '',
    '【提供サービス】',
    '1. リカバリーコンディショニング（VRC®）',
    '   世界TOP50病院が導入した医療由来の血流改善技術。ベッドに寝るだけで受けられる。',
    '   疲労・睡眠不足・むくみ・冷えの根本改善に対応。',
    '',
    '2. 仙骨整体',
    '   骨盤・仙骨へのアプローチ。姿勢改善・疲労回復・自律神経の調整。',
    '',
    '3. パーソナルトレーニング',
    '   フィットネス業界歴21年・指導実績1,000名超のトレーナー郡隆二によるマンツーマン指導。',
    '',
    '4. 深層パーソナルストレッチ（新メニュー）',
    '   深層筋へのアプローチで関節可動域拡大・肩こり腰痛ケア。チケット制（月会費なし）。',
    '',
    '【料金プラン】',
    '■ 無料体験（初回限定）: ¥0 / 約60分',
    '  内容: カウンセリング＋姿勢チェック＋トレーニング＋仙骨整体＋リカバリーコンディショニング',
    '',
    '■ 回数券（月会費なし・3プログラム共通・家族友人とシェア可）',
    '  1チケット＝1プログラム×15分。トータルリカバリーには3枚必要。',
    '  10枚チケット: ¥36,000（ボーナス+1枚=実質11枚、有効6ヶ月、1枚あたり約¥3,273）',
    '  20枚チケット: ¥68,000（ボーナス+3枚=実質23枚、有効9ヶ月、1枚あたり約¥2,957）',
    '  30枚チケット: ¥93,800（ボーナス+5枚=実質35枚、有効12ヶ月、1枚あたり¥2,680）',
    '',
    '■ トータルリカバリーコース（月額制・未消化分翌月繰り越し可）',
    '  楽-RAKU-（月2回）: ¥18,700（1回あたり¥9,350）',
    '  巡-MEGURI-（月4回）: ¥33,660（1回あたり¥8,415）＋AI姿勢チェック3ヶ月毎',
    '  流-RYU-（月8回・おすすめ）: ¥59,840（1回あたり¥7,480）＋AI姿勢チェック3ヶ月毎',
    '  都度利用: トータルリカバリー¥12,000/回、深層ほぐし¥3,000/回',
    '  オプション 深層ほぐし: 4回/月¥8,000、8回/月¥16,000',
    '  休会費: ¥2,200/月、プラン変更手数料: ¥2,200/回',
    '  通常入会金: ¥55,000、登録手数料: ¥5,500',
    '',
    '【現在のキャンペーン（〜2026年9月30日まで・先着10名・残り5名）】',
    '  入会金¥55,000 → 0円、登録手数料¥5,500 → 0円',
    '  月会費 永久15%OFF（全プラン対象）',
    '  ※無料体験は9/30まで。10月以降は有料体験予定。',
    '',
    '【キャンセル・運営ルール】',
    '  キャンセル・変更: 2時間前までであれば無料（マイページから24時間手続き可）',
    '  無断キャンセルは回数消化となる場合あり',
    '  退会・休会・プラン変更の締切: 毎月10日',
    '',
    '【よくある質問と回答】',
    'Q: 肩こりや膝の痛みがあっても通える？',
    'A: はい、むしろ不調がある方こそ力になれます。VRC®と仙骨整体で体の土台を整えてからトレーニングするので安心です。',
    '',
    'Q: 運動が苦手・初めてでも大丈夫？',
    'A: まったく問題ありません。セッションの約半分はリカバリーに充て、ベッドに寝るだけのメニューもあります。',
    '',
    'Q: 持ち物・ウェアは必要？',
    'A: 手ぶらでOKです。リカバリーウェア・アロマおしぼり・炭酸水は無料。更衣室にリファドライヤー・ストレートアイロン完備。スーツのままでもお越しいただけます。',
    '',
    'Q: 子ども連れでも大丈夫？',
    'A: 歓迎しています（施設内での走り回りはご遠慮ください）。年齢制限もありません。',
    '',
    'Q: 効果を感じるまでどのくらいかかる？筋肉痛はある？',
    'A: 96.7%が初回から変化を実感。継続的な改善は2〜3ヶ月が目安ですが、1〜2回で変化を感じる方が多いです。セッション内でリカバリーも行うため筋肉痛もほとんどありません。',
    '',
    'Q: 一般の整体・マッサージとの違いは？',
    'A: 血管（VRC®）→骨格（仙骨整体）→トレーニングの三段階で根本改善する、立川エリア唯一のリカバリー専門ジムです。',
    '',
    '【回答ルール】',
    '・上記にない情報を聞かれた場合は「詳しくは初回の無料カウンセリングでご案内します。お気軽にご予約ください！」と答えてください。',
    '・競合他社との比較やRYU-Sに無関係な質問には答えないでください。',
    '・回答は400文字以内を目安に、親しみやすい丁寧語で書いてください。',
    '・絵文字は1〜2個程度ならOKです。',
    '・必要に応じて予約を促す一言を添えてください。',
  ].join('\n');

  let history = [];

  /* ── スタイル ── */
  var css = document.createElement('style');
  css.textContent = '\
#ryus-chat-btn{\
  position:fixed;bottom:24px;right:24px;z-index:9999;\
  width:60px;height:60px;border-radius:50%;\
  background:linear-gradient(135deg,#c9952a,#f0b840);\
  color:#fff;border:none;cursor:pointer;\
  box-shadow:0 4px 20px rgba(201,149,42,.55);\
  font-size:26px;display:flex;align-items:center;justify-content:center;\
  transition:transform .2s,box-shadow .2s;\
}\
#ryus-chat-btn:hover{transform:scale(1.08);box-shadow:0 6px 28px rgba(201,149,42,.65);}\
#ryus-chat-btn.open{background:linear-gradient(135deg,#2c1b3e,#4a2d6b);font-size:20px;}\
#ryus-chat-win{\
  position:fixed;bottom:96px;right:24px;z-index:9998;\
  width:340px;max-width:calc(100vw - 32px);\
  height:480px;max-height:calc(100vh - 120px);\
  background:#fff;border-radius:16px;\
  box-shadow:0 8px 40px rgba(44,27,62,.22);\
  display:flex;flex-direction:column;overflow:hidden;\
  transform:scale(.9) translateY(20px);opacity:0;\
  transition:transform .25s cubic-bezier(.34,1.56,.64,1),opacity .2s;\
  pointer-events:none;\
}\
#ryus-chat-win.open{transform:scale(1) translateY(0);opacity:1;pointer-events:auto;}\
#ryus-chat-hd{\
  background:linear-gradient(135deg,#2c1b3e,#3d2560);\
  color:#fff;padding:14px 16px;\
  display:flex;align-items:center;gap:10px;flex-shrink:0;\
}\
.ryus-av{\
  width:36px;height:36px;border-radius:50%;\
  background:linear-gradient(135deg,#c9952a,#f0b840);\
  display:flex;align-items:center;justify-content:center;\
  font-size:18px;flex-shrink:0;\
}\
.ryus-hd-title{font-size:13px;font-weight:700;line-height:1.3;}\
.ryus-hd-sub{font-size:11px;opacity:.7;margin-top:2px;}\
#ryus-chat-msgs{\
  flex:1;overflow-y:auto;padding:14px 12px;\
  display:flex;flex-direction:column;gap:10px;\
  background:#fdf6f0;\
}\
#ryus-chat-msgs::-webkit-scrollbar{width:4px;}\
#ryus-chat-msgs::-webkit-scrollbar-thumb{background:#ddd;border-radius:4px;}\
.ryus-msg{display:flex;flex-direction:column;max-width:85%;}\
.ryus-msg.bot{align-self:flex-start;}\
.ryus-msg.user{align-self:flex-end;}\
.ryus-bubble{\
  padding:10px 13px;border-radius:14px;\
  font-size:13px;line-height:1.7;\
}\
.ryus-msg.bot .ryus-bubble{\
  background:#fff;border:1px solid #ecdcc8;\
  border-bottom-left-radius:4px;color:#2d1f23;\
  box-shadow:0 1px 4px rgba(0,0,0,.06);\
}\
.ryus-msg.user .ryus-bubble{\
  background:linear-gradient(135deg,#2c1b3e,#3d2560);\
  color:#fff;border-bottom-right-radius:4px;\
}\
.ryus-time{font-size:10px;color:#bbb;margin-top:3px;padding:0 3px;}\
.ryus-msg.user .ryus-time{text-align:right;}\
.ryus-typing{\
  display:flex;align-items:center;gap:4px;\
  padding:12px 14px;background:#fff;\
  border:1px solid #ecdcc8;border-radius:14px;\
  border-bottom-left-radius:4px;align-self:flex-start;\
  box-shadow:0 1px 4px rgba(0,0,0,.06);\
}\
.ryus-typing span{\
  width:7px;height:7px;border-radius:50%;background:#c9952a;\
  animation:ryus-dot 1.2s ease-in-out infinite;\
}\
.ryus-typing span:nth-child(2){animation-delay:.2s;}\
.ryus-typing span:nth-child(3){animation-delay:.4s;}\
@keyframes ryus-dot{\
  0%,60%,100%{transform:translateY(0);opacity:.5;}\
  30%{transform:translateY(-5px);opacity:1;}\
}\
#ryus-chat-ft{\
  padding:10px 12px;background:#fff;\
  border-top:1px solid #f0e6dc;flex-shrink:0;\
  display:flex;gap:8px;align-items:flex-end;\
}\
#ryus-chat-inp{\
  flex:1;border:1.5px solid #ddd;border-radius:20px;\
  padding:9px 14px;font-size:13px;resize:none;\
  font-family:inherit;line-height:1.5;max-height:80px;\
  outline:none;transition:border-color .2s;\
  background:#fff;\
}\
#ryus-chat-inp:focus{border-color:#c9952a;}\
#ryus-chat-inp::placeholder{color:#bbb;}\
#ryus-chat-send{\
  width:38px;height:38px;border-radius:50%;\
  background:#c9952a;color:#fff;border:none;cursor:pointer;\
  display:flex;align-items:center;justify-content:center;\
  flex-shrink:0;transition:background .2s;font-size:15px;\
}\
#ryus-chat-send:hover{background:#f0b840;}\
#ryus-chat-send:disabled{background:#ddd;cursor:not-allowed;}\
#ryus-chat-note{\
  text-align:center;font-size:10px;color:#bbb;\
  padding:4px 8px 8px;flex-shrink:0;background:#fff;\
}\
@media(max-width:400px){\
  #ryus-chat-win{right:12px;width:calc(100vw - 24px);}\
  #ryus-chat-btn{bottom:16px;right:16px;}\
}\
  ';
  document.head.appendChild(css);

  /* ── HTML ── */
  var wrap = document.createElement('div');
  wrap.innerHTML =
    '<button id="ryus-chat-btn" aria-label="AIアシスタントを開く">💬</button>' +
    '<div id="ryus-chat-win" role="dialog" aria-label="RYU-S AIアシスタント">' +
      '<div id="ryus-chat-hd">' +
        '<div class="ryus-av">✨</div>' +
        '<div>' +
          '<div class="ryus-hd-title">RYU-S AIアシスタント</div>' +
          '<div class="ryus-hd-sub">ご質問にお答えします</div>' +
        '</div>' +
      '</div>' +
      '<div id="ryus-chat-msgs"></div>' +
      '<div id="ryus-chat-ft">' +
        '<textarea id="ryus-chat-inp" placeholder="質問を入力してください…" rows="1"></textarea>' +
        '<button id="ryus-chat-send" aria-label="送信">&#9658;</button>' +
      '</div>' +
      '<div id="ryus-chat-note">RYU-S のLP情報をもとに回答します</div>' +
    '</div>';
  document.body.appendChild(wrap);

  var chatBtn  = document.getElementById('ryus-chat-btn');
  var chatWin  = document.getElementById('ryus-chat-win');
  var chatMsgs = document.getElementById('ryus-chat-msgs');
  var chatInp  = document.getElementById('ryus-chat-inp');
  var chatSend = document.getElementById('ryus-chat-send');

  /* ── 開閉 ── */
  chatBtn.addEventListener('click', function () {
    var isOpen = chatWin.classList.toggle('open');
    chatBtn.classList.toggle('open', isOpen);
    chatBtn.setAttribute('aria-label', isOpen ? 'チャットを閉じる' : 'AIアシスタントを開く');
    chatBtn.textContent = isOpen ? '✕' : '💬';
    if (isOpen && chatMsgs.children.length === 0) {
      addBot('こんにちは！RYU-S 立川のAIアシスタントです。\n料金・サービス・アクセスなど、お気軽にご質問ください😊');
    }
    if (isOpen) { setTimeout(function () { chatInp.focus(); }, 300); }
  });

  /* ── メッセージ表示 ── */
  function now() {
    var d = new Date();
    return d.getHours() + ':' + ('0' + d.getMinutes()).slice(-2);
  }
  function addMsg(text, role) {
    var div = document.createElement('div');
    div.className = 'ryus-msg ' + role;
    div.innerHTML =
      '<div class="ryus-bubble">' + text.replace(/\n/g, '<br>') + '</div>' +
      '<div class="ryus-time">' + now() + '</div>';
    chatMsgs.appendChild(div);
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
  }
  function addBot(t)  { addMsg(t, 'bot'); }
  function addUser(t) { addMsg(t, 'user'); }

  function showTyping() {
    var d = document.createElement('div');
    d.id = 'ryus-typing';
    d.className = 'ryus-msg bot';
    d.innerHTML = '<div class="ryus-typing"><span></span><span></span><span></span></div>';
    chatMsgs.appendChild(d);
    chatMsgs.scrollTop = chatMsgs.scrollHeight;
  }
  function hideTyping() {
    var el = document.getElementById('ryus-typing');
    if (el) el.remove();
  }

  /* ── Gemini API 呼び出し ── */
  function callGemini(userText) {
    history.push({ role: 'user', parts: [{ text: userText }] });

    var body = JSON.stringify({
      system_instruction: { parts: [{ text: SYSTEM_INSTRUCTION }] },
      contents: history,
      generationConfig: { maxOutputTokens: 800, temperature: 0.3 }
    });

    return fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': API_KEY
      },
      body: body
    })
    .then(function (res) {
      if (!res.ok) throw new Error('API ' + res.status);
      return res.json();
    })
    .then(function (data) {
      var reply = (data.candidates &&
                   data.candidates[0] &&
                   data.candidates[0].content &&
                   data.candidates[0].content.parts &&
                   data.candidates[0].content.parts[0] &&
                   data.candidates[0].content.parts[0].text)
                 || 'うまく回答できませんでした。恐れ入りますが直接お電話ください：042-847-9898';
      history.push({ role: 'model', parts: [{ text: reply }] });
      return reply;
    });
  }

  /* ── 送信 ── */
  function doSend() {
    var text = chatInp.value.trim();
    if (!text) return;
    chatInp.value = '';
    chatInp.style.height = 'auto';
    chatSend.disabled = true;
    addUser(text);
    showTyping();
    callGemini(text)
      .then(function (reply) {
        hideTyping();
        addBot(reply);
      })
      .catch(function () {
        hideTyping();
        addBot('通信エラーが発生しました。しばらくしてから再度お試しください。\nお急ぎの場合はお電話（042-847-9898）でどうぞ。');
      })
      .then(function () {
        chatSend.disabled = false;
        chatInp.focus();
      });
  }

  chatSend.addEventListener('click', doSend);
  chatInp.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(); }
  });
  chatInp.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 80) + 'px';
  });

})();
