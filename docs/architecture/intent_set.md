# SquareTrade Chat Agent - Intent Set

## Intent Categories

### 1. Product Information Intents
- **intent_plan_inquiry**: User asks about available plans
  - "What plans do you offer?"
  - "What types of coverage are available?"
  - "Tell me about your protection plans"
  - "What devices can I protect?"
  - "Do you cover smartphones?"

- **intent_plan_details**: User wants specific details about plans
  - "What's included in the plan?"
  - "Does it cover accidental damage?"
  - "What are the exclusions?"
  - "Is there a deductible?"
  - "What's the coverage limit?"

- **intent_pricing**: User asks about costs
  - "How much does it cost?"
  - "What's the monthly price?"
  - "Do you offer discounts?"
  - "How do I pay?"
  - "Are there different pricing tiers?"

### 2. Claims Intents
- **intent_file_claim**: User wants to file a claim
  - "How do I file a claim?"
  - "I need to file a claim"
  - "My device is damaged"
  - "I want to make a claim"
  - "How do I report damage?"

- **intent_claim_status**: User checks claim status
  - "Where's my claim?"
  - "What's the status of my claim?"
  - "How long does processing take?"
  - "Can I track my claim?"
  - "Is my claim approved?"

- **intent_device_replacement**: User asks about replacement
  - "Can I get a replacement?"
  - "Do you replace devices?"
  - "How does replacement work?"
  - "When will I get my replacement?"
  - "What condition is the replacement in?"

### 3. Support Intents
- **intent_contact_support**: User wants to contact support
  - "How do I contact support?"
  - "I need help"
  - "Can I speak to someone?"
  - "I want to talk to an agent"
  - "What's your phone number?"

- **intent_activation**: User wants to activate a plan
  - "How do I sign up?"
  - "How do I activate coverage?"
  - "How do I purchase a plan?"
  - "Can I get started today?"
  - "How do I enroll?"

- **intent_faq**: General questions
  - "Do you have FAQs?"
  - "Can you answer common questions?"
  - "What should I know?"
  - "Tell me more about your service"

- **intent_welcome**: User greets or asks for capabilities
  - "Hi"
  - "Hello"
  - "What can you help me with?"
  - "What do you do?"
  - "Tell me what you can do"
  - "How can you help?"
  - "What services do you offer?"

### 4. Escalation Intents
- **intent_escalation_urgent**: User needs urgent assistance
  - "I need immediate help"
  - "This is urgent"
  - "I'm frustrated"
  - "Please connect me to someone"
  - "I want to speak to a manager"

- **intent_escalation_issue**: User reports a problem
  - "Something's wrong"
  - "I have a problem"
  - "This isn't working"
  - "I need to escalate"
  - "I'm not satisfied"

## Intent-to-Document Mapping

| Intent | Primary Documents | Category |
|--------|-------------------|----------|
| intent_plan_inquiry | doc_001, doc_002, doc_007 | protection_plans |
| intent_plan_details | doc_004, doc_002, doc_007 | protection_plans |
| intent_pricing | doc_006 | protection_plans |
| intent_file_claim | doc_003, doc_008 | claims |
| intent_claim_status | doc_008, doc_003 | claims |
| intent_device_replacement | doc_009, doc_008 | claims |
| intent_contact_support | doc_005 | support |
| intent_activation | doc_010, doc_006 | protection_plans |
| intent_faq | doc_001, doc_005 | support |
| intent_welcome | doc_001, doc_005 | support |
| intent_escalation_urgent | ESCALATE | escalation |
| intent_escalation_issue | ESCALATE | escalation |
