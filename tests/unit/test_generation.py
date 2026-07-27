"""Testes da geração de rodadas do elevador."""

from faker import Faker

from elevator_vibe_code.generation import (
    FakerPassengerGenerator,
    RoundGenerator,
)
from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    TOP_FLOOR_NUMBER,
    Direction,
    ServiceRound,
)


def _seeded_faker(seed: int) -> Faker:
    faker_instance = Faker("pt_BR")
    faker_instance.seed_instance(seed)
    return faker_instance


def test_faker_generator_satisfies_round_generator_protocol() -> None:
    generator: RoundGenerator = FakerPassengerGenerator(_seeded_faker(100))

    assert isinstance(generator.generate_round(), ServiceRound)


def test_seeded_generators_produce_the_same_round() -> None:
    first_generator = FakerPassengerGenerator(_seeded_faker(321))
    second_generator = FakerPassengerGenerator(_seeded_faker(321))

    assert (
        first_generator.generate_round() == second_generator.generate_round()
    )


def test_default_generator_produces_a_valid_round() -> None:
    service_round = FakerPassengerGenerator().generate_round()

    assert isinstance(service_round, ServiceRound)


def test_generated_rounds_follow_call_and_passenger_contracts() -> None:
    for seed in range(25):
        service_round = FakerPassengerGenerator(
            _seeded_faker(seed)
        ).generate_round()
        upward_call = service_round.upward_call
        downward_call = service_round.downward_call

        assert upward_call.floor.number == GROUND_FLOOR_NUMBER
        assert upward_call.direction is Direction.UP
        assert 1 <= len(upward_call.passengers) <= ELEVATOR_CAPACITY
        assert isinstance(upward_call.passengers, tuple)
        for passenger in upward_call.passengers:
            assert passenger.passenger_id.strip()
            assert passenger.name.strip()
            assert passenger.origin == upward_call.floor
            assert GROUND_FLOOR_NUMBER < passenger.destination.number
            assert passenger.destination.number <= TOP_FLOOR_NUMBER
            assert passenger.direction is Direction.UP

        assert GROUND_FLOOR_NUMBER < downward_call.floor.number
        assert downward_call.floor.number <= TOP_FLOOR_NUMBER
        assert downward_call.direction is Direction.DOWN
        assert 1 <= len(downward_call.passengers) <= ELEVATOR_CAPACITY
        assert isinstance(downward_call.passengers, tuple)
        for passenger in downward_call.passengers:
            assert passenger.passenger_id.strip()
            assert passenger.name.strip()
            assert passenger.origin == downward_call.floor
            assert passenger.destination.number == GROUND_FLOOR_NUMBER
            assert passenger.direction is Direction.DOWN


def test_call_sizes_are_drawn_separately() -> None:
    call_sizes = tuple(
        (
            len(service_round.upward_call.passengers),
            len(service_round.downward_call.passengers),
        )
        for seed in range(20)
        for service_round in (
            FakerPassengerGenerator(_seeded_faker(seed)).generate_round(),
        )
    )

    assert len({upward_size for upward_size, _ in call_sizes}) > 1
    assert len({downward_size for _, downward_size in call_sizes}) > 1
    assert any(
        upward_size != downward_size
        for upward_size, downward_size in call_sizes
    )
