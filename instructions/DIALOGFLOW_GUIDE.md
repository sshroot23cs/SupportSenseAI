# Dialog Flow Documentation

## Overview

The SquareTrade Chat Agent uses a sophisticated dialog flow system to manage conversation paths and provide contextual responses for different user intents.

## Architecture

### Components

1. **Intent Detection** - Identifies user intent from their query
2. **Dialog Flow States** - Defines conversation states and transitions
3. **Knowledge Base Integration** - Retrieves relevant documents for context
4. **LLM Generation** - Generates natural responses using retrieved context

## Intent Taxonomy

### 1. Product Information Intents

#### intent_welcome
- **Description**: Initial greeting and capability introduction
- **Keywords**: hi, hello, help, can you, what, do, capabilities, services
- **Entry Message**: Displays available capabilities
- **Flow States**: welcome_start → awaiting_user_input

#### intent_plan_inquiry
- **Description**: User asks about available plans
- **Keywords**: plan, offer, coverage, protection, device, what
- **Primary Documents**: doc_001, doc_002, doc_007, doc_010
- **Flow States**: plan_inquiry_start → plan_inquiry_clarify

#### intent_plan_details
- **Description**: User wants specific details about plans
- **Keywords**: included, coverage, exclusion, deductible, limit, what
- **Primary Documents**: doc_004, doc_002, doc_007
- **Flow States**: Multiple clarification states

#### intent_pricing
- **Description**: User asks about costs
- **Keywords**: cost, price, monthly, payment, discount, how much
- **Primary Documents**: doc_006
- **Flow States**: Breaks down pricing by device type

### 2. Claims Management Intents

#### intent_file_claim
- **Description**: User wants to file a claim
- **Keywords**: file, claim, damage, broken, damaged, how
- **Primary Documents**: doc_003, doc_008, doc_001
- **Flow States**: Guides through step-by-step claim filing

#### intent_claim_status
- **Description**: User checks claim status
- **Keywords**: status, claim, tracking, where, approved, long
- **Primary Documents**: doc_008, doc_003
- **Flow States**: Explains tracking mechanism and timelines

#### intent_device_replacement
- **Description**: User asks about replacement
- **Keywords**: replacement, replace, device, new, refurbished, when
- **Primary Documents**: doc_009, doc_008
- **Flow States**: Explains replacement process and timeline

### 3. Support Intents

#### intent_contact_support
- **Description**: User wants to contact support
- **Keywords**: contact, support, help, phone, agent, speak, how
- **Primary Documents**: doc_005
- **Flow States**: Provides contact information and escalation options

#### intent_activation
- **Description**: User wants to activate a plan
- **Keywords**: sign up, activate, purchase, enroll, started, how
- **Primary Documents**: doc_010, doc_006
- **Flow States**: Step-by-step activation guide

#### intent_faq
- **Description**: General questions about service
- **Keywords**: faq, question, know, common, more
- **Primary Documents**: doc_001, doc_005
- **Flow States**: Topic selection and answer

### 4. Escalation Intents

#### intent_escalation_urgent
- **Description**: User needs immediate assistance
- **Keywords**: urgent, immediate, frustrated, manager, now
- **Priority**: High
- **Action**: Creates escalation ticket with high priority

#### intent_escalation_issue
- **Description**: User reports a problem
- **Keywords**: problem, wrong, issue, escalate, not satisfied
- **Priority**: Medium
- **Action**: Documents issue and creates support ticket

## Dialog Flow Structure

Each dialog flow contains:

```json
{
  "name": "Flow Name",
  "description": "Flow description",
  "entry_message": "Initial message to user",
  "states": [
    {
      "state_id": "state_name",
      "type": "greeting|response|instruction|clarification|information|question|escalation|confirmation|end",
      "message": "Message to display",
      "next_states": ["next_state_1", "next_state_2"],
      "actions": ["action_1", "action_2"]
    }
  ]
}
```

### State Types

- **greeting**: Initial greeting message
- **response**: Response to user query
- **instruction**: Step-by-step instructions
- **clarification**: Request for clarification
- **information**: Informational message
- **question**: Question to user
- **escalation**: Escalation to human support
- **confirmation**: Confirmation message
- **end**: End of conversation

### Actions

- **retrieve_documents**: Search knowledge base for relevant documents
- **generate_answer**: Use LLM to generate contextual response
- **detect_intent**: Analyze user input to determine intent
- **create_escalation_ticket**: Create support ticket
- **set_priority_high**: Mark escalation as high priority
- **send_escalation_notification**: Send notification to support team

## Flow Examples

### Welcome Flow Example

```
User: "Hi"
↓
intent_welcome detected
↓
Display capabilities message
↓
awaiting_user_input state
↓
User selects topic
↓
Route to appropriate intent flow
```

### Plan Inquiry Flow Example

```
User: "What plans do you offer?"
↓
intent_plan_inquiry detected
↓
Retrieve doc_001, doc_002, doc_007, doc_010
↓
Generate answer using LLM
↓
Ask clarification: "Interested in Smartphones, Tablets, Laptops, or Appliances?"
↓
Route to specific device flow
```

### Urgent Escalation Flow Example

```
User: "I need immediate help!"
↓
intent_escalation_urgent detected (high priority)
↓
Create escalation ticket
↓
Set priority to HIGH
↓
Send notification to support team
↓
Confirm to user
```

## Integration with RAG Engine

The RAG engine uses dialog flows by:

1. **Intent Detection**: Identifies user intent from keywords
2. **Dialog Flow Retrieval**: Loads corresponding dialog flow
3. **State Tracking**: Maintains current conversation state
4. **Document Retrieval**: Fetches relevant documents
5. **Response Generation**: Uses LLM to generate contextual response
6. **State Transition**: Moves to next state based on logic

## Configuration Files

### intent_knowledge_base.json
- Defines intents and their properties
- Maps intents to documents
- Provides keywords for intent detection

### dialogflows.json
- Defines conversation states for each intent
- Specifies state transitions
- Outlines actions for each state

## Usage in Code

```python
from rag_engine import RAGEngine

engine = RAGEngine()

# Detect intent
intent, confidence = engine._detect_intent("What plans do you offer?")
# Result: ("intent_plan_inquiry", 0.85)

# Get dialog flow entry message
entry_msg = engine._get_dialogflow_entry_message(intent)
# Returns entry message for plan inquiry flow

# Process query with full context
response, metadata = engine.process_query("What plans do you offer?")
# Returns answer with metadata including intent, confidence, etc.
```

## Best Practices

1. **Intent Specificity**: Keep intent keywords distinct to avoid overlap
2. **Clear State Flow**: Design states that logically flow to the next
3. **Document Mapping**: Ensure intents map to relevant documents
4. **Error Handling**: Escalate on low confidence or errors
5. **User Feedback**: Provide clear messages at each state
6. **Timeout Management**: Handle long-running LLM operations gracefully

## Future Enhancements

1. **State Persistence**: Save conversation state across sessions
2. **Context Memory**: Remember previous interactions
3. **A/B Testing**: Test different dialog flows
4. **Analytics**: Track conversation paths and success rates
5. **Multi-turn Context**: Maintain context across multiple turns
6. **Personalization**: Customize flows based on user history
