"""Geração de fases aleatórias para o elevador."""

from typing import Protocol

from faker import Faker

from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    TOP_FLOOR_NUMBER,
    Direction,
    Floor,
    Passenger,
    ServicePhase,
)


class PhaseGenerator(Protocol):
    """Contrato para fontes das fases de uma rodada."""

    def generate_upward_phase(self) -> ServicePhase:
        """Gera solicitações individuais para a fase de subida."""
        ...

    def generate_downward_phase(self) -> ServicePhase:
        """Gera solicitações individuais para a fase de descida."""
        ...


class FakerPassengerGenerator:
    """Gera fases e passageiros aleatórios com Faker."""

    def __init__(self, faker_instance: Faker | None = None) -> None:
        self._faker = (
            faker_instance if faker_instance is not None else Faker("pt_BR")
        )

    def generate_upward_phase(self) -> ServicePhase:
        """Gera solicitações com origem no térreo e destinos individuais."""
        ground_floor = Floor(GROUND_FLOOR_NUMBER)
        requests = tuple(
            self._upward_passenger(ground_floor)
            for _ in range(self._passenger_count())
        )
        return ServicePhase(direction=Direction.UP, requests=requests)

    def generate_downward_phase(self) -> ServicePhase:
        """Gera solicitações com origens individuais e destino no térreo."""
        ground_floor = Floor(GROUND_FLOOR_NUMBER)
        requests = tuple(
            self._downward_passenger(self._upper_floor(), ground_floor)
            for _ in range(self._passenger_count())
        )
        return ServicePhase(direction=Direction.DOWN, requests=requests)

    def _passenger_count(self) -> int:
        return self._faker.random_int(min=1, max=ELEVATOR_CAPACITY)

    def _upper_floor(self) -> Floor:
        return Floor(
            self._faker.random_int(
                min=GROUND_FLOOR_NUMBER + 1,
                max=TOP_FLOOR_NUMBER,
            )
        )

    def _upward_passenger(self, ground_floor: Floor) -> Passenger:
        return Passenger(
            passenger_id=self._passenger_id(),
            name=self._passenger_name(),
            origin=ground_floor,
            destination=self._upper_floor(),
            direction=Direction.UP,
        )

    def _downward_passenger(
        self,
        origin: Floor,
        ground_floor: Floor,
    ) -> Passenger:
        return Passenger(
            passenger_id=self._passenger_id(),
            name=self._passenger_name(),
            origin=origin,
            destination=ground_floor,
            direction=Direction.DOWN,
        )

    def _passenger_id(self) -> str:
        passenger_id = str(self._faker.uuid4()).strip()
        if not passenger_id:
            raise ValueError(
                "Identificador gerado inválido: esperado texto não vazio."
            )
        return passenger_id

    def _passenger_name(self) -> str:
        passenger_name = self._faker.name().strip()
        if not passenger_name:
            raise ValueError("Nome gerado inválido: esperado texto não vazio.")
        return passenger_name
