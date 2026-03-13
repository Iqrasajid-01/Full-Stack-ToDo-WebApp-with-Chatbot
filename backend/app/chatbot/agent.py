"""
AI Chatbot Agent

Provides conversational task management using Cohere LLM.
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import calendar

from app.chatbot.logger import chatbot_logger
from mcp.tools.task_tools import (
    add_task_tool,
    list_tasks_tool,
    complete_task_tool,
    delete_task_tool,
    update_task_tool
)
from db.session import SessionLocal
from models.task import TaskCreate, TaskUpdate
from core.config import settings

logger = chatbot_logger

# Try to import Cohere
try:
    import cohere
    COHERE_AVAILABLE = True
except ImportError:
    COHERE_AVAILABLE = False
    logger.warning("Cohere package not installed. Using rule-based fallback.")


class ChatbotAgent:
    """
    AI Chatbot Agent using Cohere LLM for natural language task management.
    Falls back to rule-based detection if Cohere is unavailable.
    """

    def __init__(self, user_id: str, conversation_id: int):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.session = SessionLocal()
        self._last_task_id = None  # Track last created/mentioned task ID
        
        # Initialize Cohere client if available
        self.co = None
        if COHERE_AVAILABLE and settings.COHERE_API_KEY:
            try:
                self.co = cohere.Client(settings.COHERE_API_KEY)
                logger.info("Cohere client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Cohere client: {e}")
                self.co = None
        
        # Enhanced system prompt for better natural language understanding
        self.system_prompt = """You are an intelligent AI assistant helping users manage their todo tasks.
You have access to the following tools:
- add_task: Create a new task (requires: title, optional: description, priority, due_date)
- list_tasks: List user's tasks (optional: completed filter)
- complete_task: Mark a task as completed (requires: task_id)
- delete_task: Delete a task (requires: task_id)
- update_task: Update task details (requires: task_id, optional: title, description, priority)

YOUR CORE STRENGTH: Understand ANY type of user input - broken English, natural language, professional English, short phrases, Roman Urdu, or even single words. Use intelligence and context to interpret what the user means.

CONTEXT-AWARE FOLLOW-UPS:
- If user just created a task and then says "set priority to low" → Update the LAST created task
- If user says "make it high priority" without task ID → Update the LAST mentioned task
- If user says "change the date to tomorrow" → Update the LAST task's due date
- ALWAYS use context to understand which task the user is referring to

When the user wants to:
- Create a task: Use add_task with title and optional description, priority (high/medium/low), and due_date (YYYY-MM-DD format)
- View tasks: Use list_tasks
- Complete a task: Use complete_task with the task_id
- Delete a task: Use delete_task with the task_id
- Update a task: Use update_task with the task_id (or use context to find the last created task)

BE INTELLIGENT ABOUT INTERPRETING MESSAGES:
- "washing clothes on coming friday 6pm" → title: "Washing Clothes", due_date: "coming friday", description: "6pm"
- "i need to go in a party next monday 9pm" → title: "Go To Party", due_date: "next monday", description: "9pm"
- "Designing on 23/2/2026" → title: "Designing", due_date: "2026-02-23"
- "Meeting tomorrow 3pm" → title: "Meeting", due_date: "tomorrow's date", description: "3pm"
- "Buy groceries low priority" → title: "Buy groceries", priority: "low"
- "Submit report next friday high" → title: "Submit report", due_date: "next friday", priority: "high"
- "Dinner 8pm" → title: "Dinner", description: "8pm"
- "Task: call mom" → title: "call mom"
- "remind me to pay bills" → title: "pay bills"
- "i need to finish project" → title: "finish project"
- "23/02/2026 designing" → title: "Designing", due_date: "2026-02-23"
- "designing task 23 feb" → title: "designing", due_date: "2026-02-23"
- "i have to go shopping" → title: "Go Shopping"
- "i need to attend meeting" → title: "Attend Meeting"
- "going to doctor" → title: "Going To Doctor"
- "party at friend's place" → title: "Party"

DATE PARSING RULES (BE FLEXIBLE):
- "23/2/2026", "23/02/2026", "2-23-2026", "2026-02-23" → all mean February 23, 2026
- "23 feb", "feb 23", "23rd feb" → February 23 of current year
- "tomorrow", "next week", "next monday", "in 2 days" → calculate relative date
- "today", "tonight" → today's date
- "coming friday", "this coming monday" → next occurrence of that weekday
- "next month", "in a week" → calculate relative date
- If only time mentioned (e.g., "3pm", "8pm", "6 pm"), put it in description
- If date format is ambiguous, assume DD/MM/YYYY or MM/DD/YYYY based on context

PRIORITY PARSING:
- "high", "urgent", "important", "priority", "!" → high
- "medium", "normal", "regular" → medium
- "low", "casual", "whenever" → low
- If no priority mentioned, use "medium" as default

TITLE EXTRACTION:
- Extract the main action/object from the message
- Remove date/time/priority words from title
- Keep title concise but meaningful
- If message is just a noun/verb, use it as title
- For "i need to go X" → title is "Go X" or just "X"
- For "i have to attend X" → title is "Attend X" or just "X"

DESCRIPTION:
- Put additional details like time, location, notes
- Include context that doesn't fit in title
- Time expressions like "6pm", "3:30 pm" go in description

IMPORTANT:
1. ALWAYS try to extract task details even from very short or broken messages
2. Use context and intelligence to understand user intent
3. If user mentions a date in ANY format, parse it correctly
4. Be flexible and forgiving with input format
5. For follow-up messages without task ID, use the LAST created/mentioned task
6. Respond naturally and confirm what you understood

Format your responses with emojis for better readability.

Respond in this format:
1. If you need to call a tool, include a JSON block:
   ```json
   {"tool": "tool_name", "params": {"param1": "value1"}}
   ```
2. Then provide a friendly, natural response to the user."""

    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        Uses Cohere LLM if available, otherwise falls back to rule-based detection.
        """
        try:
            # Validate input
            if not message or not message.strip():
                return {
                    "reply": "I didn't receive any message. Could you please try again?",
                    "tool_calls": []
                }

            # Try to use Cohere LLM first
            if self.co:
                return await self._process_with_cohere(message)
            else:
                # Fallback to rule-based
                return await self._process_rule_based(message)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            # Fallback to rule-based on error
            try:
                return await self._process_rule_based(message)
            except Exception as e2:
                return {
                    "reply": f"I apologize, but I encountered an error: {str(e2)}",
                    "tool_calls": []
                }
        finally:
            if self.session:
                self.session.close()

    async def _process_with_cohere(self, message: str) -> Dict[str, Any]:
        """Process message using Cohere LLM."""
        try:
            # Get conversation history for context
            recent_messages = self._get_recent_history()
            
            # Build the prompt
            prompt = self._build_cohere_prompt(message, recent_messages)
            
            # Call Cohere API
            response = self.co.chat(
                model=settings.COHERE_MODEL,
                message=prompt,
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            ai_text = response.text
            
            # Extract tool calls from response using JSON pattern
            tool_calls = self._extract_tool_calls(ai_text)
            
            # Execute any tool calls
            if tool_calls:
                for tool_call in tool_calls:
                    result = await self._execute_tool(tool_call)
                    tool_call["result"] = result
            
            # Generate final response
            reply = self._generate_response(ai_text, tool_calls)
            
            return {
                "reply": reply,
                "tool_calls": tool_calls
            }
            
        except Exception as e:
            logger.error(f"Cohere processing error: {str(e)}", exc_info=True)
            # Fallback to rule-based
            return await self._process_rule_based(message)

    def _build_cohere_prompt(self, message: str, recent_messages: List[Dict]) -> str:
        """Build prompt for Cohere API with enhanced few-shot examples."""
        history_context = ""
        if recent_messages:
            history_context = "\n\nRecent conversation:\n"
            for msg in recent_messages[-5:]:  # Last 5 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                history_context += f"{role}: {msg['content']}\n"

        # Calculate tomorrow's date for the example
        tomorrow = (datetime.now().date() + timedelta(days=1)).strftime('%Y-%m-%d')

        prompt = f'''{self.system_prompt}

{history_context}

EXAMPLES OF HOW TO INTERPRET MESSAGES:
User: "Designing on 23/2/2026"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Designing", "due_date": "2026-02-23", "priority": "medium"}}}}
```
✅ Created task "Designing" due on Feb 23, 2026!

User: "meeting tomorrow 3pm"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Meeting", "due_date": "{tomorrow}", "description": "3pm", "priority": "medium"}}}}
```
✅ Scheduled "Meeting" for tomorrow at 3pm!

User: "buy groceries low priority"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Buy groceries", "priority": "low"}}}}
```
✅ Added "Buy groceries" with low priority!

User: "23/02/2026 designing"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Designing", "due_date": "2026-02-23", "priority": "medium"}}}}
```
✅ Created task "Designing" for Feb 23, 2026!

User: "submit report next friday high"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Submit report", "due_date": "next friday", "priority": "high"}}}}
```
✅ Added "Submit report" with high priority due next Friday!

User: "dinner 8pm"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Dinner", "description": "8pm", "priority": "medium"}}}}
```
✅ Added "Dinner" at 8pm!

User: "remind me to pay bills"
Assistant: ```json
{{"tool": "add_task", "params": {{"title": "Pay bills", "priority": "medium"}}}}
```
✅ Added reminder to "Pay bills"!

User: "show tasks"
Assistant: ```json
{{"tool": "list_tasks", "params": {{}}}}
```
📋 Here are your tasks...

Current user message: "{message}"

IMPORTANT: Respond in this format:
1. First, decide if you need to call a tool. If yes, include a JSON block like:
   ```json
   {{"tool": "tool_name", "params": {{"param1": "value1"}}}}
   ```
2. Then provide a friendly response to the user.

Available tools:
- add_task: {{"tool": "add_task", "params": {{"title": "string", "description": "string (optional)", "priority": "high|medium|low (default: medium)", "due_date": "YYYY-MM-DD (optional)"}}}}
- list_tasks: {{"tool": "list_tasks", "params": {{"completed": "true|false|null (optional)"}}}}
- complete_task: {{"tool": "complete_task", "params": {{"task_id": "number"}}}}
- delete_task: {{"tool": "delete_task", "params": {{"task_id": "number"}}}}
- update_task: {{"tool": "update_task", "params": {{"task_id": "number", "title/description/priority": "values"}}}}

Respond naturally to the user's request.'''

        return prompt

    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """Extract tool calls from Cohere response."""
        tool_calls = []
        
        # Look for JSON blocks in the response
        json_pattern = r'```json\s*({[\s\S]*?})\s*```'
        matches = re.findall(json_pattern, text, re.IGNORECASE)
        
        for match in matches:
            try:
                tool_data = json.loads(match)
                if "tool" in tool_data and "params" in tool_data:
                    tool_calls.append({
                        "tool": tool_data["tool"],
                        "parameters": tool_data["params"]
                    })
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON: {match}")
                continue
        
        return tool_calls

    def _get_recent_history(self) -> List[Dict[str, str]]:
        """Get recent conversation history from database."""
        try:
            from models.message import Message
            messages = self.session.query(Message).filter(
                Message.conversation_id == self.conversation_id
            ).order_by(Message.created_at.desc()).limit(10).all()
            
            return [
                {"role": msg.role, "content": msg.content}
                for msg in reversed(messages)
            ]
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return []

    async def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        tool_name = tool_call.get("tool")
        params = tool_call.get("parameters", {})
        
        try:
            if tool_name == "add_task":
                # Convert due_date string to datetime if provided
                due_date = None
                if params.get("due_date"):
                    try:
                        due_date = datetime.strptime(params["due_date"], "%Y-%m-%d")
                    except ValueError:
                        logger.warning(f"Invalid due_date format: {params.get('due_date')}")

                task_data = TaskCreate(
                    title=params.get("title", "Untitled Task"),
                    description=params.get("description"),
                    completed=False,
                    priority=params.get("priority", "medium"),
                    due_date=due_date
                )
                result = await add_task_tool(self.user_id, task_data, self.session)
                result_dict = result.model_dump()
                
                # Store the created task ID for context-aware follow-ups
                self._last_task_id = result_dict.get("id")
                
                return result_dict
                
            elif tool_name == "list_tasks":
                completed = params.get("completed")
                if completed is not None:
                    completed = str(completed).lower() in ("true", "1", "yes")
                results = await list_tasks_tool(
                    self.user_id,
                    completed=completed,
                    limit=50,
                    skip=0,
                    session=self.session
                )
                return {"tasks": [r.model_dump() for r in results]}
                
            elif tool_name == "complete_task":
                task_id = params.get("task_id")
                if not task_id:
                    return {"error": "Task ID is required"}
                result = await complete_task_tool(
                    self.user_id,
                    int(task_id),
                    completed=True,
                    session=self.session
                )
                return result.model_dump()
                
            elif tool_name == "delete_task":
                task_id = params.get("task_id")
                if not task_id:
                    return {"error": "Task ID is required"}
                result = await delete_task_tool(self.user_id, int(task_id), self.session)
                return {"deleted": result, "task_id": task_id}
                
            elif tool_name == "update_task":
                task_id = params.get("task_id")
                if not task_id:
                    return {"error": "Task ID is required"}
                task_update = TaskUpdate(
                    title=params.get("title"),
                    description=params.get("description"),
                    priority=params.get("priority"),
                    due_date=None
                )
                result = await update_task_tool(
                    self.user_id,
                    int(task_id),
                    task_update,
                    self.session
                )
                return result.model_dump()
                
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"error": str(e)}

    def _generate_response(self, ai_text: str, tool_calls: List[Dict]) -> str:
        """Generate final response from AI output."""
        # Remove JSON blocks from the response
        clean_text = re.sub(r'```json\s*{[\s\S]*?}\s*```', '', ai_text)
        clean_text = clean_text.strip()
        
        # Add tool execution summaries
        if tool_calls:
            summaries = []
            for tc in tool_calls:
                tool = tc.get("tool")
                result = tc.get("result", {})
                
                if tool == "add_task" and result.get("id"):
                    summaries.append(f"✅ Created task: {result.get('title')} (ID: {result.get('id')})")
                elif tool == "list_tasks":
                    tasks = result.get("tasks", [])
                    summaries.append(f"📋 Found {len(tasks)} task(s)")
                elif tool == "complete_task" and result.get("title"):
                    summaries.append(f"✅ Completed: {result.get('title')}")
                elif tool == "delete_task":
                    summaries.append(f"🗑️ Deleted task {tc.get('parameters', {}).get('task_id')}")
                elif tool == "update_task" and result.get("title"):
                    summaries.append(f"✏️ Updated: {result.get('title')}")
            
            if summaries:
                clean_text = "\n".join(summaries) + "\n\n" + clean_text
        
        return clean_text if clean_text else "Done!"

    async def _process_rule_based(self, message: str) -> Dict[str, Any]:
        """Fallback rule-based processing with intelligent preprocessing."""
        try:
            # Preprocess message to handle common patterns
            processed_message = self._preprocess_message(message)
            intent = self._analyze_intent(processed_message)
            tool_calls = []

            # Handle case where no intent was detected
            if intent["action"] is None:
                # Check if it's a question or greeting
                if self._is_greeting(message):
                    return {
                        "reply": "👋 Hello! I'm your AI task assistant. I can help you create, view, complete, or delete tasks. What would you like to do?",
                        "tool_calls": []
                    }
                elif self._is_question(message):
                    return {
                        "reply": f"I received your question: \"{message}\". I can help you manage tasks - try saying \"create a task\" or \"show my tasks\"!",
                        "tool_calls": []
                    }
                else:
                    # Try to create a task from the message anyway
                    intent = {"action": "add_task", "params": {
                        "title": self._extract_title_from_natural_message(message),
                        "description": self._extract_description(message),
                        "priority": self._extract_priority(message),
                        "due_date": self._extract_due_date(message)
                    }}

            if intent["action"] == "add_task":
                result = await self._handle_add_task(intent["params"])
                tool_calls.append({"tool": "add_task", "parameters": intent["params"], "result": result})
                reply = self._format_add_task_response(result, intent["params"])
            elif intent["action"] == "list_tasks":
                result = await self._handle_list_tasks(intent["params"])
                tool_calls.append({"tool": "list_tasks", "parameters": intent["params"], "result": {"task_count": len(result)}})
                reply = self._format_list_tasks_response(result)
            elif intent["action"] == "complete_task":
                result = await self._handle_complete_task(intent["params"])
                tool_calls.append({"tool": "complete_task", "parameters": intent["params"], "result": result})
                reply = self._format_complete_task_response(result)
            elif intent["action"] == "delete_task":
                result = await self._handle_delete_task(intent["params"])
                tool_calls.append({"tool": "delete_task", "parameters": intent["params"], "result": result})
                reply = self._format_delete_task_response(result)
            elif intent["action"] == "update_task":
                result = await self._handle_update_task(intent["params"])
                tool_calls.append({"tool": "update_task", "parameters": intent["params"], "result": result})
                reply = self._format_update_task_response(result)
            else:
                reply = self._handle_general_query(message)

            return {"reply": reply, "tool_calls": tool_calls if tool_calls else []}
        except Exception as e:
            logger.error(f"Rule-based processing error: {str(e)}", exc_info=True)
            return {
                "reply": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "tool_calls": []
            }

    def _preprocess_message(self, message: str) -> str:
        """Preprocess message to normalize common patterns."""
        # Trim whitespace
        message = message.strip()

        # Handle "title" on date" pattern (e.g., "Designing" on 23/2/2026)
        import re
        quoted_on_date = re.search(r'"([^"]+)"\s+on\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})', message, re.IGNORECASE)
        if quoted_on_date:
            title = quoted_on_date.group(1)
            date = quoted_on_date.group(2)
            return f"Create task {title} on {date}"

        # Handle title on date without quotes (e.g., Designing on 23/2/2026)
        title_on_date = re.search(r'^([A-Za-z][a-zA-Z\s]+?)\s+on\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})', message, re.IGNORECASE)
        if title_on_date:
            title = title_on_date.group(1).strip()
            date = title_on_date.group(2)
            return f"Create task {title} on {date}"

        # Handle "date title" pattern (e.g., "23/02/2026 designing")
        date_title = re.search(r'^(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+([A-Za-z].+)$', message, re.IGNORECASE)
        if date_title:
            date = date_title.group(1)
            title = date_title.group(2).strip()
            return f"Create task {title} on {date}"

        # Handle "title date priority" all together
        complex_pattern = re.search(r'^([A-Za-z].+?)\s+(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+(high|low|medium|urgent|normal)', message, re.IGNORECASE)
        if complex_pattern:
            title = complex_pattern.group(1).strip()
            date = complex_pattern.group(2)
            priority = complex_pattern.group(3).lower()
            return f"Create task {title} on {date} {priority} priority"

        # Handle "date title" pattern with weekday (e.g., "next monday party")
        weekday_title = re.search(r'^(next\s+\w+\s+)([A-Za-z].+)$', message, re.IGNORECASE)
        if weekday_title:
            weekday = weekday_title.group(1).strip()
            title = weekday_title.group(2).strip()
            return f"Create task {title} on {weekday}"

        # Handle "coming <weekday> <title>" pattern
        coming_weekday = re.search(r'^(coming\s+\w+\s+)([A-Za-z].+)$', message, re.IGNORECASE)
        if coming_weekday:
            weekday = coming_weekday.group(1).strip()
            title = coming_weekday.group(2).strip()
            return f"Create task {title} on {weekday}"

        return message

    # Rule-based methods (fallback)
    def _analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze intent using rule-based detection."""
        message_lower = message.lower().strip()

        # FIRST: Check for list/view tasks patterns (HIGHEST PRIORITY for queries)
        # This prevents "show tasks with priority low" from being misinterpreted as update
        list_tasks_patterns = [
            "show tasks", "list tasks", "my tasks", "what tasks", "view tasks", 
            "get tasks", "show my tasks", "show all", "list all", "see all tasks",
            "show all tasks", "list all tasks", "view all tasks", "see all",
            "show completed", "list completed", "show pending", "list pending",
            "mere kaam", "kaam dikhao", "tasks dikhao", "saare kaam", "sab kaam",
            "show task list", "task list", "all tasks", "complete task list",
            "show all task", "list all task"
        ]
        
        if any(phrase in message_lower for phrase in list_tasks_patterns):
            # Check for completed filter
            completed = None
            if any(word in message_lower for word in ["completed", "done", "finished"]):
                completed = True
            elif any(word in message_lower for word in ["pending", "incomplete", "active", "not done"]):
                completed = False
            # Note: "priority" in message doesn't change the filter - just show all tasks
            return {"action": "list_tasks", "params": {"completed": completed}}

        # SECOND: Check for task completion patterns
        if any(phrase in message_lower for phrase in ["complete task", "finish task", "done with task", "mark as done", "mark complete", "kaam complete karo", "kaam khatam", "ho gaya", "ho gaya kaam", "complete ho gaya", "mark as complete", "mark complete"]):
            task_id = self._extract_task_id(message) or self._extract_task_by_title(message) or self._last_task_id
            return {"action": "complete_task", "params": {"task_id": task_id, "completed": True}}

        # Mark task pattern (shorthand for mark as complete)
        if "mark" in message_lower and ("id" in message_lower or "task" in message_lower):
            # Check if it's not "mark as incomplete"
            if "incomplete" not in message_lower and "wapis" not in message_lower:
                task_id = self._extract_task_id(message) or self._last_task_id
                if task_id:
                    return {"action": "complete_task", "params": {"task_id": task_id, "completed": True}}

        # Unmark/reopen task patterns (mark as incomplete)
        if any(phrase in message_lower for phrase in ["mark as incomplete", "mark incomplete", "unmark task", "reopen task", "unmark", "incomplete task", "kaam incomplete karo", "wapis karo", "uncross karo"]):
            task_id = self._extract_task_id(message) or self._extract_task_by_title(message) or self._last_task_id
            return {"action": "complete_task", "params": {"task_id": task_id, "completed": False}}

        # THIRD: Check for delete task patterns
        if any(phrase in message_lower for phrase in ["delete task", "remove task", "cancel task", "kaam delete karo", "kaam hatao", "kaam mita do", "remove karo"]):
            task_id = self._extract_task_id(message) or self._last_task_id
            return {"action": "delete_task", "params": {"task_id": task_id}}

        # FOURTH: Check for update task patterns (EXPLICIT update keywords ONLY)
        # Require explicit action words to avoid false positives
        if any(phrase in message_lower for phrase in ["update task", "edit task", "change task", "modify task", "kaam update karo", "kaam change karo", "kaam edit karo", "set task", "task set", "change the priority", "update the priority", "make the priority", "set the priority", "change priority", "update priority"]):
            task_id = self._extract_task_id(message) or self._last_task_id
            return {"action": "update_task", "params": {
                "task_id": task_id,
                "title": self._extract_title_from_natural_message(message),
                "description": self._extract_description(message),
                "priority": self._extract_priority(message),
                "due_date": self._extract_due_date(message)
            }}

        # Set task time pattern (e.g., "set task id = 105 time 7:00 am")
        if "time" in message_lower and ("am" in message_lower or "pm" in message_lower):
            task_id = self._extract_task_id(message) or self._last_task_id
            if task_id:
                time_str = self._extract_time(message)
                if time_str:
                    return {"action": "update_task", "params": {
                        "task_id": task_id,
                        "title": None,
                        "description": f"Time: {time_str}",
                        "priority": None,
                        "due_date": None
                    }}

        # FIFTH: Check for Roman Urdu intents
        roman_urdu_intent = self._analyze_roman_urdu_intent(message)
        if roman_urdu_intent and roman_urdu_intent.get("action"):
            return roman_urdu_intent

        # SIXTH: Check for follow-up date correction (e.g., "make the date correct", "fix the date", "set it to...")
        # Only for SHORT follow-up messages, not full sentences
        if self._is_date_correction(message):
            task_id = self._get_context_task_id(message)
            if task_id:
                due_date = self._extract_due_date(message)
                if not due_date:
                    due_date = self._get_date_from_history()
                if due_date:
                    return {"action": "update_task", "params": {
                        "task_id": task_id,
                        "priority": None,
                        "title": None,
                        "description": None,
                        "due_date": due_date
                    }}

        # SEVENTH: Check for follow-up priority update
        # ONLY match if it has explicit action words AND is a short follow-up message
        if self._is_priority_update(message):
            task_id = self._get_context_task_id(message)
            if task_id:
                return {"action": "update_task", "params": {
                    "task_id": task_id,
                    "priority": self._extract_priority(message),
                    "title": None,
                    "description": None,
                    "due_date": None
                }}

        # EIGHTH: Check for follow-up due date update
        if self._is_due_date_update(message):
            task_id = self._get_context_task_id(message)
            if task_id:
                return {"action": "update_task", "params": {
                    "task_id": task_id,
                    "priority": None,
                    "title": None,
                    "description": None,
                    "due_date": self._extract_due_date(message)
                }}

        # NINTH: Check for combined priority + due date follow-up
        # Only for SHORT follow-up messages (< 6 words)
        if self._is_combined_priority_date_update(message):
            task_id = self._get_context_task_id(message)
            if task_id:
                return {"action": "update_task", "params": {
                    "task_id": task_id,
                    "priority": self._extract_priority(message),
                    "title": None,
                    "description": None,
                    "due_date": self._extract_due_date(message)
                }}

        # TENTH: Check for task creation patterns
        add_task_patterns = [
            # Explicit task creation
            "create task", "add task", "new task", "i need to", "i want to",
            "remind me to", "create a task", "add a task",
            # Natural language patterns
            "i have to", "i need", "i want", "have to", "going to",
            "don't forget to", "remember to", "must", "should",
            # Event/schedule patterns
            "i have", "there is", "we have", "meeting", "appointment",
            "dinner", "lunch", "breakfast", "party", "event",
            # Roman Urdu patterns
            "mera kaam hai", "yeh kaam hai", "kaam add karo", "task banao",
            "yaad dila", "mujhe yeh karna hai", "mujhe woh karna hai",
            "kaam likh lo", "task add karo", "naya kaam", "kaam hai",
            "mujhe jaana hai", "mujhe khareedna hai", "mujhe milna hai",
            # Mixed English/Urdu
            "create kaam", "add task karo", "new kaam", "task create",
            "yeh task add", "iska task banao", "task rakh lo",
        ]

        if any(phrase in message_lower for phrase in add_task_patterns):
            # Make sure it's not just a question or unrelated statement
            if not self._is_question(message) and not self._is_greeting(message):
                return {"action": "add_task", "params": {
                    "title": self._extract_title_from_natural_message(message),
                    "description": self._extract_description(message),
                    "priority": self._extract_priority(message),
                    "due_date": self._extract_due_date(message)
                }}

        # Handle very short messages that are likely task titles (2-4 words)
        word_count = len(message.split())
        if 2 <= word_count <= 4 and not self._is_question(message) and not self._is_greeting(message):
            # Check if it contains any task-like keywords
            task_like_words = ["buy", "get", "make", "do", "go", "call", "send", "meet", 
                              "attend", "finish", "complete", "write", "read", "clean",
                              "cook", "shop", "pay", "submit", "upload", "download"]
            has_task_word = any(word in message_lower for word in task_like_words)
            
            # If it has a task word or looks like a command, treat as task creation
            if has_task_word or (message_lower and not message_lower.endswith('?')):
                return {"action": "add_task", "params": {
                    "title": self._extract_title_from_natural_message(message),
                    "description": self._extract_description(message),
                    "priority": self._extract_priority(message),
                    "due_date": self._extract_due_date(message)
                }}

        # ELEVENTH: Check for implicit task creation (e.g., "washing clothes on friday", "party next monday")
        # If message has a date reference and looks like a task title, treat it as task creation
        has_date = self._extract_due_date(message) is not None
        has_event_keyword = any(keyword in message_lower for keyword in [
            "party", "meeting", "dinner", "lunch", "breakfast", "event",
            "appointment", "concert", "show", "movie", "game", "match",
            "conference", "seminar", "workshop", "class", "lecture",
            "trip", "vacation", "flight", "train", "bus",
            "doctor", "dentist", "hospital", "clinic",
            "shopping", "groceries", "errands", "chores",
            "birthday", "wedding", "funeral", "ceremony", "celebration",
            "deadline", "submission", "exam", "test", "quiz",
            "washing", "cleaning", "cooking", "exercise", "workout",
        ])

        # Count words excluding date expressions
        words = message.split()
        word_count = len(words)

        # If message has a date AND (has event keyword OR is short phrase < 8 words without question/greeting)
        if has_date and (has_event_keyword or (word_count < 8 and not self._is_question(message) and not self._is_greeting(message))):
            # Check if it doesn't match any other intent first
            # This is a fallback for implicit task creation
            return {"action": "add_task", "params": {
                "title": self._extract_title_from_natural_message(message),
                "description": self._extract_description(message),
                "priority": self._extract_priority(message),
                "due_date": self._extract_due_date(message)
            }}

        return {"action": None, "params": {}}

    def _analyze_roman_urdu_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Analyze Roman Urdu intent for task operations (including mixed English/Urdu)."""
        message_lower = message.lower().strip()

        # Only process if message contains common Roman Urdu words
        # This prevents English-only messages from being misinterpreted
        roman_urdu_markers = ["kaam", "karo", "banao", "dikhao", "karna", "hai", "mujhe", "yeh", "woh",
                              "jaana", "khareedna", "milna", "likh", "naya", "mera", "mere",
                              "ho gaya", "khatam", "wapis", "hatao", "mita", "badlo", "zyada", "kam",
                              "kal", "aaj", "parson", "tak", "batao"]
        
        # Remove short/common English words that could cause false positives
        # "lo" was matching inside "clothes", "list" inside "enlist", etc.
        # Use word boundary matching to prevent substring false positives
        import re
        has_urdu_marker = False
        for marker in roman_urdu_markers:
            # Use word boundary regex to match whole words only
            if re.search(r'\b' + re.escape(marker) + r'\b', message_lower):
                has_urdu_marker = True
                break
        
        # If no Roman Urdu markers, skip this analysis (let English patterns handle it)
        if not has_urdu_marker:
            return None
        
        # Roman Urdu + English mixed: Create task patterns
        create_patterns = [
            "kaam add karo", "task banao", "naya kaam", "kaam hai",
            "mujhe yeh karna hai", "mujhe woh karna hai", "kaam likh lo",
            "task add karo", "mera kaam hai", "yeh kaam hai",
            "mujhe jaana hai", "mujhe khareedna hai", "mujhe milna hai",
            "mujhe karna hai", "kaam banane ka", "task create karo",
            # Mixed English/Urdu
            "create kaam", "add task karo", "new kaam", "task create",
            "yeh task add", "iska task banao", "task rakh lo",
        ]
        
        if any(pattern in message_lower for pattern in create_patterns):
            if not self._is_question(message) and not self._is_greeting(message):
                return {"action": "add_task", "params": {
                    "title": self._extract_title_from_natural_message(message),
                    "description": self._extract_description(message),
                    "priority": self._extract_priority(message),
                    "due_date": self._extract_due_date(message)
                }}
        
        # Roman Urdu + English mixed: List tasks patterns
        list_patterns = [
            "mere kaam", "kaam dikhao", "tasks dikhao", "saare kaam",
            "kaam list", "meri tasks", "kaam batao", "tasks batao",
            "kaam kya hain", "kya kaam hai", "kaam show karo",
            # Mixed English/Urdu
            "show kaam", "list kaam", "tasks dikhao", "mere tasks",
            "all kaam", "my tasks dikhao", "kaam show",
        ]
        
        if any(pattern in message_lower for pattern in list_patterns):
            completed = True if "completed" in message_lower or "done" in message_lower or "khatam" in message_lower else (False if "pending" in message_lower or "chalu" in message_lower else None)
            return {"action": "list_tasks", "params": {"completed": completed}}
        
        # Roman Urdu + English mixed: Complete task patterns
        complete_patterns = [
            "kaam complete karo", "kaam khatam", "ho gaya", "ho gaya kaam",
            "complete ho gaya", "kaam done", "kaam finish", "khatam karo",
            "kaam pura hua", "task complete", "kaam ho gaya",
            # Mixed English/Urdu
            "complete kaam", "finish kaam", "done kaam", "task pura",
            "kaam mark done", "task complete karo", "mark complete kaam",
        ]
        
        if any(pattern in message_lower for pattern in complete_patterns):
            task_id = self._extract_task_id(message) or self._extract_task_by_title(message) or self._last_task_id
            return {"action": "complete_task", "params": {"task_id": task_id, "completed": True}}
        
        # Roman Urdu + English mixed: Incomplete task patterns
        incomplete_patterns = [
            "kaam incomplete karo", "wapis karo", "uncross karo",
            "kaam wapis", "incomplete karo", "kaam undo",
            # Mixed English/Urdu
            "incomplete kaam", "mark incomplete", "kaam mark incomplete",
            "task wapis", "undo kaam", "reopen kaam",
        ]
        
        if any(pattern in message_lower for pattern in incomplete_patterns):
            task_id = self._extract_task_id(message) or self._extract_task_by_title(message) or self._last_task_id
            return {"action": "complete_task", "params": {"task_id": task_id, "completed": False}}
        
        # Roman Urdu + English mixed: Delete task patterns
        delete_patterns = [
            "kaam delete karo", "kaam hatao", "kaam mita do", "remove karo",
            "kaam remove", "task delete", "kaam khatam karo",
            # Mixed English/Urdu
            "delete kaam", "remove kaam", "task hatao", "task mita do",
            "kaam mark delete", "delete task karo",
        ]
        
        if any(pattern in message_lower for pattern in delete_patterns):
            task_id = self._extract_task_id(message) or self._last_task_id
            return {"action": "delete_task", "params": {"task_id": task_id}}
        
        # Roman Urdu + English mixed: Update task patterns
        update_patterns = [
            "kaam update karo", "kaam change karo", "kaam edit karo",
            "kaam badlo", "task update", "kaam modify",
            # Mixed English/Urdu
            "update kaam", "change kaam", "edit kaam", "task badlo",
            "modify kaam", "task edit karo", "update task karo",
            # Name/title change patterns
            "naam badlo", "name change karo", "title badlo", "naam change",
            "name badlo", "title change karo", "kaam ka naam badlo",
        ]

        if any(pattern in message_lower for pattern in update_patterns):
            task_id = self._extract_task_id(message) or self._last_task_id
            return {"action": "update_task", "params": {
                "task_id": task_id,
                "title": self._extract_title_from_natural_message(message),
                "description": self._extract_description(message),
                "priority": self._extract_priority(message),
                "due_date": self._extract_due_date(message)
            }}
        
        # Roman Urdu + English mixed: Priority update patterns (short follow-ups only)
        priority_patterns = [
            "priority high", "priority low", "priority medium",
            "zyada important", "kam important", "zaroori",
            "priority zyada", "priority kam",
            # Mixed English/Urdu
            "high priority karo", "low priority karo", "priority badhao",
            "priority kam karo", "zyada priority", "important banao",
        ]
        
        # Only match priority patterns for short messages (follow-ups)
        word_count = len(message.split())
        if word_count <= 6 and any(pattern in message_lower for pattern in priority_patterns):
            task_id = self._get_context_task_id(message)
            if task_id:
                return {"action": "update_task", "params": {
                    "task_id": task_id,
                    "priority": self._extract_priority(message),
                    "title": None,
                    "description": None,
                    "due_date": None
                }}

        # Roman Urdu + English mixed: Date update patterns (short follow-ups only)
        date_patterns = [
            "kal tak", "aaj tak", "is tak", "date kal",
            "due kal", "kal ka", "parson", "next week",
            # Mixed English/Urdu
            "due date kal", "date change kal", "kal ka kaam",
            "aaj ka kaam", "parson tak", "this week tak",
        ]

        # Only match date patterns for short messages (follow-ups)
        # REQUIRE Roman Urdu markers or explicit date update keywords
        # This prevents English messages like "washing clothes on friday" from being treated as updates
        if word_count <= 6:
            # Use the has_urdu_marker computed at the top of the function (with word boundaries)
            has_explicit_date_keyword = any(kw in message_lower for kw in ["due date", "change date", "update date", "fix date", "set date", "date change", "make date"])

            # Only treat as date update if it has Urdu markers OR explicit date keywords
            if has_urdu_marker or has_explicit_date_keyword:
                if any(pattern in message_lower for pattern in date_patterns) or self._extract_due_date(message):
                    task_id = self._get_context_task_id(message)
                    if task_id:
                        return {"action": "update_task", "params": {
                            "task_id": task_id,
                            "priority": None,
                            "title": None,
                            "description": None,
                            "due_date": self._extract_due_date(message)
                        }}
        
        return None

    def _is_date_correction(self, message: str) -> bool:
        """Check if message is a date correction request."""
        message_lower = message.lower()
        correction_patterns = [
            "make the date correct", "fix the date", "correct the date",
            "set the date", "update the date", "change the date",
            "the date is wrong", "wrong date", "incorrect date",
            "make it correct", "fix it", "correct it", "that's wrong",
            "not correct", "incorrect", "make correct",
            # Also match "make/correct/fix + date reference" patterns
            "make correct", "fix correct",
        ]
        has_correction = any(pattern in message_lower for pattern in correction_patterns)
        has_date_reference = "date" in message_lower or "day" in message_lower or "when" in message_lower
        # Also check if there's a date mentioned in the message
        has_date_value = self._extract_due_date(message) is not None

        # If it's a correction phrase with date reference, or correction with date in history
        if has_correction and (has_date_reference or has_date_value):
            return True

        # If just "make it correct" or "fix it", check if there's a date in history
        if has_correction and not has_date_reference:
            # Look for date in conversation history
            history_date = self._get_date_from_history()
            if history_date:
                return True

        return False

    def _get_date_from_history(self) -> Optional[str]:
        """Try to extract a date from recent conversation history."""
        try:
            from models.message import Message
            # Get recent messages from the conversation
            messages = self.session.query(Message).filter(
                Message.conversation_id == self.conversation_id
            ).order_by(Message.created_at.desc()).limit(10).all()
            
            # Look for date patterns in recent user messages (not assistant responses)
            for msg in messages:
                if msg.role == "user":  # Only check user messages
                    due_date = self._extract_due_date(msg.content)
                    if due_date:
                        return due_date
        except Exception:
            pass
        return None

    def _is_question(self, message: str) -> bool:
        """Check if message is a question (not a task creation)."""
        message_lower = message.lower()
        question_words = ["what", "when", "where", "who", "why", "how", "can you", "could you", "will you", "do you", "are you", "is there"]
        return message.strip().endswith("?") or any(word in message_lower for word in question_words)

    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting (not a task creation)."""
        message_lower = message.lower()
        greetings = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "thank", "thanks",
            # Roman Urdu greetings
            "assalam o alaikum", "walaikum assalam", "adaab", "namaste",
            "kaise ho", "kya haal hai", "kaise hain aap", "salam",
            "shukriya", "thank you", "thanks",
        ]
        return any(word in message_lower for word in greetings)

    def _extract_title_from_natural_message(self, message: str) -> str:
        """Extract task title from natural language messages."""
        message_lower = message.lower()
        message_stripped = message.strip()

        # First try standard patterns
        standard_title = self._extract_title_from_message(message)
        if standard_title != "Untitled Task":
            return standard_title

        # Natural language: "next monday i have to go for dinner" -> "Go For Dinner"
        # Remove date/time expressions from the beginning
        cleaned = message_stripped

        # Remove leading date expressions
        date_prefixes = [
            r"^(next\s+\w+\s*,?\s*)",  # "next monday, "
            r"^(coming\s+\w+\s*,?\s*)",  # "coming monday, "
            r"^(this\s+coming\s+\w+\s*,?\s*)",  # "this coming monday, "
            r"^(on\s+\w+\s*,?\s*)",  # "on monday, "
            r"^(tomorrow\s*,?\s*)",  # "tomorrow, "
            r"^(today\s*,?\s*)",  # "today, "
            r"^(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s*,?\s*)",  # "18/02/2026, "
        ]

        import re
        for pattern in date_prefixes:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Remove common starting phrases (EXTENDED LIST for better natural language support)
        starting_phrases = [
            # Standard phrases
            "i have to ", "i need to ", "i want to ", "i should ", "i must ",
            "i have ", "i need ", "i want ", "i am going to ", "i'm going to ",
            "have to ", "need to ", "want to ",
            "going to ", "go to ",
            "don't forget to ", "remember to ", "forgot to ",
            "there is ", "there's ", "we have ",
            # Event/party specific phrases
            "i need to go ", "i have to go ", "i want to go ", "i'm going ", "i am going ",
            "need to go ", "have to go ", "want to go ", "going ",
            "i need to attend ", "i have to attend ", "need to attend ", "have to attend ",
            "i need to join ", "i have to join ", "need to join ", "have to join ",
            # General activity phrases
            "i need to ", "i have to ", "i want to ", "i should ", "i must ",
            "planning to ", "plan to ", "want to ", "need to ",
            # Implicit task phrases
            "got to ", "gotta ", "supposed to ", "have got to ",
            # Roman Urdu update phrases
            "naam badlo ", "name change karo ", "title badlo ", "naam change ",
            "name badlo ", "title change karo ", "kaam ka naam badlo ",
            "kaam badlo ", "kaam change karo ", "kaam edit karo ",
        ]

        cleaned_lower = cleaned.lower()
        for phrase in starting_phrases:
            if cleaned_lower.startswith(phrase):
                cleaned = cleaned[len(phrase):]
                cleaned_lower = cleaned.lower()
                break

        # Remove trailing metadata (priority, due date)
        if cleaned:
            cleaned = self._remove_metadata_from_title(cleaned.strip())

        # Title case if we have something meaningful
        if cleaned and len(cleaned.strip()) > 2:
            return cleaned.strip().title()

        # Fallback: try to extract the main action/event
        # Look for event/activity nouns that indicate a task
        event_nouns = [
            "party", "meeting", "dinner", "lunch", "breakfast", "event",
            "concert", "show", "movie", "game", "match", "tournament",
            "conference", "seminar", "workshop", "class", "lecture",
            "appointment", "interview", "presentation", "demo",
            "trip", "vacation", "journey", "flight", "train", "bus",
            "doctor", "dentist", "hospital", "clinic",
            "shopping", "groceries", "errands", "chores",
            "birthday", "wedding", "funeral", "ceremony", "celebration",
            "deadline", "submission", "exam", "test", "quiz",
            "call", "email", "message", "report", "presentation",
        ]

        # Check if any event noun is in the message
        for noun in event_nouns:
            if f" {noun} " in f" {message_lower} " or message_lower.endswith(f" {noun}"):
                # Found an event noun - use it as the base for the title
                # Try to get surrounding context
                idx = message_lower.find(f" {noun}")
                if idx == -1:
                    idx = message_lower.rfind(f" {noun}")

                # Get words before the noun (up to 5 words)
                before = message_stripped[:idx].strip().split()
                context_words = before[-3:] if len(before) > 3 else before

                # Build title from context + noun
                title_parts = [w.strip('.,!?;:\'"') for w in context_words if len(w) > 2]
                title_parts.append(noun.title())

                if title_parts:
                    title = ' '.join(title_parts).strip()
                    title = self._remove_metadata_from_title(title)
                    if title and len(title.strip()) > 2:
                        return title.strip().title()

        # Fallback: try to extract the main action
        # Find specific action verbs (not generic "have", "be", etc.)
        specific_actions = [
            "go", "buy", "make", "finish", "complete", "attend", "meet",
            "eat", "take", "call", "send", "write", "read", "study", "work",
            "play", "run", "walk", "drive", "cook", "clean", "shop", "visit",
            "watch", "listen", "learn", "teach", "help", "prepare", "organize",
            "plan", "schedule", "book", "reserve", "order", "pay", "submit",
            "upload", "download", "install", "fix", "build", "create", "design",
            "test", "review", "check", "verify", "confirm", "update", "delete",
            "add", "edit", "save", "print", "scan", "copy", "move", "backup",
            "restore", "attend", "join", "participate", "present", "speak",
        ]

        # Find the first specific action word in the message
        for action in specific_actions:
            idx = message_stripped.lower().find(f" {action} ")
            if idx == -1:
                idx = message_stripped.lower().find(f" {action}")
            if idx != -1:
                # Check word boundary
                end_idx = idx + len(action) + 1
                if end_idx >= len(message_stripped) or not message_stripped[end_idx].isalpha():
                    title = message_stripped[idx:].strip()
                    title = self._remove_metadata_from_title(title)
                    if title and len(title.strip()) > 2:
                        return title.strip().title()

        # Last resort: extract meaningful words from the message
        # Skip common stop words and metadata
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after", "above",
            "below", "between", "under", "again", "further", "then", "once", "here",
            "there", "when", "where", "why", "how", "all", "each", "few", "more",
            "most", "other", "some", "such", "no", "nor", "not", "only", "own",
            "same", "so", "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "about", "against", "this", "that", "these",
            "those", "am", "it", "its", "i", "my", "me", "task", "mark", "complete",
            "incomplete", "unmark", "reopen", "delete", "update", "edit",
            "need", "want", "have", "going", "go", "come", "came",
            "next", "coming", "this", "that", "these", "those",
            "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
            "today", "tomorrow", "yesterday", "week", "month", "year",
            "priority", "high", "low", "medium", "urgent", "normal",
        }

        words = message_stripped.split()
        meaningful_words = []
        for word in words:
            clean_word = word.strip('.,!?;:\'"').lower()
            if clean_word and clean_word not in stop_words and len(clean_word) > 2:
                # Check if it's not a date pattern
                if not re.match(r'^\d+[/\-]\d+[/\-]\d+$', clean_word):
                    meaningful_words.append(word.strip('.,!?;:\'"'))

        if meaningful_words:
            title = ' '.join(meaningful_words[:5])  # Limit to 5 words
            title = self._remove_metadata_from_title(title)
            if title and len(title.strip()) > 2:
                return title.strip().title()

        return "Untitled Task"

    def _is_priority_update(self, message: str) -> bool:
        """Check if message is a priority update request."""
        message_lower = message.lower()

        # Must be a SHORT follow-up message (< 8 words)
        # This prevents "show all tasks with priority low" from being treated as update
        word_count = len(message.split())
        if word_count > 8:
            return False

        # Must NOT contain list/show/view keywords
        list_keywords = ["show", "list", "view", "get", "see", "display", "all", "my", "the"]
        if any(keyword in message_lower for keyword in list_keywords):
            return False

        # Check for explicit action words
        priority_patterns = ["keep", "make", "set", "change", "update", "modify", "adjust"]
        has_priority = any(word in message_lower for word in ["priority", "urgent", "important"])
        has_action = any(word in message_lower for word in priority_patterns)
        has_priority_value = any(word in message_lower for word in ["low", "high", "medium", "normal"])
        
        # Check for implicit action patterns like "set its priority to", "make it", "change it to"
        has_implicit_action = any(pattern in message_lower for pattern in [
            "set its priority", "set the priority", "make it", "make the priority",
            "change it to", "change the priority", "update it to", "update the priority"
        ])

        # Also detect direct priority updates like "priority high", "high priority", "make it urgent"
        # without requiring an explicit action word, but ONLY for very short messages
        is_direct_priority = has_priority_value and has_priority and word_count <= 5
        
        # Detect "its priority" or "the priority" references (clear follow-up indicator)
        has_pronoun_reference = "its priority" in message_lower or "the priority" in message_lower or "the task" in message_lower
        
        # Detect "change/set/update priority to X" pattern
        has_priority_to_pattern = "priority to" in message_lower and has_priority_value

        return (has_action and has_priority and has_priority_value) or is_direct_priority or (has_implicit_action and has_priority_value) or has_pronoun_reference or has_priority_to_pattern

    def _is_combined_priority_date_update(self, message: str) -> bool:
        """Check if message is a combined priority + date update (e.g., 'priority high, tomorrow')."""
        message_lower = message.lower()
        
        # This should only match SHORT follow-up messages, not full sentences
        # If the message has more than 6 words, it's likely a new task creation
        word_count = len(message.split())
        if word_count > 6:
            return False
        
        # Check for priority value
        has_priority_value = any(word in message_lower for word in ["low", "high", "medium", "normal"])
        has_priority_keyword = "priority" in message_lower
        
        # Check for date reference
        has_date = self._extract_due_date(message) is not None
        
        # Combined update if we have both priority and date, and it's not a question/greeting
        # Also require that it looks like a follow-up (has priority keyword or is very short)
        is_followup_style = has_priority_keyword or word_count <= 4
        is_combined = has_priority_value and has_date and not self._is_question(message) and not self._is_greeting(message) and is_followup_style
        
        return is_combined

    def _is_due_date_update(self, message: str) -> bool:
        """Check if message is a due date update request."""
        message_lower = message.lower()
        # Be more specific with due patterns - require word boundaries
        due_patterns = [" due ", "due ", " due", "deadline", " by ", " until "]
        has_due = any(word in message_lower for word in due_patterns)
        has_date = self._extract_due_date(message) is not None

        # Only treat as update if it's a short follow-up message (< 6 words)
        # or has explicit "due" keyword
        # This prevents full sentences like "I have to... till today" from being treated as updates
        word_count = len(message.split())
        is_short_followup = word_count <= 6

        return has_due and has_date and is_short_followup

    def _get_context_task_id(self, message: str) -> Optional[int]:
        """Get task ID from context - either explicit in message or last mentioned."""
        # First try to extract explicit task ID from message
        explicit_id = self._extract_task_id(message)
        if explicit_id:
            return explicit_id
        
        # Fall back to last mentioned task ID
        if self._last_task_id:
            return self._last_task_id
        
        # Try to get the most recent task from database
        try:
            from models.task import TaskDB as Task
            latest_task = self.session.query(Task).filter(
                Task.user_id == self.user_id
            ).order_by(Task.created_at.desc()).first()

            if latest_task:
                return latest_task.id
        except Exception:
            pass

        return None
    
    def _extract_title_from_message(self, message: str) -> str:
        """Extract task title from common patterns."""
        message_lower = message.lower()
        message_stripped = message.strip()

        # Pattern 1: "create task <title>" or "add task <title>" or "new task <title>"
        for pattern in ["create task ", "add task ", "new task ", "create a task ", "add a task "]:
            if pattern in message_lower:
                idx = message_lower.find(pattern)
                start_idx = idx + len(pattern)
                title = message_stripped[start_idx:].strip()
                # Remove priority/due date mentions
                title = self._remove_metadata_from_title(title)
                if title:
                    return title.strip('"\'').title()

        # Pattern 2: "task: <title>" or "task to <title>"
        for pattern in ["task: ", "task to "]:
            if pattern in message_lower:
                idx = message_lower.find(pattern)
                start_idx = idx + len(pattern)
                title = message_stripped[start_idx:].strip()
                title = self._remove_metadata_from_title(title)
                if title:
                    return title.strip('"\'').title()

        # Pattern 3: "I need to <title>" or "I want to <title>" or "remind me to <title>"
        for pattern in ["i need to ", "i want to ", "remind me to "]:
            if pattern in message_lower:
                idx = message_lower.find(pattern)
                start_idx = idx + len(pattern)
                title = message_stripped[start_idx:].strip()
                title = self._remove_metadata_from_title(title)
                if title:
                    return title.strip('"\'').title()

        return "Untitled Task"

    def _remove_metadata_from_title(self, title: str) -> str:
        """Remove priority, due date, and other metadata from title."""
        title_lower = title.lower()

        # Remove common metadata patterns (priority and due date related only)
        metadata_patterns = [
            (" with low priority", ""),
            (" with high priority", ""),
            (" with medium priority", ""),
            (" with priority", ""),
            (" due tomorrow", ""),
            (" due next ", ""),
            (" due on ", ""),
            (" due ", ""),
            (" by tomorrow", ""),
            (" by next ", ""),
            (" by ", ""),
            (" for tomorrow", ""),
            (" for next ", ""),
            (" and low priority", ""),
            (" and high priority", ""),
            (" and medium priority", ""),
            (" and tomorrow", ""),
            (" and next ", ""),
            (" on coming ", ""),
            (" on next ", ""),
            # Remove ordinal weekday of month patterns
            (" on first monday of ", ""),
            (" on first tuesday of ", ""),
            (" on first wednesday of ", ""),
            (" on first thursday of ", ""),
            (" on first friday of ", ""),
            (" on first saturday of ", ""),
            (" on first sunday of ", ""),
            (" on second monday of ", ""),
            (" on second tuesday of ", ""),
            (" on second wednesday of ", ""),
            (" on second thursday of ", ""),
            (" on second friday of ", ""),
            (" on second saturday of ", ""),
            (" on second sunday of ", ""),
            (" on third monday of ", ""),
            (" on third tuesday of ", ""),
            (" on third wednesday of ", ""),
            (" on third thursday of ", ""),
            (" on third friday of ", ""),
            (" on third saturday of ", ""),
            (" on third sunday of ", ""),
            (" on fourth monday of ", ""),
            (" on fourth tuesday of ", ""),
            (" on fourth wednesday of ", ""),
            (" on fourth thursday of ", ""),
            (" on fourth friday of ", ""),
            (" on fourth saturday of ", ""),
            (" on fourth sunday of ", ""),
            (" on last monday of ", ""),
            (" on last tuesday of ", ""),
            (" on last wednesday of ", ""),
            (" on last thursday of ", ""),
            (" on last friday of ", ""),
            (" on last saturday of ", ""),
            (" on last sunday of ", ""),
        ]

        for pattern, replacement in metadata_patterns:
            if pattern in title_lower:
                idx = title_lower.find(pattern)
                title = title[:idx].strip()
                title_lower = title.lower()

        # Also handle "with" followed by anything
        if " with " in title_lower:
            idx = title_lower.find(" with ")
            title = title[:idx].strip()
            title_lower = title.lower()

        # Handle "and" followed by anything (like "and tomorrow")
        if " and " in title_lower:
            idx = title_lower.find(" and ")
            title = title[:idx].strip()
            title_lower = title.lower()

        # NEW: Remove trailing date/time expressions using regex
        import re
        
        # Remove "on <weekday>" patterns (e.g., "on Monday", "on Friday")
        title = re.sub(r'\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "on <date>" patterns (e.g., "on 23/02/2026", "on Feb 23")
        title = re.sub(r'\s+on\s+\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+on\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+on\s+\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', '', title, flags=re.IGNORECASE)
        
        # Remove "next <weekday>" patterns
        title = re.sub(r'\s+next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "coming <weekday>" patterns
        title = re.sub(r'\s+coming\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "this coming <weekday>" patterns
        title = re.sub(r'\s+this\s+coming\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "tomorrow", "today", "tonight"
        title = re.sub(r'\s+(tomorrow|today|tonight)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "at <time>" patterns (e.g., "at 6 pm", "at 9:30 am")
        title = re.sub(r'\s+at\s+\d{1,2}(:\d{2})?\s*(am|pm)\b', '', title, flags=re.IGNORECASE)
        
        # Remove standalone time expressions (e.g., "6 pm", "9:30 am")
        title = re.sub(r'\b\d{1,2}(:\d{2})?\s*(am|pm)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "in <number> days/weeks" patterns
        title = re.sub(r'\s+in\s+\d+\s+(days?|weeks?|months?)\b', '', title, flags=re.IGNORECASE)
        
        # Remove "by <weekday/date>" patterns
        title = re.sub(r'\s+by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+by\s+\d{1,2}[/-]\d{1,2}[/-]\d{4}\b', '', title, flags=re.IGNORECASE)
        
        # Remove priority keywords at the end
        title = re.sub(r'\s+(high|low|medium|urgent|normal)\s*(priority)?\b', '', title, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        title = re.sub(r'\s{2,}', ' ', title).strip()
        
        # Remove trailing "at", "to", "in", "on" that might be left
        title = re.sub(r'\s+(at|to|in|on)\s*$', '', title, flags=re.IGNORECASE)

        return title

    def _extract_description(self, message: str) -> Optional[str]:
        for keyword in ["description:", "desc:", "details:", "note:"]:
            if keyword in message.lower():
                idx = message.lower().find(keyword)
                desc = message[idx + len(keyword):].strip()
                return desc if desc else None
        return None

    def _extract_priority(self, message: str) -> str:
        """Extract priority from message."""
        message_lower = message.lower()

        # Check for explicit priority patterns
        if "high priority" in message_lower or "urgent" in message_lower or "priority high" in message_lower or "important" in message_lower:
            return "high"
        elif "low priority" in message_lower or "priority low" in message_lower or "whenever" in message_lower or "casual" in message_lower or "no rush" in message_lower or "anytime" in message_lower:
            return "low"
        elif "medium priority" in message_lower or "normal priority" in message_lower or "priority medium" in message_lower:
            return "medium"

        # Fallback to single word detection
        if "high" in message_lower or "urgent" in message_lower or "important" in message_lower:
            return "high"
        elif "low" in message_lower or "whenever" in message_lower or "casual" in message_lower:
            return "low"
        return "medium"

    def _find_nth_weekday_of_month(self, year: int, month: int, weekday: int, n: int) -> Optional[datetime]:
        """
        Find the nth occurrence of a weekday in a given month.
        weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
        n: 1=first, 2=second, 3=third, 4=fourth, 5=fifth, -1=last
        """
        import calendar
        
        # Get the number of days in the month
        _, num_days = calendar.monthrange(year, month)
        
        if n == -1:  # Last occurrence
            # Start from the end of the month and work backwards
            for day in range(num_days, 0, -1):
                try:
                    date = datetime(year, month, day)
                    if date.weekday() == weekday:
                        return date
                except ValueError:
                    continue
            return None
        else:  # First, second, third, fourth, fifth
            count = 0
            for day in range(1, num_days + 1):
                try:
                    date = datetime(year, month, day)
                    if date.weekday() == weekday:
                        count += 1
                        if count == n:
                            return date
                except ValueError:
                    continue
            return None

    def _extract_due_date(self, message: str) -> Optional[str]:
        """
        Extract due date from message and convert to YYYY-MM-DD format.
        Handles relative dates like 'tomorrow', 'next Sunday', 'in 2 days', etc.
        """
        message_lower = message.lower()
        today = datetime.now().date()

        # Pattern: "tomorrow"
        if "tomorrow" in message_lower:
            due_date = today + timedelta(days=1)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "today"
        if "today" in message_lower:
            return today.strftime("%Y-%m-%d")

        # Pattern: "yesterday" (probably a mistake, but handle it)
        if "yesterday" in message_lower:
            due_date = today - timedelta(days=1)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "<ordinal> <weekday> of <month>" (e.g., "first monday of march", "second tuesday of april")
        months = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        ordinals = {
            "first": 1, "1st": 1,
            "second": 2, "2nd": 2,
            "third": 3, "3rd": 3,
            "fourth": 4, "4th": 4,
            "fifth": 5, "5th": 5,
            "last": -1  # Special case for last occurrence
        }
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
            "friday": 4, "saturday": 5, "sunday": 6
        }
        
        # Check for ordinal + weekday + of + month pattern
        for month_name, month_num in months.items():
            if month_name in message_lower:
                for ordinal_name, ordinal_num in ordinals.items():
                    for day_name, weekday_num in weekdays.items():
                        pattern = f"{ordinal_name} {day_name} of {month_name}"
                        if pattern in message_lower:
                            # Calculate the date for the nth weekday of the specified month
                            year = today.year
                            # If the month has already passed this year, use next year
                            if month_num < today.month or (month_num == today.month and today.day > 1):
                                year += 1
                            
                            # Find the nth occurrence of weekday in that month
                            due_date = self._find_nth_weekday_of_month(year, month_num, weekday_num, ordinal_num)
                            if due_date:
                                return due_date.strftime("%Y-%m-%d")

        # Pattern: "coming <weekday>" (e.g., "coming sunday", "coming monday")
        for day_name, weekday_num in weekdays.items():
            if f"coming {day_name}" in message_lower:
                days_ahead = weekday_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                due_date = today + timedelta(days=days_ahead)
                return due_date.strftime("%Y-%m-%d")
            
            # Also handle "this coming <weekday>"
            if f"this coming {day_name}" in message_lower:
                days_ahead = weekday_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                due_date = today + timedelta(days=days_ahead)
                return due_date.strftime("%Y-%m-%d")

        # Pattern: "next <weekday>" (e.g., "next Sunday", "next Monday")
        for day_name, weekday_num in weekdays.items():
            if f"next {day_name}" in message_lower:
                # Calculate days until next occurrence of this weekday
                days_ahead = weekday_num - today.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                due_date = today + timedelta(days=days_ahead)
                return due_date.strftime("%Y-%m-%d")

            # Also handle "on <weekday>" (e.g., "on Friday", "on Monday")
            if f"on {day_name}" in message_lower:
                days_ahead = weekday_num - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                due_date = today + timedelta(days=days_ahead)
                return due_date.strftime("%Y-%m-%d")

        # Pattern: "in X days" (e.g., "in 2 days", "in 5 days")
        days_match = re.search(r"in\s+(\d+)\s+days?", message_lower)
        if days_match:
            days = int(days_match.group(1))
            due_date = today + timedelta(days=days)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "in X weeks" (e.g., "in 2 weeks")
        weeks_match = re.search(r"in\s+(\d+)\s+weeks?", message_lower)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            due_date = today + timedelta(weeks=weeks)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "next week"
        if "next week" in message_lower:
            due_date = today + timedelta(weeks=1)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "in X months" (e.g., "in 2 months")
        months_match = re.search(r"in\s+(\d+)\s+months?", message_lower)
        if months_match:
            months = int(months_match.group(1))
            # Calculate month addition carefully
            month = today.month + months
            year = today.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            day = min(today.day, calendar.monthrange(year, month)[1])
            due_date = today.replace(year=year, month=month, day=day)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "next month"
        if "next month" in message_lower:
            month = today.month + 1
            year = today.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            day = min(today.day, calendar.monthrange(year, month)[1])
            due_date = today.replace(year=year, month=month, day=day)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: "in X days" variations like "after X days"
        days_match = re.search(r"after\s+(\d+)\s+days?", message_lower)
        if days_match:
            days = int(days_match.group(1))
            due_date = today + timedelta(days=days)
            return due_date.strftime("%Y-%m-%d")

        # Pattern: explicit date in various formats
        # YYYY-MM-DD
        date_match = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', message)
        if date_match:
            try:
                due_date = datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3))).date()
                return due_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # DD/MM/YYYY or DD-MM-YYYY
        date_match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', message)
        if date_match:
            try:
                due_date = datetime(int(date_match.group(3)), int(date_match.group(2)), int(date_match.group(1))).date()
                return due_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # MM/DD/YYYY (US format) - less common but handle it
        date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', message)
        if date_match:
            try:
                due_date = datetime(int(date_match.group(3)), int(date_match.group(1)), int(date_match.group(2))).date()
                return due_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        # Pattern: "DD MMM" or "MMM DD" (e.g., "23 feb", "feb 23", "23rd feb")
        months_short = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
        }
        months_long = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12
        }
        
        # Try "DD MMM" pattern (e.g., "23 feb", "5 march")
        for month_name, month_num in {**months_short, **months_long}.items():
            day_month_pattern = rf'(\d{{1,2}})(?:st|nd|rd|th)?\s+{month_name}'
            day_month_match = re.search(day_month_pattern, message_lower)
            if day_month_match:
                try:
                    day = int(day_month_match.group(1))
                    year = today.year
                    # If this date has already passed this year, use next year
                    try:
                        test_date = datetime(year, month_num, day).date()
                        if test_date < today:
                            year += 1
                    except ValueError:
                        year += 1
                    due_date = datetime(year, month_num, day).date()
                    return due_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            
            # Try "MMM DD" pattern (e.g., "feb 23", "march 5")
            month_day_pattern = rf'{month_name}\s+(\d{{1,2}})(?:st|nd|rd|th)?'
            month_day_match = re.search(month_day_pattern, message_lower)
            if month_day_match:
                try:
                    day = int(month_day_match.group(1))
                    year = today.year
                    # If this date has already passed this year, use next year
                    try:
                        test_date = datetime(year, month_num, day).date()
                        if test_date < today:
                            year += 1
                    except ValueError:
                        year += 1
                    due_date = datetime(year, month_num, day).date()
                    return due_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # Pattern: "on DD/MM" or "on MM/DD" (assume current year)
        on_date_match = re.search(r'on\s+(\d{1,2})[/-](\d{1,2})', message_lower)
        if on_date_match:
            try:
                day = int(on_date_match.group(1))
                month = int(on_date_match.group(2))
                year = today.year
                due_date = datetime(year, month, day).date()
                # If already passed, assume next year
                if due_date < today:
                    due_date = datetime(year + 1, month, day).date()
                return due_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None

    def _extract_task_id(self, message: str) -> Optional[int]:
        patterns = [r"task\s*(\d+)", r"id[:\s]*(\d+)", r"#(\d+)"]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return int(match.group(1))
        numbers = re.findall(r"\d+", message)
        return int(numbers[0]) if numbers else None

    def _extract_task_by_title(self, message: str) -> Optional[int]:
        """Extract task ID by searching for task title in quotes or by title match."""
        try:
            from models.task import TaskDB as Task
            
            # Try to extract title from quotes (e.g., "Assignment")
            import re
            quoted_title = re.search(r'"([^"]+)"', message)
            if quoted_title:
                title = quoted_title.group(1)
                # Search for task with this title for the user
                task = self.session.query(Task).filter(
                    Task.user_id == self.user_id,
                    Task.title.ilike(f"%{title}%")
                ).order_by(Task.created_at.desc()).first()
                if task:
                    return task.id
            
            # Try to find task by title words (without quotes)
            # Skip common words
            skip_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being", 
                         "have", "has", "had", "do", "does", "did", "will", "would", "could", 
                         "should", "may", "might", "must", "shall", "can", "need", "dare", 
                         "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by", 
                         "from", "as", "into", "through", "during", "before", "after", "above", 
                         "below", "between", "under", "again", "further", "then", "once", "here", 
                         "there", "when", "where", "why", "how", "all", "each", "few", "more", 
                         "most", "other", "some", "such", "no", "nor", "not", "only", "own", 
                         "same", "so", "than", "too", "very", "just", "and", "but", "if", "or", 
                         "because", "until", "while", "about", "against", "this", "that", "these", 
                         "those", "am", "it", "its", "i", "my", "me", "task", "mark", "complete", 
                         "incomplete", "unmark", "reopen", "delete", "update", "edit"}
            
            # Look for capitalized words that might be task titles
            words = message.split()
            for word in words:
                clean_word = word.strip('"\'.,!?;:').strip()
                if clean_word and clean_word.lower() not in skip_words and clean_word[0].isupper():
                    task = self.session.query(Task).filter(
                        Task.user_id == self.user_id,
                        Task.title.ilike(f"%{clean_word}%")
                    ).order_by(Task.created_at.desc()).first()
                    if task:
                        return task.id
        except Exception as e:
            logger.error(f"Error extracting task by title: {e}")
        return None

    def _extract_time(self, message: str) -> Optional[str]:
        """Extract time from message (e.g., '7:00 am', '3:30 pm', '7 am')."""
        import re
        
        # Pattern: HH:MM AM/PM or H:MM AM/PM or H AM/PM
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:am|pm))',  # 7:00 am, 3:30 pm
            r'(\d{1,2}\s*(?:am|pm))',  # 7 am, 3 pm
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).upper()
        
        return None

    async def _handle_add_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # Convert due_date string to datetime if provided
        due_date = None
        if params.get("due_date"):
            try:
                due_date = datetime.strptime(params["due_date"], "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid due_date format: {params.get('due_date')}")
        
        task_data = TaskCreate(
            title=params.get("title", "Untitled Task"),
            description=params.get("description"),
            completed=False,
            priority=params.get("priority", "medium"),
            due_date=due_date
        )
        result = await add_task_tool(self.user_id, task_data, self.session)
        result_dict = result.model_dump()
        
        # Store the created task ID for context-aware follow-ups
        self._last_task_id = result_dict.get("id")
        
        return result_dict

    async def _handle_list_tasks(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        results = await list_tasks_tool(self.user_id, completed=params.get("completed"), limit=50, skip=0, session=self.session)
        return [r.model_dump() for r in results]

    async def _handle_complete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params.get("task_id"):
            raise ValueError("Task ID is required")
        completed = params.get("completed", True)
        result = await complete_task_tool(self.user_id, params["task_id"], completed=completed, session=self.session)
        return result.model_dump()

    async def _handle_delete_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params.get("task_id"):
            raise ValueError("Task ID is required")
        result = await delete_task_tool(self.user_id, params["task_id"], self.session)
        return {"deleted": result, "task_id": params["task_id"]}

    async def _handle_update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params.get("task_id"):
            raise ValueError("Task ID is required")
        
        # Convert due_date string to datetime if provided
        due_date = None
        if params.get("due_date"):
            try:
                due_date = datetime.strptime(params["due_date"], "%Y-%m-%d")
            except ValueError:
                logger.warning(f"Invalid due_date format: {params.get('due_date')}")
        
        # Get the current task to preserve unchanged fields
        from models.task import TaskDB as Task
        current_task = self.session.query(Task).filter(Task.id == params["task_id"], Task.user_id == self.user_id).first()
        if not current_task:
            raise ValueError(f"Task {params['task_id']} not found")
        
        task_update = TaskUpdate(
            title=params.get("title") if params.get("title") is not None else current_task.title,
            description=params.get("description") if params.get("description") is not None else current_task.description,
            priority=params.get("priority") if params.get("priority") is not None else current_task.priority,
            due_date=due_date if due_date is not None else current_task.due_date
        )
        result = await update_task_tool(self.user_id, params["task_id"], task_update, self.session)
        result_dict = result.model_dump()
        
        # Update last_task_id for context
        self._last_task_id = params["task_id"]
        
        return result_dict

    def _format_add_task_response(self, result: Dict[str, Any], params: Dict[str, Any]) -> str:
        return f"✅ Task created successfully!\n\n**{result.get('title', params.get('title', 'Task'))}** (ID: {result.get('id')})\n\nIs there anything else you'd like me to help you with?"

    def _format_list_tasks_response(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return "📋 You don't have any tasks yet. Would you like me to create one for you?"
        response = f"📋 You have {len(results)} task(s):\n\n"
        for i, task in enumerate(results, 1):
            status = "✅" if task.get("completed") else "⏳"
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
            response += f"{i}. {status} {priority_icon} **{task.get('title')}** (ID: {task.get('id')})\n"
            if task.get("description"):
                response += f"   _{task.get('description')}_\n"
        return response

    def _format_complete_task_response(self, result: Dict[str, Any]) -> str:
        completed = result.get('completed', True)
        if completed:
            return f"✅ Great job! Task \"{result.get('title', 'Task')}\" has been marked as completed!"
        else:
            return f"🔓 Task \"{result.get('title', 'Task')}\" has been marked as incomplete!"

    def _format_delete_task_response(self, result: Dict[str, Any]) -> str:
        return f"🗑️ Task {result.get('task_id')} has been deleted successfully."

    def _format_update_task_response(self, result: Dict[str, Any]) -> str:
        response = f"✏️ Task \"{result.get('title', 'Task')}\" has been updated successfully!"
        if result.get('priority'):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(result.get('priority'), "🟡")
            response += f" Priority: {priority_icon} {result.get('priority').title()}"
        if result.get('due_date'):
            # Format due date nicely
            due_date = result.get('due_date')
            if isinstance(due_date, str):
                response += f" Due: {due_date}"
            elif due_date:
                response += f" Due: {due_date.strftime('%Y-%m-%d') if hasattr(due_date, 'strftime') else str(due_date)}"
        # Add helpful follow-up suggestion
        response += "\n\nIs there anything else you'd like me to help you with?"
        return response

    def _handle_general_query(self, message: str) -> str:
        message_lower = message.lower()
        
        # Roman Urdu greetings
        if any(word in message_lower for word in ["assalam o alaikum", "salam", "adaab", "namaste"]):
            return "👋 Walaikum Assalam! Main aap ka AI task assistant hoon. Main aap ko tasks create, view, complete, ya delete karne mein madad kar sakta hoon. Main aap ki kaise madad karoon?"
        
        if any(word in message_lower for word in ["hello", "hi", "hey", "kaise ho", "kya haal hai"]):
            return "👋 Hello! I'm your AI task assistant. I can help you create, view, complete, or delete tasks. What would you like to do?"
        
        # Roman Urdu help
        if any(word in message_lower for word in ["help", "madad", "kya kar sakte ho", "kaise use karein"]):
            return "🤖 Main aap ke tasks manage kar sakta hoon! Try karein:\n- \"Create a task to buy groceries\" ya \"kaam add karo\"\n- \"Show my tasks\" ya \"mere kaam dikhao\"\n- \"Complete task 1\" ya \"kaam complete karo\"\n- \"Delete task 2\" ya \"kaam delete karo\""
        
        if any(word in message_lower for word in ["thank", "thanks", "shukriya"]):
            return "You're welcome! Koi aur cheez jismein main madad kar sakta hoon?"
        
        return f"I received your message: \"{message}\". I can help you manage tasks - try saying \"create a task\" or \"show my tasks\"!"


async def process_chat_message(message: str, user_id: str, conversation_id: int) -> Dict[str, Any]:
    """Process a chat message using the AI agent."""
    agent = ChatbotAgent(user_id, conversation_id)
    return await agent.process_message(message)
