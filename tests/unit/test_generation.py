"""Testes da geração das fases do elevador."""

from faker import Faker

from elevator_vibe_code.generation import (
    FakerPassengerGenerator,
    PhaseGenerator,
)
from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    TOP_FLOOR_NUMBER,
    Direction,
    ServicePhase,
)


def _seeded_faker(seed: int) -> Faker:
    faker_instance = Faker("pt_BR")
    faker_instance.seed_instance(seed)
    return faker_instance


def test_faker_generator_satisfies_phase_generator_protocol() -> None:
    generator: PhaseGenerator = FakerPassengerGenerator(_seeded_faker(100))

    assert isinstance(generator.generate_upward_phase(), ServicePhase)
    assert isinstance(generator.generate_downward_phase(), ServicePhase)


def test_seeded_generators_produce_the_same_phases() -> None:
    first_generator = FakerPassengerGenerator(_seeded_faker(321))
    second_generator = FakerPassengerGenerator(_seeded_faker(321))

    assert (
        first_generator.generate_upward_phase()
        == second_generator.generate_upward_phase()
    )
    assert (
        first_generator.generate_downward_phase()
        == second_generator.generate_downward_phase()
    )


def test_default_generator_produces_valid_phases() -> None:
    generator = FakerPassengerGenerator()

    assert isinstance(generator.generate_upward_phase(), ServicePhase)
    assert isinstance(generator.generate_downward_phase(), ServicePhase)


def test_generated_phases_follow_individual_request_contracts() -> None:
    downward_origin_sets: list[set[int]] = []
    upward_destination_sets: list[set[int]] = []

    for seed in range(25):
        generator = FakerPassengerGenerator(_seeded_faker(seed))
        upward_phase = generator.generate_upward_phase()
        downward_phase = generator.generate_downward_phase()

        assert upward_phase.direction is Direction.UP
        assert 1 <= len(upward_phase.requests) <= ELEVATOR_CAPACITY
        assert isinstance(upward_phase.requests, tuple)
        for passenger in upward_phase.requests:
            assert passenger.passenger_id.strip()
            assert passenger.name.strip()
            assert passenger.origin.number == GROUND_FLOOR_NUMBER
            assert GROUND_FLOOR_NUMBER < passenger.destination.number
            assert passenger.destination.number <= TOP_FLOOR_NUMBER
            assert passenger.direction is Direction.UP
        upward_destination_sets.append({
            passenger.destination.number for passenger in upward_phase.requests
        })

        assert downward_phase.direction is Direction.DOWN
        assert 1 <= len(downward_phase.requests) <= ELEVATOR_CAPACITY
        assert isinstance(downward_phase.requests, tuple)
        for passenger in downward_phase.requests:
            assert passenger.passenger_id.strip()
            assert passenger.name.strip()
            assert GROUND_FLOOR_NUMBER < passenger.origin.number
            assert passenger.origin.number <= TOP_FLOOR_NUMBER
            assert passenger.destination.number == GROUND_FLOOR_NUMBER
            assert passenger.direction is Direction.DOWN
        downward_origin_sets.append({
            passenger.origin.number for passenger in downward_phase.requests
        })

    assert any(
        len(destinations) > 1 for destinations in upward_destination_sets
    )
    assert any(len(origins) > 1 for origins in downward_origin_sets)


def test_phase_sizes_are_drawn_separately() -> None:
    phase_sizes = tuple(
        (
            len(generator.generate_upward_phase().requests),
            len(generator.generate_downward_phase().requests),
        )
        for seed in range(20)
        for generator in (FakerPassengerGenerator(_seeded_faker(seed)),)
    )

    assert len({upward_size for upward_size, _ in phase_sizes}) > 1
    assert len({downward_size for _, downward_size in phase_sizes}) > 1
    assert any(
        upward_size != downward_size
        for upward_size, downward_size in phase_sizes
    )
