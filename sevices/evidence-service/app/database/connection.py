import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def conectar():
    """Estabelece uma conexão com o PostgreSQL"""
    conexao = psycopg2.connect(DATABASE_URL)
    return conexao 

