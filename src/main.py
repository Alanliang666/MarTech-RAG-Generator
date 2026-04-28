"""
Main entry point for running the application.
"""
from fastapi import FastAPI
from src.api import router

app = FastAPI(title='MarTech RAG Generator')

app.include_router(router, prefix='/api/v1')

@app.get('/')
async def root():
    """
    Health check endpoint returning a welcome message.
    """
    return {'message':'Welcome to MarTech RAG API!'}
