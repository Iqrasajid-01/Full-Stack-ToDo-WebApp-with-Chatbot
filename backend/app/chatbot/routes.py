"""
AI Chatbot Routes

Provides endpoints for conversational task management using Cohere LLM.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional, AsyncGenerator
import json
import asyncio

from db.session import get_session
from core.dependencies import get_current_user
from schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationSchema,
    MessageSchema,
    ConversationWithMessages,
    ToolCall
)
from models.conversation import Conversation
from models.message import Message
from app.chatbot.agent import process_chat_message
from app.chatbot.logger import chatbot_logger

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


def serialize_for_json(obj):
    """Serialize objects for JSON storage, handling datetime objects."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, 'model_dump'):
        # Pydantic model
        return serialize_for_json(obj.model_dump())
    elif hasattr(obj, '__dict__'):
        # Regular object
        return serialize_for_json(obj.__dict__)
    return obj


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Send a message to the AI chatbot and get a response.

    The chatbot can help you manage tasks using natural language.
    Try: "Create a task to buy groceries", "Show my pending tasks", etc.
    """
    logger = chatbot_logger

    try:
        # Validate message is not empty
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Get or create conversation
        conversation_id = request.conversation_id
        if conversation_id:
            # Verify conversation belongs to user
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user
            ).first()
            
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Update timestamp
            conversation.updated_at = datetime.utcnow()
            db.add(conversation)
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
        
        # Store user message
        user_message = Message(
            conversation_id=conversation_id,
            user_id=current_user,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        
        # Call AI agent directly
        agent_data = await process_chat_message(
            message=request.message,
            user_id=current_user,
            conversation_id=conversation_id
        )
        
        ai_reply = agent_data.get("reply", "I apologize, but I couldn't process your request.")
        tool_calls_data = agent_data.get("tool_calls", [])

        # Serialize tool_calls for JSON storage (handle datetime objects)
        serialized_tool_calls = serialize_for_json(tool_calls_data) if tool_calls_data else None

        # Store AI response
        assistant_message = Message(
            conversation_id=conversation_id,
            user_id=current_user,
            role="assistant",
            content=ai_reply,
            tool_calls=serialized_tool_calls
        )
        db.add(assistant_message)
        db.commit()
        
        # Parse tool calls for response
        tool_calls = []
        for tc in tool_calls_data:
            tool_calls.append(ToolCall(
                tool=tc.get("tool", ""),
                parameters=tc.get("parameters", {}),
                result=tc.get("result")
            ))
        
        return ChatResponse(
            reply=ai_reply,
            conversation_id=conversation_id,
            tool_calls=tool_calls if tool_calls else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/message/stream")
async def send_message_stream(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Send a message to the AI chatbot and get a streaming response.
    Returns chunks of the response as they are generated for faster perceived response time.
    """
    logger = chatbot_logger
    logger.info(f"Stream request received from user: {current_user}")

    try:
        # Validate message is not empty
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Get or create conversation
        conversation_id = request.conversation_id
        if conversation_id:
            # Verify conversation belongs to user
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user
            ).first()

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Update timestamp
            conversation.updated_at = datetime.utcnow()
            db.add(conversation)
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user,
                title=request.message[:50] + "..." if len(request.message) > 50 else request.message
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            conversation_id = conversation.id
            logger.info(f"Created new conversation: {conversation_id}")

        # Store user message
        user_message = Message(
            conversation_id=conversation_id,
            user_id=current_user,
            role="user",
            content=request.message
        )
        db.add(user_message)
        db.commit()
        logger.info(f"Stored user message in conversation: {conversation_id}")

        # Create async generator for streaming
        async def generate_stream() -> AsyncGenerator[str, None]:
            try:
                logger.info(f"Processing message for conversation: {conversation_id}")
                
                # Call AI agent
                agent_data = await process_chat_message(
                    message=request.message,
                    user_id=current_user,
                    conversation_id=conversation_id
                )

                ai_reply = agent_data.get("reply", "I apologize, but I couldn't process your request.")
                tool_calls_data = agent_data.get("tool_calls", [])

                logger.info(f"AI reply generated, length: {len(ai_reply)}")

                # Serialize tool_calls for JSON storage
                serialized_tool_calls = serialize_for_json(tool_calls_data) if tool_calls_data else None

                # Store AI response
                assistant_message = Message(
                    conversation_id=conversation_id,
                    user_id=current_user,
                    role="assistant",
                    content=ai_reply,
                    tool_calls=serialized_tool_calls
                )
                db.add(assistant_message)
                db.commit()
                logger.info(f"Stored AI response in database")

                # Stream the response word by word for faster perception
                words = ai_reply.split()
                logger.info(f"Streaming {len(words)} words")
                
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    yield f"data: {json.dumps({'chunk': chunk, 'done': False})}\n\n"
                    await asyncio.sleep(0.005)  # 5ms delay for near-instant streaming

                # Send tool calls if any (serialize datetime objects)
                if tool_calls_data:
                    serialized_tool_calls = []
                    for tc in tool_calls_data:
                        serialized_tool_calls.append({
                            "tool": tc.get("tool", ""),
                            "parameters": serialize_for_json(tc.get("parameters", {})),
                            "result": serialize_for_json(tc.get("result"))
                        })
                    yield f"data: {json.dumps({'tool_calls': serialized_tool_calls, 'done': False})}\n\n"

                # Send completion signal
                yield f"data: {json.dumps({'done': True, 'conversation_id': conversation_id})}\n\n"
                logger.info(f"Stream completed for conversation: {conversation_id}")

            except Exception as e:
                logger.error(f"Error in stream generation: {str(e)}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # Disable nginx buffering if applicable
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send_message_stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations", response_model=List[ConversationSchema])
async def get_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get all conversations for the current user."""
    try:
        conversations = db.query(Conversation).filter(
            Conversation.user_id == current_user
        ).order_by(
            Conversation.updated_at.desc()
        ).offset(offset).limit(limit).all()
        
        # Get message counts
        result = []
        for conv in conversations:
            msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            
            result.append(ConversationSchema(
                id=conv.id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=msg_count
            ))
        
        return result
        
    except Exception as e:
        chatbot_logger.error(f"Error getting conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}", response_model=ConversationWithMessages)
async def get_conversation(
    conversation_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Get a specific conversation with its messages."""
    try:
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Get messages
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).all()
        
        return ConversationWithMessages(
            conversation=ConversationSchema(
                id=conversation.id,
                title=conversation.title,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                message_count=len(messages)
            ),
            messages=[
                MessageSchema(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    user_id=msg.user_id,
                    role=msg.role,
                    content=msg.content,
                    created_at=msg.created_at,
                    tool_calls=msg.tool_calls
                )
                for msg in messages
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        chatbot_logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete a conversation and all its messages."""
    try:
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete messages first
        messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
        
        for msg in messages:
            db.delete(msg)
        
        # Delete conversation
        db.delete(conversation)
        db.commit()
        
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        chatbot_logger.error(f"Error deleting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
