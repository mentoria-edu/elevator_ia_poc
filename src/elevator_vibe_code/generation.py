"""Geração de rodadas aleatórias para o elevador."""

from typing import Protocol

from faker import Faker

from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    TOP_FLOOR_NUMBER,
    Direction,
    ElevatorCall,
    Floor,
    Passenger,
    ServiceRound,
)


class RoundGenerator(Protocol):
    """Contrato para fontes de rodadas de serviço."""

    def generate_round(self) -> ServiceRound:
        """Gera a próxima rodada de serviço."""
        ...


class FakerPassengerGenerator:
    """Gera passageiros e chamadas aleatórias com Faker."""

    def __init__(self, faker_instance: Faker | None = None) -> None:
        self._faker = (
            faker_instance if faker_instance is not None else Faker("pt_BR")
        )

    def generate_round(self) -> ServiceRound:
        """Gera uma chamada de subida e uma chamada de descida."""
        ground_floor = Floor(GROUND_FLOOR_NUMBER)
        upward_count = self._passenger_count()
        downward_count = self._passenger_count()
        downward_floor = self._upper_floor()

        upward_passengers = tuple(
            self._upward_passenger(ground_floor) for _ in range(upward_count)
        )
        downward_passengers = tuple(
            self._downward_passenger(downward_floor, ground_floor)
            for _ in range(downward_count)
        )
        return ServiceRound(
            upward_call=ElevatorCall(
                floor=ground_floor,
                direction=Direction.UP,
                passengers=upward_passengers,
            ),
            downward_call=ElevatorCall(
                floor=downward_floor,
                direction=Direction.DOWN,
                passengers=downward_passengers,
            ),
        )

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
