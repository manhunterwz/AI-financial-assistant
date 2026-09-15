import React, { useState, useEffect, useRef } from 'react';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  LineChart, Line, XAxis, YAxis, CartesianGrid,
} from 'recharts';
import {
  Wallet, TrendingUp, TrendingDown, Plus, Trash2, Sparkles, Send,
  LayoutDashboard, Receipt, Bot, Loader2, AlertCircle,
} from 'lucide-react';

// ---------- design tokens ----------
const COLORS_TOKENS = {
  ink: '#12231D',
  paper: '#F5F6F1',
  card: '#FFFFFF',
  primary: '#1F6F54',
  primaryDark: '#164F3D',
  accent: '#E8A33D',
  negative: '#C1443C',
  muted: '#6F776B',
  border: '#DDE1D8',
};

const CATEGORIES = ['Food', 'Transport', 'Shopping', 'Bills & Utilities', 'Entertainment', 'Health', 'Education', 'Other'];

const CATEGORY_COLORS = {
  Food: '#1F6F54',
  Transport: '#E8A33D',
  Shopping: '#8B6F9E',
  'Bills & Utilities': '#3B7A9E',
  Entertainment: '#C1443C',
  Health: '#4A9B7F',
  Education: '#B0862E',
  Other: '#8A9086',
};

// keyword table mirrors the features the Python TF-IDF/Naive-Bayes model
// learned from data - this client-side version trades a little accuracy
// for zero network latency during the live demo.
const CATEGORY_KEYWORDS = {
  Food: ['swiggy', 'zomato', 'pizza', 'food', 'lunch', 'dinner', 'canteen', 'restaurant', 'cafe', 'coffee', 'snack', 'grocery', 'biryani', 'bakery', 'milk', 'chai', 'starbucks'],
  Transport: ['uber', 'ola', 'cab', 'auto', 'petrol', 'fuel', 'metro', 'bus', 'train', 'rapido', 'parking', 'flight', 'airport'],
  Shopping: ['amazon', 'flipkart', 'myntra', 'shoes', 'clothes', 'shopping', 'cover', 'decathlon', 'gift', 'electronics'],
  'Bills & Utilities': ['electricity', 'recharge', 'wifi', 'bill', 'dth', 'water', 'gas', 'maintenance', 'laundry', 'broadband'],
  Entertainment: ['netflix', 'spotify', 'movie', 'pvr', 'prime', 'game', 'steam', 'concert', 'youtube', 'hotstar', 'bowling'],
  Health: ['pharmacy', 'medicine', 'doctor', 'hospital', 'gym', 'protein', 'dental', 'insurance', 'lab', 'clinic'],
  Education: ['college', 'course', 'udemy', 'textbook', 'coaching', 'printing', 'xerox', 'exam', 'coursera', 'library', 'fees', 'tuition'],
};

function guessCategory(description) {
  const text = description.toLowerCase();
  for (const cat of CATEGORIES) {
    const keywords = CATEGORY_KEYWORDS[cat];
    if (keywords && keywords.some((k) => text.includes(k))) return cat;
  }
  return 'Other';
}

function formatINR(amount) {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount || 0);
}

function makeId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

// simple least-squares trend, one point ahead - the JS mirror of the
// LinearRegression forecaster in the Python backend.
function linearForecast(points) {
  const n = points.length;
  if (n === 0) return 0;
  if (n === 1) return points[0].value;
  const xs = points.map((_, i) => i);
  const ys = points.map((p) => p.value);
  const xMean = xs.reduce((a, b) => a + b, 0) / n;
  const yMean = ys.reduce((a, b) => a + b, 0) / n;
  let num = 0, den = 0;
  for (let i = 0; i < n; i++) {
    num += (xs[i] - xMean) * (ys[i] - yMean);
    den += (xs[i] - xMean) ** 2;
  }
  const slope = den === 0 ? 0 : num / den;
  const intercept = yMean - slope * xMean;
  return Math.max(0, slope * n + intercept);
}

async function callClaude(messages, system) {
  const res = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: 'claude-sonnet-4-6', max_tokens: 1000, system, messages }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = await res.json();
  const block = (data.content || []).find((b) => b.type === 'text');
  return block ? block.text : '';
}

export default function AIFinancialAssistant() {
  const [ready, setReady] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [budgets, setBudgets] = useState({});
  const [tab, setTab] = useState('dashboard');

  const [form, setForm] = useState({ type: 'expense', amount: '', description: '', category: '', date: new Date().toISOString().slice(0, 10) });
  const [budgetForm, setBudgetForm] = useState({ category: CATEGORIES[0], limit: '' });

  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    (async () => {
      try {
        const result = await window.storage.get('financial-data', false);
        if (result && result.value) {
          const parsed = JSON.parse(result.value);
          setTransactions(parsed.transactions || []);
          setBudgets(parsed.budgets || {});
        }
      } catch (e) {
        // nothing saved yet - start fresh
      } finally {
        setReady(true);
      }
    })();
  }, []);

  async function persist(nextTx, nextBudgets) {
    try {
      await window.storage.set('financial-data', JSON.stringify({ transactions: nextTx, budgets: nextBudgets }), false);
    } catch (e) {
      // best-effort persistence; app keeps working in-memory either way
    }
  }

  useEffect(() => {
    if (chatEndRef.current) chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, chatLoading]);

  function addTransaction(e) {
    e.preventDefault();
    const amount = parseFloat(form.amount);
    if (!amount || amount <= 0 || !form.description.trim()) return;
    const category = form.type === 'income' ? 'Income' : (form.category || guessCategory(form.description));
    const tx = {
      id: makeId(),
      type: form.type,
      amount,
      description: form.description.trim(),
      category,
      date: form.date,
    };
    const next = [tx, ...transactions];
    setTransactions(next);
    persist(next, budgets);
    setForm({ type: 'expense', amount: '', description: '', category: '', date: new Date().toISOString().slice(0, 10) });
  }

  function deleteTransaction(id) {
    const next = transactions.filter((t) => t.id !== id);
    setTransactions(next);
    persist(next, budgets);
  }

  function setBudget(e) {
    e.preventDefault();
    const limit = parseFloat(budgetForm.limit);
    if (!limit || limit <= 0) return;
    const next = { ...budgets, [budgetForm.category]: limit };
    setBudgets(next);
    persist(transactions, next);
    setBudgetForm({ category: CATEGORIES[0], limit: '' });
  }

  // ---------- derived data ----------
  const totalIncome = transactions.filter((t) => t.type === 'income').reduce((s, t) => s + t.amount, 0);
  const totalExpense = transactions.filter((t) => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
  const balance = totalIncome - totalExpense;

  const byCategory = {};
  transactions.filter((t) => t.type === 'expense').forEach((t) => {
    byCategory[t.category] = (byCategory[t.category] || 0) + t.amount;
  });
  const pieData = Object.entries(byCategory).map(([name, value]) => ({ name, value }));

  const monthlyMap = {};
  transactions.filter((t) => t.type === 'expense').forEach((t) => {
    const m = t.date.slice(0, 7);
    monthlyMap[m] = (monthlyMap[m] || 0) + t.amount;
  });
  const monthly = Object.entries(monthlyMap).sort(([a], [b]) => a.localeCompare(b)).map(([label, value]) => ({ label, value }));
  const forecastValue = linearForecast(monthly);
  const forecastChartData = [
    ...monthly.map((m) => ({ label: m.label, actual: m.value, forecast: null })),
    ...(monthly.length > 0 ? [{ label: 'Next', actual: null, forecast: forecastValue, prevActual: monthly[monthly.length - 1].value }] : []),
  ];

  function buildSummary() {
    return {
      totalIncome, totalExpense, balance,
      spendingByCategory: byCategory,
      budgets,
      monthlyTotals: Object.fromEntries(monthly.map((m) => [m.label, Math.round(m.value)])),
      forecastNextMonth: Math.round(forecastValue),
      recentTransactions: transactions.slice(0, 15).map((t) => ({ date: t.date, type: t.type, amount: t.amount, category: t.category, description: t.description })),
    };
  }

  async function sendChat() {
    const text = chatInput.trim();
    if (!text || chatLoading) return;
    const next = [...chatMessages, { role: 'user', content: text }];
    setChatMessages(next);
    setChatInput('');
    setChatLoading(true);
    try {
      const system = `You are a friendly, encouraging personal finance assistant embedded inside a student's budgeting app. Ground every answer in the real numbers given below - never invent transactions or amounts that aren't there. Keep answers concise (roughly 3-5 sentences) unless the user asks for more detail. Currency is Indian Rupees. Financial summary as JSON: ${JSON.stringify(buildSummary())}`;
      const apiMessages = next.map((m) => ({ role: m.role, content: m.content }));
      const reply = await callClaude(apiMessages, system);
      setChatMessages((prev) => [...prev, { role: 'assistant', content: reply || "I couldn't come up with a response - try rephrasing?" }]);
    } catch (e) {
      setChatMessages((prev) => [...prev, { role: 'assistant', content: "I couldn't reach the AI service just now. Please try again in a moment." }]);
    } finally {
      setChatLoading(false);
    }
  }

  const suggestedPrompts = [
    'How much did I spend this month?',
    'Where can I cut back?',
    'Am I within my budgets?',
    'Give me 3 saving tips based on my spending',
  ];

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'transactions', label: 'Transactions', icon: Receipt },
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'assistant', label: 'Assistant', icon: Bot },
  ];

  if (!ready) {
    return (
      <div style={{ background: COLORS_TOKENS.paper, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Loader2 className="animate-spin" size={28} color={COLORS_TOKENS.primary} />
      </div>
    );
  }

  return (
    <div style={{ background: COLORS_TOKENS.paper, minHeight: '100vh', fontFamily: "'IBM Plex Sans', sans-serif", color: COLORS_TOKENS.ink }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
        .fin-serif { font-family: 'Fraunces', serif; }
        .fin-scroll::-webkit-scrollbar { width: 6px; }
        .fin-scroll::-webkit-scrollbar-thumb { background: ${COLORS_TOKENS.border}; border-radius: 4px; }
        input, select, button { font-family: inherit; }
        .fin-input:focus, .fin-select:focus { outline: 2px solid ${COLORS_TOKENS.primary}; outline-offset: 1px; }
      `}</style>

      <div className="max-w-4xl mx-auto px-5 py-8">
        {/* header */}
        <div className="flex items-end justify-between mb-6 flex-wrap gap-2">
          <div>
            <h1 className="fin-serif" style={{ fontSize: '28px', fontWeight: 600, letterSpacing: '-0.01em', margin: 0 }}>
              AI Financial Assistant
            </h1>
            <p style={{ color: COLORS_TOKENS.muted, fontSize: '14px', marginTop: '4px' }}>
              Track spending, forecast trends, and ask for advice.
            </p>
          </div>
        </div>

        {/* tab nav - underline style */}
        <div className="flex gap-1 mb-6" style={{ borderBottom: `1px solid ${COLORS_TOKENS.border}` }}>
          {tabs.map((t) => {
            const Icon = t.icon;
            const active = tab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className="flex items-center gap-1.5 px-3 py-2.5 transition-all duration-200"
                style={{
                  background: 'transparent',
                  border: 'none',
                  borderBottom: active ? `2px solid ${COLORS_TOKENS.primary}` : '2px solid transparent',
                  marginBottom: '-1px',
                  color: active ? COLORS_TOKENS.primary : COLORS_TOKENS.muted,
                  fontWeight: active ? 600 : 500,
                  fontSize: '14px',
                  cursor: 'pointer',
                }}
              >
                <Icon size={16} />
                {t.label}
              </button>
            );
          })}
        </div>

        {tab === 'dashboard' && (
          <DashboardTab
            totalIncome={totalIncome} totalExpense={totalExpense} balance={balance}
            pieData={pieData} byCategory={byCategory} budgets={budgets}
            transactions={transactions} budgetForm={budgetForm} setBudgetForm={setBudgetForm} setBudget={setBudget}
          />
        )}

        {tab === 'transactions' && (
          <TransactionsTab
            form={form} setForm={setForm} addTransaction={addTransaction}
            transactions={transactions} deleteTransaction={deleteTransaction}
          />
        )}

        {tab === 'forecast' && (
          <ForecastTab monthly={monthly} forecastValue={forecastValue} forecastChartData={forecastChartData} byCategory={byCategory} />
        )}

        {tab === 'assistant' && (
          <AssistantTab
            chatMessages={chatMessages} chatInput={chatInput} setChatInput={setChatInput}
            chatLoading={chatLoading} sendChat={sendChat} suggestedPrompts={suggestedPrompts}
            chatEndRef={chatEndRef} hasData={transactions.length > 0}
          />
        )}
      </div>
    </div>
  );
}

// ---------- Dashboard ----------
function DashboardTab({ totalIncome, totalExpense, balance, pieData, byCategory, budgets, transactions, budgetForm, setBudgetForm, setBudget }) {
  return (
    <div>
      {/* hero balance + stat chips */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div style={{ background: COLORS_TOKENS.card, border: `1px solid ${COLORS_TOKENS.border}`, borderRadius: '10px', padding: '20px 24px', minWidth: '220px', flex: '1 1 220px' }}>
          <div className="flex items-center gap-2" style={{ color: COLORS_TOKENS.muted, fontSize: '13px' }}>
            <Wallet size={15} /> Balance
          </div>
          <div className="fin-serif" style={{ fontSize: '34px', fontWeight: 600, marginTop: '6px', color: balance >= 0 ? COLORS_TOKENS.primary : COLORS_TOKENS.negative }}>
            {formatINR(balance)}
          </div>
        </div>
        <div style={{ border: `1px solid ${COLORS_TOKENS.border}`, borderRadius: '10px', padding: '20px 24px', minWidth: '160px', flex: '1 1 160px' }}>
          <div className="flex items-center gap-2" style={{ color: COLORS_TOKENS.muted, fontSize: '13px' }}>
            <TrendingUp size={15} /> Income
          </div>
          <div className="fin-serif" style={{ fontSize: '22px', fontWeight: 600, marginTop: '6px' }}>{formatINR(totalIncome)}</div>
        </div>
        <div style={{ border: `1px solid ${COLORS_TOKENS.border}`, borderRadius: '10px', padding: '20px 24px', minWidth: '160px', flex: '1 1 160px' }}>
          <div className="flex items-center gap-2" style={{ color: COLORS_TOKENS.muted, fontSize: '13px' }}>
            <TrendingDown size={15} /> Expenses
          </div>
          <div className="fin-serif" style={{ fontSize: '22px', fontWeight: 600, marginTop: '6px' }}>{formatINR(totalExpense)}</div>
        </div>
      </div>

      {transactions.length === 0 ? (
        <EmptyState text="No transactions yet. Add your first one in the Transactions tab." />
      ) : (
        <div className="flex flex-wrap gap-6 mb-6">
          <div style={{ flex: '1 1 280px', minWidth: '260px' }}>
            <SectionLabel>Spending by category</SectionLabel>
            <div style={{ height: '240px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" innerRadius={50} outerRadius={85} paddingAngle={2}>
                    {pieData.map((entry, i) => <Cell key={i} fill={CATEGORY_COLORS[entry.name] || COLORS_TOKENS.muted} />)}
                  </Pie>
                  <Tooltip formatter={(v) => formatINR(v)} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ flex: '1 1 280px', minWidth: '260px' }}>
            <SectionLabel>Recent transactions</SectionLabel>
            <div className="fin-scroll" style={{ maxHeight: '240px', overflowY: 'auto' }}>
              {transactions.slice(0, 6).map((t) => <TxRow key={t.id} t={t} compact />)}
            </div>
          </div>
        </div>
      )}

      {/* budgets */}
      <SectionLabel>Budgets</SectionLabel>
      <div className="mb-3">
        {Object.keys(budgets).length === 0 ? (
          <p style={{ color: COLORS_TOKENS.muted, fontSize: '14px', marginTop: '4px' }}>Set a monthly limit per category to track progress here.</p>
        ) : (
          Object.entries(budgets).map(([cat, limit]) => {
            const spent = byCategory[cat] || 0;
            const pct = Math.min(100, (spent / limit) * 100);
            const over = spent > limit;
            return (
              <div key={cat} style={{ marginBottom: '12px' }}>
                <div className="flex justify-between" style={{ fontSize: '13px', marginBottom: '4px' }}>
                  <span>{cat}</span>
                  <span style={{ color: over ? COLORS_TOKENS.negative : COLORS_TOKENS.muted }}>{formatINR(spent)} / {formatINR(limit)}</span>
                </div>
                <div style={{ height: '6px', background: COLORS_TOKENS.border, borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${pct}%`, height: '100%', background: over ? COLORS_TOKENS.negative : (pct > 80 ? COLORS_TOKENS.accent : COLORS_TOKENS.primary), transition: 'width 0.3s ease' }} />
                </div>
              </div>
            );
          })
        )}
      </div>
      <form onSubmit={setBudget} className="flex gap-2 flex-wrap items-end">
        <div>
          <label style={{ fontSize: '12px', color: COLORS_TOKENS.muted }}>Category</label>
          <select className="fin-select" value={budgetForm.category} onChange={(e) => setBudgetForm({ ...budgetForm, category: e.target.value })}
            style={{ display: 'block', padding: '7px 10px', borderRadius: '6px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13px' }}>
            {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: '12px', color: COLORS_TOKENS.muted }}>Monthly limit (Rs)</label>
          <input className="fin-input" type="number" min="1" placeholder="5000" value={budgetForm.limit}
            onChange={(e) => setBudgetForm({ ...budgetForm, limit: e.target.value })}
            style={{ display: 'block', padding: '7px 10px', borderRadius: '6px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13px', width: '120px' }} />
        </div>
        <button type="submit" style={{ background: COLORS_TOKENS.primary, color: '#fff', border: 'none', borderRadius: '6px', padding: '8px 14px', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}>
          Set budget
        </button>
      </form>
    </div>
  );
}

// ---------- Transactions ----------
function TransactionsTab({ form, setForm, addTransaction, transactions, deleteTransaction }) {
  return (
    <div>
      <SectionLabel>Add a transaction</SectionLabel>
      <form onSubmit={addTransaction} className="flex flex-wrap gap-2 items-end mb-6" style={{ background: COLORS_TOKENS.card, border: `1px solid ${COLORS_TOKENS.border}`, borderRadius: '10px', padding: '16px' }}>
        <div className="flex gap-1">
          {['expense', 'income'].map((ty) => (
            <button key={ty} type="button" onClick={() => setForm({ ...form, type: ty, category: '' })}
              style={{
                padding: '7px 12px', borderRadius: '6px', fontSize: '13px', fontWeight: 600, cursor: 'pointer',
                border: `1px solid ${form.type === ty ? COLORS_TOKENS.primary : COLORS_TOKENS.border}`,
                background: form.type === ty ? COLORS_TOKENS.primary : 'transparent',
                color: form.type === ty ? '#fff' : COLORS_TOKENS.ink,
              }}>
              {ty === 'expense' ? 'Expense' : 'Income'}
            </button>
          ))}
        </div>
        <div>
          <label style={{ fontSize: '12px', color: COLORS_TOKENS.muted }}>Amount (Rs)</label>
          <input className="fin-input" type="number" min="1" step="0.01" required value={form.amount}
            onChange={(e) => setForm({ ...form, amount: e.target.value })}
            style={{ display: 'block', padding: '7px 10px', borderRadius: '6px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13px', width: '110px' }} />
        </div>
        <div style={{ flex: '1 1 180px' }}>
          <label style={{ fontSize: '12px', color: COLORS_TOKENS.muted }}>Description</label>
          <input className="fin-input" type="text" required placeholder="e.g. Swiggy order" value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            style={{ display: 'block', width: '100%', padding: '7px 10px', borderRadius: '6px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13px' }} />
        </div>
        {form.type === 'expense' && (
          <div>
            <label style={{ fontSize: '12px', color: COLORS_TOKENS.muted }}>Category</label>
            <div className="flex gap-1">
              <select className="fin-select" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
                style={{ padding: '7px 10px', borderRadius: '6px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13px' }}>
                <option value="">Auto</option>
                {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
              <button type="button" title="Guess category from description"
                onClick={() => setForm({ ...form, category: guessCategory(form.description || '') })}
                style={{ border: `1px solid ${COLORS_TOKENS.accent}`, background: 'transparent', color: COLORS_TOKENS.accent, borderRadius: '6px', padding: '0 10px', cursor: 'pointer' }}>
                <Sparkles size={14} />
              </button>
            </div>
          </div>
        )}
        <div>
          <label style={{ fontSize: '12px', color: COLORS_TOKENS.muted }}>Date</label>
          <input className="fin-input" type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })}
            style={{ display: 'block', padding: '6px 10px', borderRadius: '6px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13px' }} />
        </div>
        <button type="submit" style={{ background: COLORS_TOKENS.primary, color: '#fff', border: 'none', borderRadius: '6px', padding: '8px 16px', fontSize: '13px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}>
          <Plus size={15} /> Add
        </button>
      </form>

      <SectionLabel>All transactions ({transactions.length})</SectionLabel>
      {transactions.length === 0 ? (
        <EmptyState text="Nothing added yet - use the form above." />
      ) : (
        <div>{transactions.map((t) => <TxRow key={t.id} t={t} onDelete={() => deleteTransaction(t.id)} />)}</div>
      )}
    </div>
  );
}

function TxRow({ t, onDelete, compact }) {
  const isIncome = t.type === 'income';
  return (
    <div className="flex items-center justify-between" style={{ padding: compact ? '8px 0' : '10px 2px', borderBottom: `1px solid ${COLORS_TOKENS.border}` }}>
      <div className="flex items-center gap-2.5" style={{ minWidth: 0 }}>
        <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: isIncome ? COLORS_TOKENS.primary : (CATEGORY_COLORS[t.category] || COLORS_TOKENS.muted), flexShrink: 0 }} />
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: '13.5px', fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.description}</div>
          <div style={{ fontSize: '11.5px', color: COLORS_TOKENS.muted }}>{t.category} · {t.date}</div>
        </div>
      </div>
      <div className="flex items-center gap-3" style={{ flexShrink: 0 }}>
        <span style={{ fontSize: '14px', fontWeight: 600, color: isIncome ? COLORS_TOKENS.primary : COLORS_TOKENS.ink }}>
          {isIncome ? '+' : '-'}{formatINR(t.amount)}
        </span>
        {onDelete && (
          <button onClick={onDelete} style={{ background: 'none', border: 'none', cursor: 'pointer', color: COLORS_TOKENS.muted, padding: '4px' }} title="Delete">
            <Trash2 size={14} />
          </button>
        )}
      </div>
    </div>
  );
}

// ---------- Forecast ----------
function ForecastTab({ monthly, forecastValue, forecastChartData, byCategory }) {
  if (monthly.length === 0) {
    return <EmptyState text="Add a few transactions across different dates to see a forecast." />;
  }
  return (
    <div>
      <SectionLabel>Monthly spend trend & next-month forecast</SectionLabel>
      <div style={{ background: COLORS_TOKENS.card, border: `1px solid ${COLORS_TOKENS.border}`, borderRadius: '10px', padding: '16px', marginBottom: '20px' }}>
        <div style={{ height: '260px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={forecastChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke={COLORS_TOKENS.border} />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
              <Tooltip formatter={(v) => (v == null ? '-' : formatINR(v))} />
              <Line type="monotone" dataKey="actual" stroke={COLORS_TOKENS.primary} strokeWidth={2.5} dot={{ r: 3 }} connectNulls={false} name="Actual" />
              <Line type="monotone" dataKey="forecast" stroke={COLORS_TOKENS.accent} strokeWidth={2.5} strokeDasharray="5 5" dot={{ r: 4 }} name="Forecast" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p style={{ marginTop: '10px', fontSize: '13px', color: COLORS_TOKENS.muted }}>
          Projected next month: <strong style={{ color: COLORS_TOKENS.ink }}>{formatINR(forecastValue)}</strong> (straight-line trend fit on {monthly.length} month{monthly.length === 1 ? '' : 's'} of history)
        </p>
      </div>

      <SectionLabel>Where the forecast comes from</SectionLabel>
      <p style={{ fontSize: '13.5px', color: COLORS_TOKENS.muted, lineHeight: 1.6, maxWidth: '560px' }}>
        This chart fits a least-squares line through your monthly totals and projects one step ahead - the same
        approach as the <code style={{ background: COLORS_TOKENS.border, padding: '1px 5px', borderRadius: '4px' }}>forecaster.py</code> module
        in the Python backend. With more months of real history, that Python version is the one to trust for the report; this in-app
        version exists so the trend updates live as you add transactions.
      </p>
    </div>
  );
}

// ---------- AI Assistant ----------
function AssistantTab({ chatMessages, chatInput, setChatInput, chatLoading, sendChat, suggestedPrompts, chatEndRef, hasData }) {
  return (
    <div>
      <div style={{ background: COLORS_TOKENS.card, border: `1px solid ${COLORS_TOKENS.border}`, borderRadius: '10px', display: 'flex', flexDirection: 'column', height: '460px' }}>
        <div className="fin-scroll" style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
          {chatMessages.length === 0 && (
            <div>
              <div className="flex items-center gap-2" style={{ color: COLORS_TOKENS.muted, fontSize: '13px', marginBottom: '10px' }}>
                <Bot size={16} />
                {hasData ? 'Ask about your spending, budgets, or ways to save.' : 'Add a few transactions first, then ask me about them.'}
              </div>
              <div className="flex flex-wrap gap-2">
                {suggestedPrompts.map((p) => (
                  <button key={p} onClick={() => setChatInput(p)}
                    style={{ fontSize: '12.5px', padding: '6px 10px', borderRadius: '999px', border: `1px solid ${COLORS_TOKENS.border}`, background: 'transparent', cursor: 'pointer', color: COLORS_TOKENS.ink }}>
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}
          {chatMessages.map((m, i) => (
            <div key={i} className="flex" style={{ justifyContent: m.role === 'user' ? 'flex-end' : 'flex-start', marginBottom: '10px' }}>
              <div style={{
                maxWidth: '78%', padding: '9px 13px', borderRadius: '12px', fontSize: '13.5px', lineHeight: 1.5,
                background: m.role === 'user' ? COLORS_TOKENS.primary : COLORS_TOKENS.paper,
                color: m.role === 'user' ? '#fff' : COLORS_TOKENS.ink,
                border: m.role === 'user' ? 'none' : `1px solid ${COLORS_TOKENS.border}`,
                whiteSpace: 'pre-wrap',
              }}>
                {m.content}
              </div>
            </div>
          ))}
          {chatLoading && (
            <div className="flex items-center gap-2" style={{ color: COLORS_TOKENS.muted, fontSize: '13px' }}>
              <Loader2 className="animate-spin" size={14} /> Thinking…
            </div>
          )}
          <div ref={chatEndRef} />
        </div>
        <form
          onSubmit={(e) => { e.preventDefault(); sendChat(); }}
          className="flex gap-2"
          style={{ borderTop: `1px solid ${COLORS_TOKENS.border}`, padding: '10px' }}
        >
          <input
            className="fin-input"
            type="text"
            placeholder="Ask about your finances…"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            style={{ flex: 1, padding: '9px 12px', borderRadius: '8px', border: `1px solid ${COLORS_TOKENS.border}`, fontSize: '13.5px' }}
          />
          <button type="submit" disabled={chatLoading || !chatInput.trim()}
            style={{ background: COLORS_TOKENS.primary, color: '#fff', border: 'none', borderRadius: '8px', padding: '0 16px', cursor: 'pointer', opacity: chatLoading || !chatInput.trim() ? 0.5 : 1, display: 'flex', alignItems: 'center' }}>
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}

// ---------- shared bits ----------
function SectionLabel({ children }) {
  return <div className="fin-serif" style={{ fontSize: '15px', fontWeight: 600, marginBottom: '10px', color: COLORS_TOKENS.ink }}>{children}</div>;
}

function EmptyState({ text }) {
  return (
    <div className="flex items-center gap-2" style={{ color: COLORS_TOKENS.muted, fontSize: '13.5px', padding: '20px 0' }}>
      <AlertCircle size={15} /> {text}
    </div>
  );
}
