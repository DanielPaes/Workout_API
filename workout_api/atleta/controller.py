from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, Query, status
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from pydantic import UUID4
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from workout_api.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workout_api.atleta.models import AtletaModel
from workout_api.categorias.models import CategoriaModel
from workout_api.centro_treinamento.models import CentroTreinamentoModel
from workout_api.contrib.dependencies import DatabaseDependency

router = APIRouter()

@router.post(
        '/',
        summary='Criar novo atleta',
        status_code=status.HTTP_201_CREATED,
        response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency,
    atleta_in: AtletaIn = Body(...)
):
    
    categoria = (await db_session.execute(select(CategoriaModel).filter_by(nome=atleta_in.categoria.nome))).scalars().first()

    if not categoria:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'A categoria informada não foi encontrada.')

    centro_treinamento = (await db_session.execute(select(CentroTreinamentoModel).filter_by(nome=atleta_in.centro_treinamento.nome))).scalars().first()

    if not centro_treinamento:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'O centro de treinamento não foi encontrado.')


    try:

        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.now(), **atleta_in.model_dump())

        atleta_model = AtletaModel(**atleta_out.model_dump(exclude=['categoria', 'centro_treinamento']))
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_trienamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=f'Já existe um atleta cadastrado com o cpf:{atleta_model.cpf}'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ocorreu um erro ao inserir os dados.'
        )

    return atleta_out


@router.get(
        '/',
        summary='Consultar todos os atletas',
        status_code=status.HTTP_200_OK,
        response_model=Page[AtletaOut],
)
async def query(
    db_session: DatabaseDependency,
    # Query parameters para ser utilizado nos endpoints. Ex: localhost/atletas?nome=Richard
    nome: str = Query(None, description="Nome do atleta para filtrar"),
    idade: int = Query(None, description="Idade do atleta para filtrar")
) -> Page[AtletaOut]:
    
    query = select(AtletaModel)

    if nome:
        query = query.filter(AtletaModel.nome == nome)
    
    if idade:
        query = query.filter(AtletaModel.idade == idade)

    #atletas = (await db_session.execute(query)).scalars().all()

    #atletas = [AtletaOut.model_validate(atleta) for atleta in atletas]

    return await sqlalchemy_paginate(db_session, query)


@router.get(
        '/{id}',
        summary='Consulta um atleta pelo id',
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
)
async def query(id: UUID4,
    db_session: DatabaseDependency,
) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado para o id:{id}')
    
    return atleta


@router.patch(
        '/{id}',
        summary='Editar um atleta pelo id',
        status_code=status.HTTP_200_OK,
        response_model=AtletaOut,
)
async def query(id: UUID4,
    db_session: DatabaseDependency,
    atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado para o id:{id}')
    
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)
    return atleta

@router.delete(
        '/{id}',
        summary='Deletar um atleta pelo id',
        status_code=status.HTTP_204_NO_CONTENT
)
async def query(id: UUID4,
    db_session: DatabaseDependency,
) -> None:
    atleta: AtletaOut = (await db_session.execute(select(AtletaModel).filter_by(id=id))).scalars().first()
    
    if not atleta:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Atleta não encontrado para o id:{id}')
    

    await db_session.delete(atleta)
    await db_session.commit()


add_pagination(router)