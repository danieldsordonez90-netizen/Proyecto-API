
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class Multa(BaseModel):
    # Mapeado a: [Id_multa]
    Id_multa: Optional[int] = Field(
        default=None, 
        description="ID único de la multa (Auto-incremental)"
    )

    # Mapeado a: [Id_prestamo]
    Id_prestamo: int = Field(
        description="ID del préstamo que generó la multa"
    )

    # Mapeado a: [Monto]
    Monto: float = Field( 
        description="Monto de la multa",
        gt=0
    )

    # Mapeado a: [Fecha_multa]
    Fecha_multa: Optional[date] = Field(
        default=None,
        description="Fecha en que se registró la multa (Auto-generada si es Nula)"
    )

    # Mapeado a: [Nombre_estudiante]
    Nombre_estudiante: Optional[str] = Field(
            default=None,
            description="Nombre del estudiante (traído con JOIN)"
        )

    # Mapeado a: [Titulo] 
    Titulo: Optional[str] = Field(
        default=None,
        description="Título del libro (traído con JOIN)"
    )
