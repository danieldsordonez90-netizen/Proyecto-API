# Archivo: Models/Libros.py

from pydantic import BaseModel, Field
from typing import Optional, List


class Libro(BaseModel):
    # Mapeado a: [ISBN]
    ISBN: Optional[str] = Field(
        default=None,
        description="ISBN único del libro. Es la Clave Primaria.",
        max_length=20, 
        examples=["978-84-1362-179-1"]
    )

    # Mapeado a: [Titulo]
    Titulo: Optional[str] = Field(
        default=None,
        description="Título completo del libro",
        examples=["Nuestra señora de París"]
    )

    # Mapeado a: [Año_publicacion]
    Año_publicacion: Optional[int] = Field(
        default=None, 
        description="Año en que el libro fue publicado",
        ge=1400,
        le=2025
    )
    