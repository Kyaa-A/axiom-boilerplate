"""
AI endpoints demonstrating RAG and AI capabilities.
Frontend calls these endpoints - NEVER calls AI services directly.
"""
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from app.schemas.document import QueryRequest, QueryResponse
from app.services.ai.chains.base_chain import rag_chain
from app.services.ai.llm.cerebras_client import cerebras_client

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/query", response_model=QueryResponse)
async def query_documents(query_data: QueryRequest):
    """
    Query documents using RAG (Retrieval-Augmented Generation).

    Workflow:
    1. Convert query to embedding (Voyage AI)
    2. Search similar vectors (Qdrant)
    3. Generate response with context (Cerebras LLM)

    This is the ONLY way frontend should access AI capabilities.
    """
    try:
        result = await rag_chain.run(
            query=query_data.query,
            top_k=query_data.top_k,
            score_threshold=query_data.score_threshold,
        )

        return QueryResponse(
            query=result["query"],
            response=result["response"],
            sources=result["sources"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        )


@router.post("/generate")
async def generate_text(
    prompt: str,
    system_prompt: str = None,
    max_tokens: int = None,
):
    """
    Generate text using LLM without RAG.

    Use this for tasks that don't require document retrieval.
    """
    try:
        response = await cerebras_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )

        return {"response": response}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}",
        )


@router.post("/generate/stream")
async def generate_text_stream(
    prompt: str,
    system_prompt: str = None,
    max_tokens: int = None,
):
    """
    Stream text generation using LLM.

    Returns a streaming response for real-time generation.
    """
    try:
        async def stream_generator():
            async for chunk in cerebras_client.stream_generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
            ):
                yield chunk

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Streaming generation failed: {str(e)}",
        )
