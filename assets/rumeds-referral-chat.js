/**
 * Rumeds Referral Chat — 8-flow conversational engine
 * Persists state in localStorage; Flow 5 hooks via RumedsReferral.recordSuccess()
 */
(function () {
  const STORAGE_KEY = 'rumeds_referral_state';
  const REENGAGE_DAYS = 5;
  const REFERRALS_FOR_FREE = 3;
  const REWARD_AMOUNT = 500;

  const defaultState = () => ({
    userId: genUserId(),
    name: '',
    referralCode: '',
    referralCount: 0,
    walletAmount: 0,
    freeScrubUnlocked: false,
    freeScrubCode: '',
    lastVisit: Date.now(),
    lastReengageAt: 0,
    awaitingName: false,
    opened: false,
  });

  function genUserId() {
    return Math.random().toString(36).slice(2, 8).toUpperCase();
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? { ...defaultState(), ...JSON.parse(raw) } : defaultState();
    } catch {
      return defaultState();
    }
  }

  function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function sanitizeName(name) {
    return name.replace(/[^a-zA-Z]/g, '').toUpperCase().slice(0, 12) || 'DOCTOR';
  }

  function buildReferralCode(name, userId) {
    const last3 = userId.replace(/\D/g, '').slice(-3).padStart(3, '0');
    return `DR${sanitizeName(name)}${last3}`;
  }

  function buildFreeScrubCode(userId) {
    return `FREESCRUB${userId}`;
  }

  function daysSince(ts) {
    return (Date.now() - ts) / (1000 * 60 * 60 * 24);
  }

  function escapeHtml(text) {
    const d = document.createElement('div');
    d.textContent = text;
    return d.innerHTML;
  }

  function formatMessage(text) {
    return escapeHtml(text)
      .replace(/\n/g, '<br>')
      .replace(/👉 ([^\n<]+)/g, '<strong>👉 $1</strong>');
  }

  class RumedsReferralChat extends HTMLElement {
    constructor() {
      super();
      this.state = loadState();
      this.config = {
        websiteUrl: this.dataset.websiteUrl || window.location.origin,
        shopUrl: this.dataset.shopUrl || '/collections/all',
        whatsappNumber: (this.dataset.whatsappNumber || '').replace(/\D/g, ''),
        rewardAmount: parseInt(this.dataset.rewardAmount || String(REWARD_AMOUNT), 10),
        referralsForFree: parseInt(this.dataset.referralsForFree || String(REFERRALS_FOR_FREE), 10),
      };
    }

    connectedCallback() {
      this.panel = this.querySelector('[data-chat-panel]');
      this.messages = this.querySelector('[data-chat-messages]');
      this.form = this.querySelector('[data-chat-form]');
      this.input = this.querySelector('[data-chat-input]');
      this.toggle = this.querySelector('[data-chat-toggle]');
      this.quickActions = this.querySelector('[data-quick-actions]');

      this.toggle?.addEventListener('click', () => this.openChat(true));
      this.form?.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleUserInput(this.input.value.trim());
        this.input.value = '';
      });

      this.quickActions?.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;
        this.handleUserInput(btn.dataset.action);
      });

      this.messages?.addEventListener('click', (e) => {
        if (e.target.closest('[data-share-whatsapp]')) {
          this.shareOnWhatsApp();
        }
      });

      if (new URLSearchParams(window.location.search).get('referral_success') === '1') {
        this.recordReferralSuccess();
        history.replaceState({}, '', window.location.pathname);
      }

      const chatParam = new URLSearchParams(window.location.search).get('chat');
      const refParam = new URLSearchParams(window.location.search).get('ref');
      if (chatParam === 'hi' || refParam === 'qr' || refParam === 'welcome') {
        this.openChat(true);
        this.runFlow1();
        history.replaceState({}, '', window.location.pathname);
      }
    }

    openChat(userInitiated = false) {
      this.panel?.classList.add('is-open');
      this.toggle?.classList.add('is-hidden');
      if (!this.state.opened || userInitiated) {
        this.state.opened = true;
        if (this.shouldReengage()) {
          this.runFlow7();
        } else if (this.messages?.childElementCount === 0) {
          this.runFlow1();
        }
      }
      this.state.lastVisit = Date.now();
      saveState(this.state);
      this.input?.focus();
    }

    closeChat() {
      this.panel?.classList.remove('is-open');
      this.toggle?.classList.remove('is-hidden');
    }

    shouldReengage() {
      const { referralCount, lastReengageAt, lastVisit } = this.state;
      const target = this.config.referralsForFree;
      if (referralCount >= target) return false;
      if (daysSince(lastVisit) < REENGAGE_DAYS) return false;
      if (lastReengageAt && daysSince(lastReengageAt) < REENGAGE_DAYS) return false;
      return true;
    }

    addBotMessage(html, options = {}) {
      const el = document.createElement('div');
      el.className = 'rumeds-chat__msg rumeds-chat__msg--bot';
      el.innerHTML = `<div class="rumeds-chat__bubble">${html}</div>`;
      if (options.actions) {
        const actions = document.createElement('div');
        actions.className = 'rumeds-chat__actions';
        actions.innerHTML = options.actions;
        el.querySelector('.rumeds-chat__bubble').appendChild(actions);
      }
      this.messages?.appendChild(el);
      this.messages.scrollTop = this.messages.scrollHeight;
    }

    addUserMessage(text) {
      const el = document.createElement('div');
      el.className = 'rumeds-chat__msg rumeds-chat__msg--user';
      el.innerHTML = `<div class="rumeds-chat__bubble">${escapeHtml(text)}</div>`;
      this.messages?.appendChild(el);
      this.messages.scrollTop = this.messages.scrollHeight;
    }

    handleUserInput(raw) {
      if (!raw) return;
      this.addUserMessage(raw);
      const input = raw.toLowerCase().trim();

      if (this.state.awaitingName) {
        this.state.name = raw.trim();
        this.state.awaitingName = false;
        this.state.referralCode = buildReferralCode(this.state.name, this.state.userId);
        saveState(this.state);
        this.runFlow2();
        return;
      }

      if (/^(hi|hello|hey|start|help)$/i.test(input) || input === '👋') {
        this.runFlow1();
      } else if (input === '1' || /referral|code|share/.test(input)) {
        this.triggerFlow2();
      } else if (input === '2' || /explore|scrubs|shop/.test(input)) {
        this.runFlow8();
      } else if (input === '3' || /track|reward|wallet|progress/.test(input)) {
        this.runFlow4();
      } else {
        this.addBotMessage(
          formatMessage(
            "I didn't catch that.\n\nReply with:\n1️⃣ Get my referral code\n2️⃣ Explore scrubs\n3️⃣ Track my rewards"
          )
        );
      }
    }

    triggerFlow2() {
      if (!this.state.name) {
        this.state.awaitingName = true;
        saveState(this.state);
        this.addBotMessage(formatMessage("What's your first name, Doctor? 👨‍⚕️\n\nWe'll use it to create your personal referral code."));
        return;
      }
      if (!this.state.referralCode) {
        this.state.referralCode = buildReferralCode(this.state.name, this.state.userId);
        saveState(this.state);
      }
      this.runFlow2();
    }

    runFlow1() {
      this.addBotMessage(
        formatMessage(
          `👋 Welcome to Rumeds\nDesigned for doctors who don't get to slow down.\n\n🎁 Earn rewards on every referral\n\nReply with:\n1️⃣ Get my referral code\n2️⃣ Explore scrubs\n3️⃣ Track my rewards`
        )
      );
    }

    runFlow2() {
      const code = this.state.referralCode;
      const amt = this.config.rewardAmount;
      const shareBtn = this.config.whatsappNumber
        ? `<button type="button" class="rumeds-chat__btn rumeds-chat__btn--wa" data-share-whatsapp>Share on WhatsApp</button>`
        : '';

      this.addBotMessage(
        formatMessage(
          `🔐 Your Rumeds Referral Code:\n${code}\n\nShare this with fellow doctors 👇\n\n✅ They get ₹${amt} OFF\n✅ You get ₹${amt} credit\n\n🎯 ${this.config.referralsForFree} successful referrals = FREE scrub\n\nTap below to share:\n👉 Share on WhatsApp`
        ),
        { actions: shareBtn }
      );
    }

    getShareMessage() {
      const code = this.state.referralCode || buildReferralCode(this.state.name || 'DOC', this.state.userId);
      return (
        `Hey! I've been using Rumeds scrubs — super comfortable for long shifts.\n\n` +
        `You'll get ₹${this.config.rewardAmount} off with my code: ${code}\n\n` +
        `Check it out: ${this.config.websiteUrl}\n\n` +
        `Definitely worth it for duty hours.`
      );
    }

    shareOnWhatsApp() {
      const text = encodeURIComponent(this.getShareMessage());
      const num = this.config.whatsappNumber;
      const url = num ? `https://wa.me/${num}?text=${text}` : `https://wa.me/?text=${text}`;
      window.open(url, '_blank', 'noopener,noreferrer');
    }

    runFlow4() {
      const { referralCount, walletAmount, freeScrubUnlocked, freeScrubCode } = this.state;
      const target = this.config.referralsForFree;
      let extra = '';
      if (freeScrubUnlocked) {
        extra = `\n\n🏆 FREE scrub unlocked!\nCode: ${freeScrubCode}`;
      }
      this.addBotMessage(
        formatMessage(
          `🩺 Your Rumeds Progress\n\nReferrals: ${referralCount} / ${target}\nRewards Earned: ₹${walletAmount}${extra}\n\n🎁 ${target} referrals unlock your FREE scrub\n\nYou're closer than you think 👀\n\n👉 Type 1 to share your code again`
        )
      );
    }

    recordReferralSuccess() {
      const target = this.config.referralsForFree;
      const amt = this.config.rewardAmount;
      this.state.referralCount += 1;
      this.state.walletAmount += amt;
      saveState(this.state);

      if (this.state.referralCount >= target && !this.state.freeScrubUnlocked) {
        this.state.freeScrubUnlocked = true;
        this.state.freeScrubCode = buildFreeScrubCode(this.state.userId);
        saveState(this.state);
        this.openChat();
        this.runFlow5();
        setTimeout(() => this.runFlow6(), 800);
        return;
      }

      this.openChat();
      this.runFlow5();
    }

    runFlow5() {
      const { referralCount, walletAmount } = this.state;
      const amt = this.config.rewardAmount;
      const target = this.config.referralsForFree;
      this.addBotMessage(
        formatMessage(
          `🎉 Success!\n\nYour referral just placed an order 🙌\n\n₹${amt} has been added to your wallet 💰\n\n🩺 Progress: ${referralCount} / ${target}\n\nKeep going — your FREE scrub is close.`
        )
      );
      if (walletAmount > 0) {
        /* wallet already updated */
      }
    }

    runFlow6() {
      const code = this.state.freeScrubCode || buildFreeScrubCode(this.state.userId);
      this.state.freeScrubCode = code;
      this.state.freeScrubUnlocked = true;
      saveState(this.state);
      this.addBotMessage(
        formatMessage(
          `🏆 You did it!\n\nYou've unlocked your FREE Rumeds Scrub 🎁\n\nUse this code at checkout:\n${code}\n\nKeep referring to unlock more rewards 👇\n\n👉 Type 1 to continue sharing`
        )
      );
    }

    runFlow7() {
      const remaining = this.config.referralsForFree - this.state.referralCount;
      this.state.lastReengageAt = Date.now();
      saveState(this.state);
      this.addBotMessage(
        formatMessage(
          `Long shift? We get it.\n\nYou're just ${remaining} referral${remaining === 1 ? '' : 's'} away from a FREE scrub 👀\n\nDon't miss it — share your code now:\n👉 Type 1`
        )
      );
    }

    runFlow8() {
      const shopLink = this.config.shopUrl.startsWith('http')
        ? this.config.shopUrl
        : `${window.location.origin}${this.config.shopUrl}`;
      this.addBotMessage(
        formatMessage(
          `👕 Explore Rumeds Scrubs\n\n✔️ Precision Stretch\n✔️ Breathable Fabric\n✔️ Wrinkle Resistant\n\nBuilt for long duty hours.\n\n👉 Shop now: ${shopLink}\n👉 Or type 1 to earn rewards`
        ),
        {
          actions: `<a href="${shopLink}" class="rumeds-chat__btn">Shop Scrubs</a>`,
        }
      );
    }
  }

  customElements.define('rumeds-referral-chat', RumedsReferralChat);

  window.RumedsReferral = {
    recordSuccess() {
      document.querySelector('rumeds-referral-chat')?.recordReferralSuccess?.();
    },
    getState() {
      return loadState();
    },
    open() {
      const el = document.querySelector('rumeds-referral-chat');
      el?.openChat(true);
    },
  };
})();
