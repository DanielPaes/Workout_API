from typing import Annotated

from pydantic import Field
from workout_api.contrib.schemas import BaseSchema


class CentroTreinamento(BaseSchema):
    nome: Annotated[str, Field(description='Nome da centro de treinamento', example='CT King', max_length=20)]
    endereco: Annotated[str, Field(description='Enderecço do CT de trienamento', example='Rua X, n. 2', max_length=60)]
    proprietario: Annotated[str, Field(description='Proprietario do CT de trienamento', example='Marcos', max_length=30)]