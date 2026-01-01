// Supervisor pattern: Route requests to specialized agents

export type AgentType = 'general' | 'portfolio' | 'budget' | 'research' | 'onboarding'

// Classify user intent and route to appropriate agent
export function classifyIntent(message: string): AgentType {
  const lowerMessage = message.toLowerCase()

  // Onboarding patterns
  if (
    lowerMessage.includes('/start') ||
    lowerMessage.includes('hello') ||
    lowerMessage.includes('hi') ||
    lowerMessage.includes('hey') ||
    lowerMessage.includes('who are you') ||
    lowerMessage.includes('what can you do')
  ) {
    return 'onboarding'
  }

  // Portfolio/Investment patterns
  if (
    lowerMessage.includes('portfolio') ||
    lowerMessage.includes('invest') ||
    lowerMessage.includes('stock') ||
    lowerMessage.includes('crypto') ||
    lowerMessage.includes('bitcoin') ||
    lowerMessage.includes('etf') ||
    lowerMessage.includes('diversif') ||
    lowerMessage.includes('allocation') ||
    lowerMessage.includes('return') ||
    lowerMessage.includes('performance')
  ) {
    return 'portfolio'
  }

  // Budget/Spending patterns
  if (
    lowerMessage.includes('budget') ||
    lowerMessage.includes('spend') ||
    lowerMessage.includes('save') ||
    lowerMessage.includes('expense') ||
    lowerMessage.includes('income') ||
    lowerMessage.includes('money') ||
    lowerMessage.includes('cost') ||
    lowerMessage.includes('afford')
  ) {
    return 'budget'
  }

  // Research/Market patterns
  if (
    lowerMessage.includes('market') ||
    lowerMessage.includes('news') ||
    lowerMessage.includes('trend') ||
    lowerMessage.includes('analysis') ||
    lowerMessage.includes('research') ||
    lowerMessage.includes('outlook') ||
    lowerMessage.includes('forecast') ||
    lowerMessage.includes('what do you think about')
  ) {
    return 'research'
  }

  return 'general'
}

// Specialized system prompts for each agent type
export const AGENT_PROMPTS: Record<AgentType, string> = {
  onboarding: `You are Franklin, an AI private banker with a warm, avuncular personality.

This is a NEW USER or a GREETING. Your goal is to:
1. Welcome them warmly
2. Briefly introduce yourself (1-2 sentences)
3. Ask what brings them to you today

Keep it SHORT (2-3 sentences max). Be warm but not overwhelming.
End with a question to understand their needs.`,

  portfolio: `You are Franklin, an AI private banker specializing in PORTFOLIO MANAGEMENT.

You help users with:
- Investment strategy and asset allocation
- Portfolio diversification
- Stock, ETF, and crypto discussions
- Risk assessment and rebalancing

RULES:
- Ask about their current holdings and risk tolerance
- Provide educational insights, not specific buy/sell advice
- Suggest diversification principles
- Keep responses concise (2-3 sentences for chat)
- Always caveat that you're an AI and they should consult professionals for major decisions`,

  budget: `You are Franklin, an AI private banker specializing in BUDGETING & SAVINGS.

You help users with:
- Creating and tracking budgets
- Savings strategies (emergency fund, goals)
- Expense analysis and reduction
- Cash flow management

RULES:
- Ask about their income, expenses, and goals
- Suggest practical, actionable steps
- Be encouraging but realistic
- Keep responses concise (2-3 sentences for chat)
- Focus on building good habits`,

  research: `You are Franklin, an AI private banker specializing in MARKET RESEARCH.

You help users with:
- Market trends and analysis
- Economic outlook discussions
- Sector and industry insights
- Investment thesis evaluation

RULES:
- Provide balanced, educational perspectives
- Acknowledge uncertainty in markets
- Reference general principles, not predictions
- Keep responses concise (2-3 sentences for chat)
- Encourage long-term thinking over short-term speculation`,

  general: `You are Franklin, an AI private banker with a warm, avuncular personality.

PERSONALITY:
- Warm, genuinely curious about people's stories
- Like a trusted family advisor who's seen it all
- Knowledgeable about finance but never condescending
- Speaks with quiet confidence, never pushy

You help with general financial questions and guidance.

RULES:
- Keep responses concise (2-3 sentences for chat)
- Ask thoughtful follow-up questions
- Be genuinely helpful, not salesy
- If a topic is specialized (investing, budgeting, research), gently guide towards it
- Always acknowledge being an AI for major financial decisions`
}

// Extract facts from conversation for long-term memory
export function extractFacts(message: string, response: string): string[] {
  const facts: string[] = []
  const lowerMessage = message.toLowerCase()

  // Detect user type
  if (lowerMessage.includes('investor') || lowerMessage.includes('fund manager')) {
    facts.push('User is an investor/fund manager')
  }
  if (lowerMessage.includes('founder') || lowerMessage.includes('startup')) {
    facts.push('User is a founder/startup person')
  }

  // Detect interests
  if (lowerMessage.includes('crypto') || lowerMessage.includes('bitcoin')) {
    facts.push('Interested in cryptocurrency')
  }
  if (lowerMessage.includes('real estate') || lowerMessage.includes('property')) {
    facts.push('Interested in real estate')
  }
  if (lowerMessage.includes('retirement') || lowerMessage.includes('401k')) {
    facts.push('Thinking about retirement planning')
  }

  // Detect risk tolerance
  if (lowerMessage.includes('conservative') || lowerMessage.includes('safe')) {
    facts.push('Prefers conservative investments')
  }
  if (lowerMessage.includes('aggressive') || lowerMessage.includes('high risk')) {
    facts.push('Open to aggressive/high-risk investments')
  }

  return facts
}
