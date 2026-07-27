"""Motor determinístico de atendimento do elevador."""

from __future__ import annotations

from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    Direction,
    ElevatorEvent,
    ElevatorSnapshot,
    EventKind,
    Floor,
    Passenger,
    ServicePhase,
)


class Elevator:
    """Executa fases de atendimento e expõe eventos cronológicos."""

    def __init__(self, initial_floor: Floor | None = None) -> None:
        """Cria um elevador ocioso no andar informado ou no térreo."""
        self._current_floor = initial_floor or Floor(GROUND_FLOOR_NUMBER)
        self._direction = Direction.IDLE
        self._cabin: list[Passenger] = []
        self._upward_waiting: list[Passenger] = []
        self._downward_waiting: list[Passenger] = []
        self._phase_direction = Direction.IDLE
        self._elapsed_seconds = 0
        self._phase_active = False

    def start_phase(self, phase: ServicePhase) -> None:
        """Registra as solicitações de uma nova fase ociosa."""
        if self._phase_active:
            raise RuntimeError(
                "Não é possível iniciar uma nova fase: "
                "a fase anterior ainda possui passageiros."
            )

        self._upward_waiting = []
        self._downward_waiting = []
        if phase.direction is Direction.UP:
            self._upward_waiting = list(phase.requests)
        else:
            self._downward_waiting = list(phase.requests)
        self._phase_direction = phase.direction
        self._phase_active = True
        self._direction = Direction.IDLE

    def step(self) -> tuple[ElevatorEvent, ...]:
        """Executa um atendimento local ou avança no máximo um andar."""
        if not self._phase_active:
            return ()

        if self._should_service_current_floor():
            self._prepare_direction_for_local_service()
            return self._service_current_floor()

        self._direction = self._next_travel_direction()
        self._move_one_floor()
        if self._should_service_current_floor():
            return self._service_current_floor()

        return (self._event(EventKind.FLOOR_PASSED),)

    def run_until_idle(self) -> tuple[ElevatorEvent, ...]:
        """Executa passos sucessivos até a fase terminar."""
        events: list[ElevatorEvent] = []
        while self._phase_active:
            events.extend(self.step())
        return tuple(events)

    def snapshot(self) -> ElevatorSnapshot:
        """Retorna uma visão imutável do estado atual."""
        return ElevatorSnapshot(
            current_floor=self._current_floor,
            direction=self._direction,
            cabin=tuple(self._cabin),
            upward_waiting=tuple(self._upward_waiting),
            downward_waiting=tuple(self._downward_waiting),
            elapsed_seconds=self._elapsed_seconds,
            is_idle=not self._phase_active,
        )

    def _has_pending_work(self) -> bool:
        return bool(
            self._cabin or self._upward_waiting or self._downward_waiting
        )

    def _should_service_current_floor(self) -> bool:
        exiting_count = sum(
            passenger.destination == self._current_floor
            for passenger in self._cabin
        )
        if exiting_count:
            return True

        waiting, waiting_direction = self._waiting_at_current_floor()
        if not waiting:
            return False

        remaining_cabin = len(self._cabin) - exiting_count
        has_capacity = remaining_cabin < ELEVATOR_CAPACITY
        direction_matches = waiting_direction is self._direction
        return has_capacity and (not remaining_cabin or direction_matches)

    def _waiting_at_current_floor(
        self,
    ) -> tuple[list[Passenger], Direction | None]:
        waiting = self._active_waiting()
        requests = [
            passenger
            for passenger in waiting
            if passenger.origin == self._current_floor
        ]
        if not requests:
            return [], None
        return requests, self._phase_direction

    def _active_waiting(self) -> list[Passenger]:
        if self._phase_direction is Direction.UP:
            return self._upward_waiting
        return self._downward_waiting

    def _prepare_direction_for_local_service(self) -> None:
        if self._direction is not Direction.IDLE:
            return

        waiting, waiting_direction = self._waiting_at_current_floor()
        if waiting and waiting_direction is not None:
            self._direction = waiting_direction

    def _move_one_floor(self) -> None:
        floor_delta = 1 if self._direction is Direction.UP else -1
        self._current_floor = Floor(self._current_floor.number + floor_delta)
        self._elapsed_seconds += 1

    def _service_current_floor(self) -> tuple[ElevatorEvent, ...]:
        arrival_direction = self._direction
        events = [self._event(EventKind.ARRIVAL)]

        self._elapsed_seconds += 1
        events.append(self._event(EventKind.DOOR_OPENING))

        exited = self._remove_arrived_passengers()
        if exited:
            events.append(self._event(EventKind.PASSENGERS_EXITED, exited))

        entered = self._board_waiting_passengers(arrival_direction)
        if entered:
            events.append(self._event(EventKind.PASSENGERS_ENTERED, entered))

        self._elapsed_seconds += 1
        events.append(self._event(EventKind.DOOR_CLOSING))
        events.extend(self._finish_stop(arrival_direction))
        return tuple(events)

    def _remove_arrived_passengers(self) -> tuple[Passenger, ...]:
        exited = tuple(
            passenger
            for passenger in self._cabin
            if passenger.destination == self._current_floor
        )
        if exited:
            self._cabin = [
                passenger
                for passenger in self._cabin
                if passenger.destination != self._current_floor
            ]
        return exited

    def _board_waiting_passengers(
        self,
        arrival_direction: Direction,
    ) -> tuple[Passenger, ...]:
        waiting_here, waiting_direction = self._waiting_at_current_floor()
        if not waiting_here or waiting_direction is None:
            return ()
        if self._cabin and waiting_direction is not arrival_direction:
            return ()

        available_places = ELEVATOR_CAPACITY - len(self._cabin)
        entered = tuple(waiting_here[:available_places])
        self._cabin.extend(entered)
        active_waiting = self._active_waiting()
        for passenger in entered:
            active_waiting.remove(passenger)
        return entered

    def _finish_stop(
        self,
        arrival_direction: Direction,
    ) -> tuple[ElevatorEvent, ...]:
        if not self._has_pending_work():
            self._phase_active = False
            self._direction = Direction.IDLE
            return (self._event(EventKind.IDLE),)

        next_direction = self._next_travel_direction()
        self._direction = next_direction
        if (
            arrival_direction is not Direction.IDLE
            and next_direction is not arrival_direction
        ):
            return (self._event(EventKind.DIRECTION_CHANGED),)
        return ()

    def _next_travel_direction(self) -> Direction:
        if self._cabin:
            return self._direction_toward_cabin_destination()
        return self._direction_toward_nearest_call()

    def _direction_toward_cabin_destination(self) -> Direction:
        current_number = self._current_floor.number
        destinations = tuple(
            passenger.destination.number for passenger in self._cabin
        )
        if any(number > current_number for number in destinations):
            return Direction.UP
        return Direction.DOWN

    def _direction_toward_nearest_call(self) -> Direction:
        current_number = self._current_floor.number
        waiting = self._active_waiting()
        _, nearest_request = min(
            enumerate(waiting),
            key=lambda item: (
                abs(item[1].origin.number - current_number),
                item[0],
            ),
        )
        if nearest_request.origin.number > current_number:
            return Direction.UP
        return Direction.DOWN

    def _event(
        self,
        kind: EventKind,
        passengers: tuple[Passenger, ...] = (),
    ) -> ElevatorEvent:
        return ElevatorEvent(
            elapsed_seconds=self._elapsed_seconds,
            floor=self._current_floor,
            direction=self._direction,
            kind=kind,
            passengers=passengers,
        )
