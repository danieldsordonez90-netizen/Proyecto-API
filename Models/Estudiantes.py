# Archivo: Models/Estudiantes.py

from pydantic import BaseModel, Field
from typing import Optional

class Estudiante(BaseModel):
    id_matricula_estudiante: Optional[int] = Field(
        default=None, 
        description="ID único de matrícula para el estudiante (Auto-incremental)"
    )

    Nombre_estudiante: Optional[str] = Field(
        default=None,
        description="Nombre completo del estudiante",
        pattern=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["Juan Perez", "Maria Martinez"]
    )

    Correo_estudiante: Optional[str] = Field(
        default=None,
        description="Correo electrónico del estudiante",
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        examples=["usuario@example.com"]
    )

    Edad: Optional[int] = Field(
        default=None,
        description="Edad del estudiante",
        ge=14,
        examples=[18]
    )
    
    Esta_Activo: Optional[bool] = Field(
        default=None,
        description="Indica si el estudiante está activo (Borrado Lógico)"
    )