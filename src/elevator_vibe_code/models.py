"""Modelos imutáveis do domínio do elevador."""

from dataclasses import dataclass
from enum import Enum

GROUND_FLOOR_NUMBER: int = 0
TOP_FLOOR_NUMBER: int = 17
ELEVATOR_CAPACITY: int = 6


@dataclass(frozen=True, slots=True, order=True)
class Floor:
    """Andar existente no prédio."""

    number: int

    def __post_init__(self) -> None:
        """Rejeita valores que não representam um andar existente."""
        if isinstance(self.number, bool) or not isinstance(self.number, int):
            raise ValueError(
                f"Número de andar inválido: {self.number!r}. "
                f"Esperado um inteiro entre {GROUND_FLOOR_NUMBER} e "
                f"{TOP_FLOOR_NUMBER}."
            )
        if not GROUND_FLOOR_NUMBER <= self.number <= TOP_FLOOR_NUMBER:
            raise ValueError(
                f"Número de andar inválido: {self.number}. "
                f"Esperado um inteiro entre {GROUND_FLOOR_NUMBER} e "
                f"{TOP_FLOOR_NUMBER}."
            )


class Direction(Enum):
    """Direção operacional do elevador ou de uma viagem."""

    UP = "SUBINDO"
    DOWN = "DESCENDO"
    IDLE = "PARADO"


@dataclass(frozen=True, slots=True)
class Passenger:
    """Pessoa que viaja entre o térreo e um andar superior."""

    passenger_id: str
    name: str
    origin: Floor
    destination: Floor
    direction: Direction

    def __post_init__(self) -> None:
        """Garante que origem, destino e direção formem uma viagem válida."""
        upward_trip = (
            self.origin.number == GROUND_FLOOR_NUMBER
            and self.destination.number > GROUND_FLOOR_NUMBER
            and self.direction is Direction.UP
        )
        downward_trip = (
            self.origin.number > GROUND_FLOOR_NUMBER
            and self.destination.number == GROUND_FLOOR_NUMBER
            and self.direction is Direction.DOWN
        )
        if not upward_trip and not downward_trip:
            raise ValueError(
                "Viagem inválida: "
                f"origem={self.origin.number}, "
                f"destino={self.destination.number}, "
                f"direção={self.direction.value}. "
                "Esperada viagem do térreo para um andar superior em "
                "SUBINDO ou de um andar superior para o térreo em DESCENDO."
            )


@dataclass(frozen=True, slots=True)
class ElevatorCall:
    """Chamada com passageiros em uma fila FIFO."""

    floor: Floor
    direction: Direction
    passengers: tuple[Passenger, ...]

    def __post_init__(self) -> None:
        """Valida capacidade, origem e direção dos passageiros."""
        passenger_count = len(self.passengers)
        if not 1 <= passenger_count <= ELEVATOR_CAPACITY:
            raise ValueError(
                f"Quantidade de passageiros inválida: {passenger_count}. "
                f"Esperado um valor entre 1 e {ELEVATOR_CAPACITY}."
            )
        for passenger in self.passengers:
            if passenger.origin != self.floor:
                raise ValueError(
                    "Origem do passageiro incompatível com a chamada: "
                    f"passageiro={passenger.passenger_id!r}, "
                    f"origem={passenger.origin.number}, "
                    f"andar da chamada={self.floor.number}."
                )
            if passenger.direction is not self.direction:
                raise ValueError(
                    "Direção do passageiro incompatível com a chamada: "
                    f"passageiro={passenger.passenger_id!r}, "
                    f"direção={passenger.direction.value}, "
                    f"direção da chamada={self.direction.value}."
                )


@dataclass(frozen=True, slots=True)
class ServiceRound:
    """Rodada com uma chamada de subida e uma chamada de descida."""

    upward_call: ElevatorCall
    downward_call: ElevatorCall

    def __post_init__(self) -> None:
        """Garante a ordem e a semântica das duas chamadas."""
        if (
            self.upward_call.floor.number != GROUND_FLOOR_NUMBER
            or self.upward_call.direction is not Direction.UP
        ):
            raise ValueError(
                "Chamada de subida inválida: "
                f"andar={self.upward_call.floor.number}, "
                f"direção={self.upward_call.direction.value}. "
                "Esperada chamada SUBINDO no térreo."
            )
        if (
            self.downward_call.floor.number == GROUND_FLOOR_NUMBER
            or self.downward_call.direction is not Direction.DOWN
        ):
            raise ValueError(
                "Chamada de descida inválida: "
                f"andar={self.downward_call.floor.number}, "
                f"direção={self.downward_call.direction.value}. "
                "Esperada chamada DESCENDO em um andar superior."
            )


class EventKind(Enum):
    """Tipos de evento produzidos pelo futuro motor do elevador."""

    FLOOR_PASSED = "floor_passed"
    ARRIVAL = "arrival"
    DOOR_OPENING = "door_opening"
    PASSENGERS_EXITED = "passengers_exited"
    PASSENGERS_ENTERED = "passengers_entered"
    DOOR_CLOSING = "door_closing"
    DIRECTION_CHANGED = "direction_changed"
    IDLE = "idle"


@dataclass(frozen=True, slots=True)
class ElevatorEvent:
    """Evento imutável ocorrido durante uma rodada."""

    elapsed_seconds: int
    floor: Floor
    direction: Direction
    kind: EventKind
    passengers: tuple[Passenger, ...] = ()

    def __post_init__(self) -> None:
        """Restringe passageiros aos eventos de entrada e saída."""
        passenger_event_kinds = (
            EventKind.PASSENGERS_EXITED,
            EventKind.PASSENGERS_ENTERED,
        )
        if self.passengers and self.kind not in passenger_event_kinds:
            raise ValueError(
                "Passageiros incompatíveis com o evento: "
                f"tipo={self.kind.value}, "
                f"quantidade={len(self.passengers)}. "
                "Esperado passengers vazio fora de entrada ou saída."
            )


@dataclass(frozen=True, slots=True)
class ElevatorSnapshot:
    """Visão imutável do estado observável do elevador."""

    current_floor: Floor
    direction: Direction
    cabin: tuple[Passenger, ...]
    upward_waiting: tuple[Passenger, ...]
    downward_waiting: tuple[Passenger, ...]
    elapsed_seconds: int
    is_idle: bool
