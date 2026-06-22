import { useState, useEffect, useRef } from 'react'
import { supportApi } from '../api/supportApi'
import { useAuthCtx } from '../store/authStore'

const C = {
  saffron: '#FC8019', amber: '#FF9E2A', tomato: '#E25E1A',
  cream: '#FDF6EE',   warm: '#FFFFFF', charcoal: '#02060C',
  bark: '#02060C99',  mocha: '#02060CEB', sand: '#F0F0F5',
  sage: '#118C4F',    cardBg: '#FFFFFF', border: '#F0F0F5',
  muted: '#02060C99', bg: '#F0F0F5',
}
const font = "'Proxima Nova', 'Inter', system-ui, sans-serif"

export default function SupportCenter() {
  const { user } = useAuthCtx()
  const [activeView, setActiveView] = useState('home') // home, tickets, chat, faqs
  const [activeTicket, setActiveTicket] = useState(null)
  const [sendError, setSendError] = useState('')
  
  // Data
  const [faqs, setFaqs] = useState([])
  const [categories, setCategories] = useState([])
  const [tickets, setTickets] = useState([])
  const [refunds, setRefunds] = useState([])
  const [loading, setLoading] = useState(true)
  const [ticketLoading, setTicketLoading] = useState(false)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    setLoading(true)
    try {
      const [tRes, fRes, cRes, rRes] = await Promise.all([
        supportApi.getTickets(),
        supportApi.getFAQs(),
        supportApi.getFAQCategories(),
        supportApi.getRefunds()
      ])
      setTickets(tRes.data?.results || tRes.data || [])
      setFaqs(fRes.data?.results || fRes.data || [])
      setCategories(cRes.data?.results || cRes.data || [])
      setRefunds(rRes.data?.results || rRes.data || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  // Fetch full ticket detail (with messages) before entering chat
  const openTicketChat = async (ticket) => {
    setTicketLoading(true)
    try {
      const res = await supportApi.getTicket(ticket.id)
      setActiveTicket(res.data)
    } catch (e) {
      console.error('Failed to load ticket:', e)
      setActiveTicket(ticket) // fallback to list data
    } finally {
      setTicketLoading(false)
      setActiveView('chat')
    }
  }

  // Chat Logic — uses REST API (works with runserver)
  const [messages, setMessages] = useState([])
  const [inputMsg, setInputMsg] = useState('')
  const [sending, setSending] = useState(false)
  const chatEndRef = useRef(null)

  useEffect(() => {
    if (activeView === 'chat' && activeTicket) {
      // Load messages from the ticket object
      setMessages(activeTicket.messages || [])
    }
  }, [activeView, activeTicket])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = async () => {
    if (!inputMsg.trim() || !activeTicket || sending) return
    const msgText = inputMsg
    setInputMsg('')
    setSending(true)
    setSendError('')

    // Optimistically add the user message
    const tempId = 'temp-' + Date.now()
    setMessages(prev => [...prev, {
      id: tempId,
      sender_type: 'user',
      message: msgText,
      created_at: new Date().toISOString()
    }])

    try {
      const res = await supportApi.addTicketMessage(activeTicket.id, { message: msgText })
      // The response is the full updated ticket with all messages (including AI reply)
      const updatedTicket = res.data
      setActiveTicket(updatedTicket)
      setMessages(updatedTicket.messages || [])
    } catch (e) {
      console.error("Failed to send message:", e)
      // Remove the optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempId))
      setInputMsg(msgText) // Restore the text so user can retry
      const errMsg = e.response?.data?.detail || e.response?.data?.error || 'Failed to send. Please try again.'
      setSendError(errMsg)
      setTimeout(() => setSendError(''), 4000)
    } finally {
      setSending(false)
    }
  }

  // Create Ticket Logic
  const [creating, setCreating] = useState(false)
  const [newSubject, setNewSubject] = useState('')
  const [newCategory, setNewCategory] = useState('General Issue')
  const [newDesc, setNewDesc] = useState('')

  const handleCreateTicket = async () => {
    if (!newSubject.trim()) return
    setLoading(true)
    try {
      const res = await supportApi.createTicket({ 
        subject: newSubject, 
        issue_category: newCategory,
        issue_type: 'User Reported',
        description: newDesc || newSubject,
      })
      await loadDashboardData()
      setActiveTicket(res.data)
      setActiveView('chat')
      setCreating(false)
      setNewSubject('')
      setNewDesc('')
    } catch (e) {
      alert("Failed to create ticket")
    } finally {
      setLoading(false)
    }
  }

  // Renderers
  if (ticketLoading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', background: C.bg }}>
        <div style={{ textAlign: 'center', color: C.muted, fontFamily: font }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>🔄</div>
          <div style={{ fontSize: 13 }}>Loading conversation...</div>
        </div>
      </div>
    )
  }

  // Status config for header badge
  const statusConfig = {
    open:                  { label: 'OPEN',              bg: '#E8F5E9', color: '#2E7D32' },
    in_progress:           { label: 'IN PROGRESS',       bg: '#E3F2FD', color: '#1565C0' },
    escalated:             { label: 'ESCALATED — TEAM ASSIGNED', bg: '#FFEBEE', color: '#C62828' },
    waiting_for_customer:  { label: 'WAITING FOR YOUR INFO', bg: '#FFF8E1', color: '#E65100' },
    resolved:              { label: 'RESOLVED',          bg: '#E8F5E9', color: '#2E7D32' },
    closed:                { label: 'CLOSED',            bg: '#F5F5F5', color: '#757575' },
  }
  const sc = statusConfig[activeTicket?.status] || statusConfig.open

  if (activeView === 'chat' && activeTicket) {
    const isEscalated = activeTicket.status === 'escalated'
    const isWaiting   = activeTicket.status === 'waiting_for_customer'

    return (
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0, background: C.cardBg }}>
        {/* Header */}
        <div style={{ padding: '14px 16px', borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', gap: 12, background: C.cardBg }}>
          <button onClick={() => { setActiveView('tickets'); setActiveTicket(null) }} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer', flexShrink: 0 }}>←</button>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 15, fontWeight: 800, fontFamily: font, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{activeTicket.subject}</div>
            <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>Ticket #{activeTicket.ticket_number}</div>
          </div>
          <div style={{ flexShrink: 0, background: sc.bg, color: sc.color, fontSize: 10, fontWeight: 800, fontFamily: font, padding: '4px 10px', borderRadius: 99, whiteSpace: 'nowrap' }}>
            {sc.label}
          </div>
        </div>

        {/* Escalation Banner */}
        {isEscalated && (
          <div style={{ background: '#FFEBEE', borderBottom: '1px solid #FFCDD2', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 18 }}>🔴</span>
            <div>
              <div style={{ fontSize: 12, fontWeight: 800, color: '#C62828', fontFamily: font }}>Transferred to Our Team</div>
              <div style={{ fontSize: 11, color: '#B71C1C', fontFamily: font }}>Our team will reach you shortly, please wait.</div>
            </div>
          </div>
        )}

        {/* Waiting Banner */}
        {isWaiting && (
          <div style={{ background: '#FFF8E1', borderBottom: '1px solid #FFE0B2', padding: '10px 16px', display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 18 }}>⏳</span>
            <div>
              <div style={{ fontSize: 12, fontWeight: 800, color: '#E65100', fontFamily: font }}>Waiting for your response</div>
              <div style={{ fontSize: 11, color: '#BF360C', fontFamily: font }}>Please reply below so our AI can continue helping you.</div>
            </div>
          </div>
        )}


        {/* Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 16, background: '#F8F8F8' }}>
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', padding: 40, color: C.muted, fontFamily: font, fontSize: 13 }}>
              No messages yet. Type your question below and our AI will assist you instantly!
            </div>
          )}
          {messages.map(m => {
            // System/escalation notification style
            const isSystemMsg = m.sender_type === 'ai' && m.message.startsWith('🔴 ESCALATED')
            if (isSystemMsg) {
              return (
                <div key={m.id} style={{ marginBottom: 16 }}>
                  <div style={{ background: '#FFEBEE', border: '1px solid #FFCDD2', borderRadius: 14, padding: '14px 16px', textAlign: 'center' }}>
                    <div style={{ fontSize: 22, marginBottom: 6 }}>🔴</div>
                    <div style={{ fontSize: 13, fontWeight: 800, color: '#C62828', fontFamily: font, marginBottom: 4 }}>Transferred to Our Team</div>
                    <div style={{ fontSize: 12, color: '#B71C1C', fontFamily: font, lineHeight: 1.5 }}>
                      Your ticket has been flagged as high priority. Our team will reach you shortly, please wait.
                    </div>
                  </div>
                </div>
              )
            }
            return (
              <div key={m.id} style={{ display: 'flex', justifyContent: m.sender_type === 'user' ? 'flex-end' : 'flex-start', marginBottom: 12 }}>
                <div style={{
                  background: m.sender_type === 'user'
                    ? `linear-gradient(135deg,${C.saffron},${C.tomato})`
                    : m.sender_type === 'agent' ? '#F0FFF4' : C.cardBg,
                  color: m.sender_type === 'user' ? '#fff' : C.charcoal,
                  padding: '12px 16px', borderRadius: 16, maxWidth: '80%', fontSize: 14, fontFamily: font,
                  border: m.sender_type === 'user' ? 'none'
                    : m.sender_type === 'agent' ? '1px solid #A5D6A7'
                    : `1px solid ${C.border}`,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
                }}>
                  {m.sender_type === 'ai'    && <div style={{ fontSize: 11, fontWeight: 800, color: C.saffron, marginBottom: 4 }}>🤖 AI Assistant</div>}
                  {m.sender_type === 'agent' && <div style={{ fontSize: 11, fontWeight: 800, color: '#2E7D32', marginBottom: 4 }}>🎧 Our Team</div>}
                  <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.5 }}>{m.message}</div>
                </div>
              </div>
            )
          })}
          {sending && (
            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: 12 }}>
              <div style={{ background: C.cardBg, border: `1px solid ${C.border}`, padding: '12px 16px', borderRadius: 16, fontSize: 14, fontFamily: font, color: C.muted }}>
                <div style={{ fontSize: 11, fontWeight: 800, color: C.saffron, marginBottom: 4 }}>🤖 AI Assistant</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <div style={{ display: 'flex', gap: 4 }}>
                    {[0,1,2].map(i => (
                      <div key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: C.saffron, opacity: 0.6, animation: `bounce 1.2s ${i * 0.2}s infinite` }} />
                    ))}
                  </div>
                  <span style={{ fontSize: 12 }}>Analyzing your issue...</span>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        {activeTicket.status === 'closed' ? (
          <div style={{ flexShrink: 0, padding: 16, textAlign: 'center', color: C.muted, background: C.sand, fontSize: 13, fontFamily: font, borderTop: `1px solid ${C.border}` }}>
            🔒 This ticket is closed.
          </div>
        ) : activeTicket.status === 'escalated' ? (
          <div style={{ flexShrink: 0, padding: 16, background: '#FFEBEE', borderTop: '1px solid #FFCDD2' }}>
            <div style={{ textAlign: 'center', color: '#C62828', fontSize: 12, fontFamily: font, fontWeight: 700, marginBottom: 8 }}>
              🔴 Ticket escalated — our team will reach you shortly, please wait
            </div>
            <div style={{ display: 'flex', gap: 12 }}>
              <input
                type="text" value={inputMsg} onChange={e => setInputMsg(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder="You can still add more details..."
                style={{ flex: 1, padding: '12px 16px', borderRadius: 99, border: '1px solid #FFCDD2', background: '#FFF8F8', fontSize: 13, fontFamily: font, outline: 'none' }}
              />
              <button onClick={sendMessage} disabled={sending} style={{ background: '#C62828', color: '#fff', border: 'none', borderRadius: 99, padding: '0 20px', fontWeight: 800, cursor: sending ? 'wait' : 'pointer', fontFamily: font, opacity: sending ? 0.7 : 1, fontSize: 13 }}>
                {sending ? '...' : 'Send'}
              </button>
            </div>
          </div>
        ) : (
          <div style={{ flexShrink: 0 }}>
            {sendError && (
              <div style={{ background: '#FEF0F0', color: '#DC2626', fontSize: 12, fontFamily: font, padding: '8px 16px', borderTop: `1px solid #FECACA`, textAlign: 'center' }}>
                ⚠️ {sendError}
              </div>
            )}
            {activeTicket.status === 'waiting_for_customer' && (
              <div style={{ background: '#FFF8E1', borderTop: '1px solid #FFE0B2', padding: '8px 16px', textAlign: 'center' }}>
                <span style={{ fontSize: 12, color: '#E65100', fontFamily: font, fontWeight: 700 }}>⏳ Please provide the requested details to continue</span>
              </div>
            )}
            <div style={{ padding: 16, borderTop: `1px solid ${C.border}`, display: 'flex', gap: 12, background: C.cardBg }}>
              <input
                type="text" value={inputMsg} onChange={e => setInputMsg(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder={activeTicket.status === 'waiting_for_customer' ? 'Provide the requested details...' : 'Type your message...'}
                style={{ flex: 1, padding: '14px 20px', borderRadius: 99, border: `1px solid ${C.border}`, background: C.bg, fontSize: 14, fontFamily: font, outline: 'none' }}
              />
              <button onClick={sendMessage} disabled={sending} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', border: 'none', borderRadius: 99, padding: '0 24px', fontWeight: 800, cursor: sending ? 'wait' : 'pointer', fontFamily: font, opacity: sending ? 0.7 : 1 }}>
                {sending ? '...' : 'Send'}
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }

  if (creating) {
    return (
      <div style={{ padding: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 24 }}>
          <button onClick={() => setCreating(false)} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer' }}>←</button>
          <div style={{ fontSize: 18, fontWeight: 800, fontFamily: font }}>Create New Ticket</div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label style={{ fontSize: 13, fontWeight: 700, color: C.muted, fontFamily: font }}>Issue Category</label>
            <select value={newCategory} onChange={e => setNewCategory(e.target.value)} style={{ width: '100%', padding: 14, borderRadius: 12, border: `1px solid ${C.border}`, marginTop: 6, fontSize: 14, fontFamily: font }}>
              <option>Order Issue</option>
              <option>Delivery Issue</option>
              <option>Payment Issue</option>
              <option>Refund Request</option>
              <option>General Issue</option>
            </select>
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 700, color: C.muted, fontFamily: font }}>Subject</label>
            <input type="text" value={newSubject} onChange={e => setNewSubject(e.target.value)} placeholder="E.g. Missing items in my order" style={{ width: '100%', padding: 14, borderRadius: 12, border: `1px solid ${C.border}`, marginTop: 6, fontSize: 14, fontFamily: font }} />
          </div>
          <div>
            <label style={{ fontSize: 13, fontWeight: 700, color: C.muted, fontFamily: font }}>Description (Optional)</label>
            <textarea value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Provide more details..." rows={4} style={{ width: '100%', padding: 14, borderRadius: 12, border: `1px solid ${C.border}`, marginTop: 6, fontSize: 14, fontFamily: font, resize: 'none' }} />
          </div>
          <button onClick={handleCreateTicket} disabled={loading} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', border: 'none', borderRadius: 12, padding: 16, fontWeight: 800, fontSize: 16, cursor: 'pointer', fontFamily: font, marginTop: 8 }}>
            {loading ? 'Submitting...' : 'Submit Ticket'}
          </button>
        </div>
      </div>
    )
  }

  if (activeView === 'tickets') {
    return (
      <div style={{ padding: 20 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button onClick={() => setActiveView('home')} style={{ background: 'none', border: 'none', fontSize: 20, cursor: 'pointer' }}>←</button>
            <div style={{ fontSize: 18, fontWeight: 800, fontFamily: font }}>My Tickets</div>
          </div>
          <button onClick={() => setCreating(true)} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', border: 'none', borderRadius: 8, padding: '6px 14px', fontSize: 13, fontWeight: 800, cursor: 'pointer', fontFamily: font }}>+ New Ticket</button>
        </div>

        {tickets.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40, color: C.muted, fontFamily: font }}>No tickets found.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {tickets.map(t => {
              const tsc = {
                open:                 { bg: '#E8F5E9', color: '#2E7D32', label: 'Open' },
                in_progress:          { bg: '#E3F2FD', color: '#1565C0', label: 'In Progress' },
                escalated:            { bg: '#FFEBEE', color: '#C62828', label: '🔴 Escalated' },
                waiting_for_customer: { bg: '#FFF8E1', color: '#E65100', label: '⏳ Waiting' },
                resolved:             { bg: '#E8F5E9', color: '#388E3C', label: 'Resolved' },
                closed:               { bg: '#F5F5F5', color: '#757575', label: 'Closed' },
              }[t.status] || { bg: C.sand, color: C.muted, label: t.status }

              return (
                <div key={t.id} onClick={() => openTicketChat(t)} style={{ background: C.cardBg, border: `1px solid ${t.status === 'escalated' ? '#FFCDD2' : t.status === 'waiting_for_customer' ? '#FFE0B2' : C.border}`, borderRadius: 16, padding: 16, cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 15, fontWeight: 800, color: C.charcoal, fontFamily: font, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{t.subject}</div>
                    <div style={{ fontSize: 12, color: C.muted, marginTop: 4 }}>{t.ticket_number} • {new Date(t.created_at).toLocaleDateString()}</div>
                  </div>
                  <div style={{ flexShrink: 0, marginLeft: 12, fontSize: 11, fontWeight: 800, padding: '4px 10px', borderRadius: 99, background: tsc.bg, color: tsc.color, whiteSpace: 'nowrap' }}>
                    {tsc.label}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    )
  }

  return (
    <div style={{ padding: 20, background: C.bg, minHeight: '100%' }}>
      <div style={{ fontSize: 24, fontWeight: 900, fontFamily: font, color: C.charcoal, marginBottom: 8 }}>Help Center</div>
      <div style={{ fontSize: 14, color: C.muted, fontFamily: font, marginBottom: 24 }}>How can we help you today?</div>

      {/* Quick Actions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 24 }}>
        <div onClick={() => setCreating(true)} style={{ background: `linear-gradient(135deg,${C.saffron},${C.tomato})`, color: '#fff', padding: 20, borderRadius: 16, cursor: 'pointer', boxShadow: '0 4px 12px rgba(252,128,25,0.2)' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>💬</div>
          <div style={{ fontSize: 15, fontWeight: 800, fontFamily: font }}>Chat with AI</div>
          <div style={{ fontSize: 12, opacity: 0.9 }}>Instant Support</div>
        </div>
        <div onClick={() => setActiveView('tickets')} style={{ background: C.cardBg, border: `1px solid ${C.border}`, padding: 20, borderRadius: 16, cursor: 'pointer' }}>
          <div style={{ fontSize: 24, marginBottom: 8 }}>🎫</div>
          <div style={{ fontSize: 15, fontWeight: 800, fontFamily: font, color: C.charcoal }}>My Tickets</div>
          <div style={{ fontSize: 12, color: C.muted }}>Track your issues</div>
        </div>
      </div>

      {/* Refunds Tracking */}
      {refunds.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ fontSize: 16, fontWeight: 800, fontFamily: font, marginBottom: 12 }}>Recent Refunds</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {refunds.slice(0, 3).map(r => (
              <div key={r.id} style={{ background: C.cardBg, border: `1px solid ${C.border}`, borderRadius: 12, padding: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 800, color: C.charcoal, fontFamily: font }}>₹{r.amount} - {r.refund_type}</div>
                  <div style={{ fontSize: 12, color: C.muted, marginTop: 4 }}>{r.reason.replace('_', ' ')}</div>
                </div>
                <div style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase', color: r.status === 'completed' ? C.sage : C.amber }}>
                  {r.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* FAQs */}
      <div style={{ fontSize: 16, fontWeight: 800, fontFamily: font, marginBottom: 12 }}>Frequently Asked Questions</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {faqs.length === 0 ? (
          <div style={{ fontSize: 13, color: C.muted, fontFamily: font }}>No FAQs available right now.</div>
        ) : (
          faqs.map(faq => (
            <details key={faq.id} style={{ background: C.cardBg, border: `1px solid ${C.border}`, borderRadius: 12, overflow: 'hidden' }}>
              <summary style={{ padding: 16, fontSize: 14, fontWeight: 700, fontFamily: font, color: C.charcoal, cursor: 'pointer', listStyle: 'none', display: 'flex', justifyContent: 'space-between' }}>
                {faq.question}
                <span>+</span>
              </summary>
              <div style={{ padding: '0 16px 16px', fontSize: 13, color: C.muted, fontFamily: font, lineHeight: 1.5 }}>
                {faq.answer}
              </div>
            </details>
          ))
        )}
      </div>
    </div>
  )
}
