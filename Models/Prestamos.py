
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Prestamo(BaseModel):
    # Mapeado a: [Id_prestamo]
    Id_prestamo: Optional[int] = Field(
        default=None, 
        description="ID único del préstamo (Auto-incremental)"
    )

    # Mapeado a: [Id_matricula_estudiante]
    Id_matricula_estudiante: int = Field(
        description="ID del estudiante que realiza el préstamo"
    )

    # Mapeado a: [ISBN]
    ISBN: str = Field(
        description="ISBN del libro que se presta",
        max_length=20
    )

    # Mapeado a: [Fecha_prestamo]
    Fecha_prestamo: Optional[date] = Field(
        default=None,
        description="Fecha en que se realiza el préstamo (Auto-generada)"
    )

    # Mapeado a: [Fecha_devolucion]
    Fecha_devolucion: Optional[date] = Field(
        default=None,
        description="Fecha en que se devuelve el libro (NULL si está activo)"
    )

    # Mapeado a: [Nombre_estudiante] (JOIN)
    Nombre_estudiante: Optional[str] = Field(
        default=None,
        description="Nombre del estudiante (traído con JOIN)"
    )
    
    # Mapeado a: [Titulo]
    Titulo: Optional[str] = Field(
        default=None,
        description="Título del libro (traído con JOIN)"
    )