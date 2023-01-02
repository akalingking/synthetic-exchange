import logging

from synthetic_exchange.agent import Agent
from synthetic_exchange.order_generator import OrderGenerator
from synthetic_exchange.strategy import RandomNormal, RandomUniform


def order_event(order):
    print(f"order_event order: {order}")


def main():
    generator = OrderGenerator()

    agent1 = Agent(RandomUniform(minPrice=100, maxPrice=130, tickSize=1, minQuantity=200, maxQuantity=300))
    agent1.strategy.order_event.subscribe(order_event)
    agent2 = Agent(RandomNormal(initialPrice=100, minQuantity=100, maxQuantity=200))
    agent2.strategy.order_event.subscribe(order_event)

    generator.add_agent([agent1, agent2])

    generator.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
