from fastapi import APIRouter, Depends

from app.db import Database
from app.dependencies import get_database
from app.security.auth import AuthenticatedUser, get_current_user


router = APIRouter(
    prefix="/api/records",
    tags=["Records"]
)


@router.get("/")
def listar_records(
    user: AuthenticatedUser = Depends(get_current_user),
    db: Database = Depends(get_database)
):
    with db.transaction() as cursor:

        cursor.execute("""
            SELECT id, titulo, url_alvo, data_hora_inicio,
                   data_hora_fim, detalhes_resumo, status
            FROM records
            WHERE user_id = %s
            ORDER BY data_hora_inicio DESC
        """, (user.id,))

        registros = cursor.fetchall()

    return list(registros)
