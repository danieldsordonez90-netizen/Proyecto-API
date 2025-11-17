from pydantic import BaseModel, Field
from typing import Optional

# Modelo Pydantic para representar un autor.
class Autor(BaseModel):
    # ID único del autor.
    Id_autor: Optional[int] = Field(
        default=None, 
        description="ID único del autor (Auto-incremental)"
    )

    # Nombre del autor.
    Nombre_autor: str = Field(
        description="Nombre completo del autor",
        pattern=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
        examples=["Gabriel García Márquez"]
    )

    # Año de nacimiento del autor.
    Año_nacimiento: Optional[int] = Field(
        default=None,
        description="Año de nacimiento del autor",
        ge=0, 
        le=2025 
    )
    