import logging

from synthetic_exchange.agent import Agent
from synthetic_exchange.market import Market
from synthetic_exchange.strategy import RandomNormal, RandomUniform


def on_order_event(order):
    print(f"on_order_event order: {order}")


def main():
    market = Market(
        "SQNC-RSCH",
        minPrice=100,
        maxPrice=110,
        tickSize=1,
        minQuantity=10,
        maxQuantity=1000,
    )

    agent1 = Agent(
        RandomUniform(
            minPrice=market.min_price,
            maxPrice=market.max_price,
            tickSize=market.tick_size,
            minQuantity=market.min_quantity,
            maxQuantity=market.max_quantity,
        )
    )
    agent2 = Agent(RandomNormal(initialPrice=100, minQuantity=100, maxQuantity=200))

    market.add_agents(
        [
            agent1,
            agent2,
            # agent3,
            # agent4
        ]
    )

    market.run()

    # market.summary()
    market.showOrderbook()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
